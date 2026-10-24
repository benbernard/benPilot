"""Fail if recovery CI includes unreviewed changes to the original driving payload."""
import os
from pathlib import Path
import subprocess
import sys

BASELINE = 'b47add65d32e232b939d4915cca0b5a9ddafc48d'
ROOT = Path(__file__).resolve().parents[2]
INSTALLER_PATHS = ('selfdrive/ui/SConscript', 'selfdrive/ui/installer/installer.cc')
sys.path.insert(0, str(ROOT / 'recovery/branding'))
from verify_branding import BRANDING_PATHS, verify as verify_branding


def git(*args):
  return subprocess.check_output(['git', *args], cwd=ROOT, text=True)


def normalize_patch(text):
  # Abbreviated index IDs depend on the available Git object set, not content.
  return '\n'.join(line for line in text.splitlines() if not line.startswith('index '))


changed = git('diff', '--name-only', BASELINE, 'HEAD').splitlines()
has_installer = (ROOT / 'recovery/installer/check_installer_guards.py').is_file()
unexpected = [p for p in changed if p != 'README.md'
              and not p.startswith(('recovery/', '.github/workflows/'))
              and not (has_installer and p in INSTALLER_PATHS)
              and p not in BRANDING_PATHS]
assert not unexpected, f'Changes outside the reviewed recovery/installer scope: {unexpected}'
readme = (ROOT / 'README.md').read_text()
assert readme.startswith('# benPilot') and 'jvePilot' in readme and 'John Van Etten' in readme
assert 'https://github.com/j-vanetten/openpilot' in readme
assert git('show', f'{BASELINE}:launch_env.sh').find('11.13') >= 0
verify_branding(ROOT)
from verify_payload_ref import verify as verify_payload_ref
verify_payload_ref(ROOT)

if has_installer:
  actual = git('diff', '--binary', BASELINE, 'HEAD', '--', *INSTALLER_PATHS)
  recorded = (ROOT / 'recovery/installer/recovery-installer.patch').read_text()
  assert normalize_patch(actual) == normalize_patch(recorded), 'Recorded installer patch differs from checked-out installer source'
  source = (ROOT / INSTALLER_PATHS[1]).read_text()
  assert 'Based on jvePilot by John Van Etten' in source
  subprocess.run([sys.executable, str(ROOT / 'recovery/installer/check_comma3x.py')], check=True)

for path in (ROOT / 'recovery').rglob('*.py'):
  compile(path.read_bytes(), str(path), 'exec')
for path in (ROOT / 'recovery').rglob('*.sh'):
  subprocess.run(['bash', '-n', str(path)], check=True)

if output := os.environ.get('GITHUB_OUTPUT'):
  with open(output, 'a') as stream:
    stream.write(f'has_installer={str(has_installer).lower()}\n')
    stream.write('has_branding=true\n')
print(f'PASS: {len(changed)} reviewed recovery/installer/branding paths; original control logic, safety, models, firmware, OS requirements and licenses unchanged.')
