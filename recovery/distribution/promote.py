#!/usr/bin/env python3
"""Publish a CI-built installer and prepare a reviewed hosting change."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
REPO = 'benbernard/benPilot'


def command(*args: str) -> str:
  return subprocess.check_output(list(args), cwd=ROOT, text=True).strip()


def record(value: object) -> dict[str, object]:
  if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
    raise ValueError('Expected a JSON object')
  return value


def read(path: Path) -> dict[str, object]:
  value: object = json.loads(path.read_text())
  return record(value)


def field(data: dict[str, object], name: str) -> str:
  value = data[name]
  if not isinstance(value, str) or not value:
    raise ValueError('Expected text: ' + name)
  return value


def validate_ci(data: dict[str, object], source: str) -> None:
  if data.get('headSha') != source or data.get('status') != 'completed' or data.get('conclusion') != 'success':
    raise ValueError('CI must have completed successfully on the exact source commit')
  jobs = data.get('jobs')
  if not isinstance(jobs, list):
    raise ValueError('CI jobs are unavailable')
  checked = {field(record(job), 'name') for job in jobs
             if record(job).get('conclusion') == 'success'}
  if not {'Recovery source and updater checks', 'Compile comma-three installer and UI on ARM64'} <= checked:
    raise ValueError('Required source, installer and UI checks are missing')
  if any(record(job).get('conclusion') != 'success' for job in jobs):
    raise ValueError('Every CI job must pass')


def verify_bytes(path: Path, spec: dict[str, object]) -> None:
  data = path.read_bytes()
  if len(data) != spec['size_bytes'] or hashlib.sha256(data).hexdigest() != spec['sha256']:
    raise ValueError('CI installer differs from the reviewed artifact manifest')


def hosting(directory: Path, manifest: dict[str, object]) -> None:
  directory.mkdir(parents=True, exist_ok=True)
  url = field(manifest, 'download_url')
  directory.joinpath('release.json').write_text(json.dumps(manifest, indent=2) + '\n')
  directory.joinpath('nginx.conf').write_text('''server {
    listen 8080;
    server_name benpilot.crabanddog.com;
    server_tokens off;
    add_header Cache-Control "no-store" always;
    add_header X-Content-Type-Options nosniff always;
    location = / { return 302 DOWNLOAD; }
    location = /release { return 302 DOWNLOAD; }
    location = /about { return 302 https://benbernard.github.io/benPilot/; }
    location = /manifest.json { default_type application/json; alias /usr/share/nginx/html/release.json; }
    location = /healthz { access_log off; return 200 'ok\\n'; }
    location / { return 404; }
}
'''.replace('DOWNLOAD', url))


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--ci-run', required=True)
  parser.add_argument('--hosting-dir', type=Path, required=True)
  parser.add_argument('--publish', action='store_true', help='Publish after all checks; default only prepares the plan')
  args = parser.parse_args()
  source = command('git', 'rev-parse', 'HEAD')
  if command('git', 'status', '--porcelain'):
    raise ValueError('Commit or remove source changes before promotion')
  spec = read(ROOT / 'recovery/installer/universal/release.json')
  payload = read(ROOT / 'recovery/installer/universal/payload-ref.json')
  if payload.get('required_models') != ['tici', 'tizi'] or payload.get('required_agnos') != '11.13':
    raise ValueError('Review changed hardware/OS requirements before promotion')
  tag = field(spec, 'tag')
  if not re.fullmatch(r'benpilot-[a-z0-9-]+', tag):
    raise ValueError('Invalid release tag')
  ci: object = json.loads(command('gh','run','view',args.ci_run,'--repo',REPO,'--json','headSha,status,conclusion,jobs'))
  validate_ci(record(ci), source)
  remote = command('git','ls-remote','--exit-code',field(payload,'repository'),'refs/heads/'+field(payload,'branch')).split()[0]
  target = field(payload, 'commit')
  if remote != target:
    command('git','fetch','--no-tags',field(payload,'repository'),remote,target)
    subprocess.run(['git','merge-base','--is-ancestor',remote,target],cwd=ROOT,check=True)
  manifest = dict(spec, payload=payload, source_commit=source,
                  ci_run='https://github.com/'+REPO+'/actions/runs/'+args.ci_run,
                  download_url='https://github.com/'+REPO+'/releases/download/'+tag+'/install-benpilot',
                  full_driving_build_prebuilt=False, device_runtime_tested=False)
  with tempfile.TemporaryDirectory(prefix='benpilot-promotion-') as temporary:
    scratch = Path(temporary)
    command('gh','run','download',args.ci_run,'--repo',REPO,'--dir',str(scratch/'ci'))
    binaries = list(scratch.joinpath('ci').rglob('install-benpilot'))
    if len(binaries) != 1:
      raise ValueError('Expected exactly one CI universal installer')
    verify_bytes(binaries[0], spec)
    command('python3','recovery/installer/verify_artifact.py',str(binaries[0]),'--payload-ref','recovery/installer/universal/payload-ref.json')
    bundle = scratch / 'release'
    bundle.mkdir()
    shutil.copyfile(binaries[0],bundle/'install-benpilot')
    for origin, name in [('recovery/installer/universal/payload-ref.json','payload-ref.json'),
                         ('recovery/installer/recovery-installer.patch','base-installer.patch'),
                         ('recovery/installer/universal/target.patch','target.patch'),('LICENSE','LICENSE.txt')]:
      shutil.copyfile(ROOT/origin,bundle/name)
    bundle.joinpath('release.json').write_text(json.dumps(manifest,indent=2)+'\n')
    bundle.joinpath('SHA256SUMS').write_text(''.join(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n' for path in sorted(bundle.iterdir())))
    if args.publish:
      existing = subprocess.run(['gh','release','view',tag,'--repo',REPO],cwd=ROOT,capture_output=True)
      if existing.returncode == 0:
        raise ValueError('Release already exists; inspect it instead of replacing immutable assets')
      notes = scratch/'notes.md'
      notes.write_text('# Universal comma three / 3X source installer\n\nEnter `benpilot.crabanddog.com` at Custom Software setup. Requires AGNOS 11.13 and no existing installation. Both models use the pinned `benPilot-release` payload. Initial checkout stays pinned as the update branch advances.\n\nCI: '+str(manifest['ci_run'])+'\n\nThe installer is built and verified; full native model generation and physical device validation remain pending. Existing single-model release assets are preserved. Ben reviewed and accepted the inherited safety findings.\n')
      command('gh','release','create',tag,'--repo',REPO,'--draft','--prerelease','--target',source,'--title','benPilot universal comma three / 3X installer','--notes-file',str(notes),*(str(path) for path in sorted(bundle.iterdir())))
      command('gh','release','download',tag,'--repo',REPO,'--pattern','install-benpilot','--dir',str(scratch/'verify'))
      verify_bytes(scratch/'verify/install-benpilot',spec)
      if remote != target:
        # Normal fast-forward push only. A concurrent branch change is rejected.
        command('git','push',field(payload,'repository'),target+':refs/heads/'+field(payload,'branch'))
      command('gh','release','edit',tag,'--repo',REPO,'--draft=false','--prerelease','--latest=false')
      with urllib.request.urlopen(field(manifest,'download_url'),timeout=30) as response:
        actual = response.read(370001)
      if hashlib.sha256(actual).hexdigest() != spec['sha256']:
        raise ValueError('Anonymous published download differs')
    hosting(args.hosting_dir, manifest)
    print(json.dumps(dict(manifest,published=args.publish),indent=2))
    print('Hosting files prepared. Deploy them through the homelab PR and release pipelines.')


if __name__ == '__main__':
  main()
