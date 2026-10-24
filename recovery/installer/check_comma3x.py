"""Check the 3X-only installer delta without running an installer or device code."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RECIPE = ROOT / 'recovery/installer'
INSTALLER = Path('selfdrive/ui/installer/installer.cc')


def main() -> None:
  original = (ROOT / INSTALLER).read_text()
  expected = original.replace('Hardware::get_name() != "tici"', 'Hardware::get_name() != "tizi"')
  expected = expected.replace('Requires comma three with AGNOS', 'Requires comma 3X with AGNOS')
  assert expected != original
  payload = json.loads((RECIPE / 'payload-ref.json').read_text())
  payload['required_model'] = 'tizi'
  assert json.loads((RECIPE / 'comma3x/payload-ref.json').read_text()) == payload, '3X must retain the exact existing application payload'
  hardware = (ROOT / 'system/hardware/tici/hardware.h').read_text()
  assert '{"tizi", cereal::InitData::DeviceType::TIZI}' in hardware
  assert 'AGNOS_VERSION="11.13"' in (ROOT / 'launch_env.sh').read_text()
  with tempfile.TemporaryDirectory(prefix='benpilot-3x-guards-') as directory:
    scratch = Path(directory)
    for name in (INSTALLER, Path('selfdrive/ui/SConscript')):
      destination = scratch / name
      destination.parent.mkdir(parents=True, exist_ok=True)
      shutil.copyfile(ROOT / name, destination)
    subprocess.run(['git', 'apply', '--check', str(RECIPE / 'comma3x/target.patch')], cwd=scratch, check=True)
    subprocess.run(['git', 'apply', str(RECIPE / 'comma3x/target.patch')], cwd=scratch, check=True)
    assert (scratch / INSTALLER).read_text() == expected, '3X patch changed more than hardware selection and its message'
    reference = scratch / 'recovery/installer/payload-ref.json'
    reference.parent.mkdir(parents=True)
    reference.write_text(json.dumps(payload))
    environment = dict(os.environ, BENPILOT_SOURCE_ROOT=str(scratch))
    subprocess.run([sys.executable, str(RECIPE / 'check_installer_guards.py')], env=environment, check=True)
  print('PASS: 3X delta changes only model guard/message; payload, OS, controls, firmware and settings are unchanged.')


if __name__ == '__main__':
  main()
