"""Execute only the actual Qt getBrand helper, without UI/hardware initialization."""
from pathlib import Path
import re
import json
import shlex
import subprocess
import xml.etree.ElementTree as ET

root = Path('/work/checkout')
text = (root / 'selfdrive/ui/qt/util.cc').read_text()
function = re.search(r'^QString getBrand\(\) \{.*?^\}', text, re.M | re.S).group(0)
catalog = ET.parse(root / 'selfdrive/ui/translations/main_es.ts')
expected = next(m.findtext('translation') for c in catalog.findall('context')
                if c.findtext('name') == 'TogglesPanel' for m in c.findall('message')
                if m.findtext('source') == 'Enable benPilot')
assert expected and 'benPilot' in expected
source = ('#include <QObject>\n#include <QString>\n#include <QCoreApplication>\n#include <QTranslator>\n#include <cassert>\n'
          '#include "common/version.h"\n' + function + '\n'
          'int main(int argc, char **argv) { QCoreApplication app(argc, argv); '
          'assert(getBrand() == "benPilot"); '
          'assert(QString(COMMA_VERSION) == "0.9.8(v3.18)-benPilot.1"); '
          'QTranslator translator; assert(translator.load("/work/checkout/selfdrive/ui/translations/main_es.qm")); '
          'app.installTranslator(&translator); '
          'assert(QCoreApplication::translate("TogglesPanel", "Enable benPilot") == QString::fromUtf8('
          + json.dumps(expected, ensure_ascii=False) + ')); }\n')
Path('/out/brand-smoke.cc').write_text(source)
flags = shlex.split(subprocess.check_output(['pkg-config', '--cflags', '--libs', 'Qt5Core'], text=True))
subprocess.run(['c++', '-fPIC', '-I' + str(root), '/out/brand-smoke.cc', '-o', '/out/brand-smoke', *flags], check=True)
subprocess.run(['/out/brand-smoke'], check=True)
data = Path('/out/benpilot-ui-candidate').read_bytes()
for label in (b'benPilot', b'BenPilotTogglesPanel', b'jvePilot by John Van Etten'):
  assert label in data, f'Missing compiled UI identity: {label!r}'
print('PASS: real Qt brand helper/version, compiled Spanish catalog and UI panel/origin credit identify benPilot. No UI/hardware service initialized.')
