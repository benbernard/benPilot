"""Constrain branding to exact text/class substitutions in the original July UI.

Stored settings and serialized field names are compatibility identifiers, not
product labels. This check rejects any additional change in these UI files.
"""
from pathlib import Path
import re
import subprocess

BASELINE = 'b47add65d32e232b939d4915cca0b5a9ddafc48d'
BRANDING_PATHS = (
  'common/version.h',
  'selfdrive/ui/qt/util.cc',
  'selfdrive/ui/qt/offroad/settings.cc',
  'selfdrive/ui/qt/offroad/settings.h',
  'selfdrive/ui/qt/offroad/software_settings.cc',
  'selfdrive/ui/qt/offroad/developer_panel.cc',
  'selfdrive/ui/qt/offroad/onboarding.cc',
  'selfdrive/ui/qt/onroad/alerts.cc',
)


def expected_source(path, original):
  if path == 'common/version.h':
    return original.replace('0.9.8(v3.18)', '0.9.8(v3.18)-benPilot.1')
  if path.endswith('/util.cc'):
    return original.replace('QObject::tr("jvePilot")', 'QObject::tr("benPilot")')
  if path.endswith(('/settings.cc', '/settings.h')):
    text = original.replace('JvePilotTogglesPanel', 'BenPilotTogglesPanel')
    if path.endswith('.cc'):
      text = re.sub(r'jvePilot(?!\.)', 'benPilot', text).replace('openpilot', 'benPilot')
    return text
  if path.endswith('/software_settings.cc'):
    return original.replace('  // download update btn\n',
      '  addItem(new LabelControl(tr("Origin"), tr("jvePilot by John Van Etten"),\n'
      '                           tr("benPilot is based on jvePilot and comma.ai openpilot.")));\n\n'
      '  // download update btn\n')
  if path.endswith('/developer_panel.cc'):
    return original.replace('openpilot', 'benPilot')
  if path.endswith('/onboarding.cc'):
    return original.replace('tr("Welcome to openpilot")', 'tr("Welcome to benPilot")')
  if path.endswith('/alerts.cc'):
    return original.replace('tr("openpilot Unavailable")', 'tr("benPilot Unavailable")')
  raise AssertionError(path)


def verify(root):
  for path in BRANDING_PATHS:
    original = subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=root, text=True)
    actual = (root / path).read_text()
    assert actual == expected_source(path, original), f'Unreviewed change beyond branding: {path}'
    old_keys = re.findall(r'"jvePilot\.[^"\n]+"', original)
    new_keys = re.findall(r'"jvePilot\.[^"\n]+"', actual)
    assert old_keys == new_keys, f'Persistent setting identifiers changed: {path}'
  print('PASS: exact UI name/version/class substitutions and visible origin credit only; all stored setting identifiers retained.')


if __name__ == '__main__':
  verify(Path(__file__).resolve().parents[2])
