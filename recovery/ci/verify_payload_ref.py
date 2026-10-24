"""Verify the exact public payload ref and its production-source equivalence."""
import json
from pathlib import Path
import re
import subprocess


def verify(root):
  payload = json.loads((root / 'recovery/installer/payload-ref.json').read_text())
  assert payload['repository'] == 'https://github.com/benbernard/benPilot.git'
  assert payload['branch'] == 'benPilot-release'
  assert re.fullmatch('[0-9a-f]{40}', payload['commit'])
  assert payload['originating_commit'] == 'b47add65d32e232b939d4915cca0b5a9ddafc48d'
  assert (payload['required_model'], payload['required_agnos']) == ('tici', '11.13')
  def git(*args):
    return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=root, text=True).strip()
  remote = git('ls-remote', '--exit-code', payload['repository'], 'refs/heads/' + payload['branch'])
  if subprocess.run(['git', 'cat-file', '-e', payload['commit'] + '^{commit}'], cwd=root, capture_output=True).returncode:
    git('fetch', '--no-tags', '--depth=1', payload['repository'], payload['commit'])
  current = remote.split()[0]
  if current != payload['commit']:
    git('fetch', '--no-tags', payload['repository'], current, payload['commit'])
    subprocess.run(['git', 'merge-base', '--is-ancestor', current, payload['commit']], cwd=root, check=True)
  assert git('rev-parse', payload['commit'] + '^{tree}') == payload['tree']
  changed = git('diff', '--name-only', payload['commit'], 'HEAD').splitlines()
  permitted = {'README.md', 'selfdrive/ui/SConscript', 'selfdrive/ui/installer/installer.cc'}
  unexpected = [p for p in changed if p not in permitted and not p.startswith(('recovery/', '.github/workflows/'))]
  assert not unexpected, f'Pinned payload differs from the reviewed production application: {unexpected}'
  assert payload['version'] in git('show', payload['commit'] + ':common/version.h')
  assert 'QObject::tr("benPilot")' in git('show', payload['commit'] + ':selfdrive/ui/qt/util.cc')
  assert 'jvePilot by John Van Etten' in git('show', payload['commit'] + ':selfdrive/ui/qt/offroad/software_settings.cc')
  assert not git('ls-tree', '--name-only', payload['commit'], '--', 'prebuilt', 'selfdrive/ui/ui'), 'Do not ship a stale prebuilt UI'
  print('PASS: public benPilot-release ref, exact payload SHA/tree, branded app/version/credit and unchanged production application verified. No prebuilt deployment claimed.')
