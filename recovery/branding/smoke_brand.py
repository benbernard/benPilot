"""Execute only the actual Qt getBrand helper, without UI/hardware initialization."""
from pathlib import Path
import re
import shlex
import subprocess

root = Path('/work/checkout')
text = (root / 'selfdrive/ui/qt/util.cc').read_text()
function = re.search(r'^QString getBrand\(\) \{.*?^\}', text, re.M | re.S).group(0)
source = ('#include <QObject>\n#include <QString>\n#include <cassert>\n'
          '#include "common/version.h"\n' + function + '\n'
          'int main() { assert(getBrand() == "benPilot"); '
          'assert(QString(COMMA_VERSION) == "0.9.8(v3.18)-benPilot.1"); }\n')
Path('/out/brand-smoke.cc').write_text(source)
flags = shlex.split(subprocess.check_output(['pkg-config', '--cflags', '--libs', 'Qt5Core'], text=True))
subprocess.run(['c++', '-fPIC', '-I' + str(root), '/out/brand-smoke.cc', '-o', '/out/brand-smoke', *flags], check=True)
subprocess.run(['/out/brand-smoke'], check=True)
data = Path('/out/benpilot-ui-candidate').read_bytes()
for label in (b'benPilot', b'BenPilotTogglesPanel', b'jvePilot by John Van Etten'):
  assert label in data, f'Missing compiled UI identity: {label!r}'
print('PASS: real Qt brand helper and version identify benPilot; compiled UI contains renamed panel and origin credit. No UI/service initialized.')
