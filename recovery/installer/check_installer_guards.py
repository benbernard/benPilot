"""Compile the real preflight method with filesystem/process doubles.

The actual Qt installer executable is never launched. run() records commands
without executing them; no simulated /data path is created on the host/device.
"""
from pathlib import Path
import os
import subprocess
import tempfile

source_root = Path(os.environ.get('BENPILOT_SOURCE_ROOT', Path(__file__).resolve().parents[2]))
src = (source_root / 'selfdrive/ui/installer/installer.cc').read_text()
method = src[src.index('void Installer::doInstall() {'):src.index('void Installer::freshClone() {')]
prefix = r'''
#include <cassert>
#include <iostream>
#include <string>
#include <vector>
#include <unistd.h>
#define TMP_INSTALL_PATH "/data/tmppilot"
#define INSTALL_PATH "/data/openpilot"
std::string os_version, hardware_name;
bool existing_install;
std::vector<std::string> commands;
int clones;
namespace util {
  std::string read_file(const std::string&) { return os_version; }
  std::string strip(const std::string& s) { return s; }
  bool system_time_valid() { return true; }
}
struct Hardware { static std::string get_name() { return hardware_name; } };
struct QDir { QDir(const char*) {} bool exists() const { return existing_install; } };
struct Label { std::string text; void setText(const std::string& s) { text=s; } };
std::string tr(const char* s) { return s; }
std::ostream& qDebug() { return std::cerr; }
void run(const char* s) { commands.emplace_back(s); }
struct Installer {
 Label label; Label* val=&label;
 void doInstall();
 void freshClone() { clones++; }
};
'''
suffix = r'''
int main() {
  struct Scenario { const char* os; const char* model; bool exists; bool allow; };
  const Scenario cases[] = {
    {"12.8", "tici", false, false}, {"11.13", "tizi", false, false},
    {"11.13", "tici", true, false}, {"11.13", "tici", false, true}
  };
  for (const auto& c: cases) {
    os_version=c.os; hardware_name=c.model; existing_install=c.exists;
    commands.clear(); clones=0;
    Installer installer; installer.doInstall();
    if (!c.allow) { assert(commands.empty()); assert(clones==0); assert(!installer.label.text.empty()); }
    else { assert(commands==std::vector<std::string>{"rm -rf /data/tmppilot"}); assert(clones==1); }
  }
  std::cout << "PASS: actual preflight refuses wrong OS, wrong model and existing installation; valid target only cleans staging and requests fresh clone. No commands executed.\n";
}
'''
scratch = tempfile.TemporaryDirectory(prefix='benpilot-installer-guards-')
out = Path(scratch.name) / 'guard-test.cpp'
out.write_text(prefix+method+suffix)
executable = out.with_suffix('')
subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(out),'-o',str(executable)],check=True)
subprocess.run([str(executable)],check=True)
clone = src[src.index('void Installer::cloneFinished('):src.index('int main(')]
assert clone.index('!= EXPECTED_COMMIT') < clone.index('run("mv " TMP_INSTALL_PATH')
assert 'b47add65d32e232b939d4915cca0b5a9ddafc48d' in src
assert 'https://github.com/benbernard/benPilot.git' in src
assert 'freshClone();' in method and 'cachedFetch(' not in method
print('PASS: static review confirms pinned source check precedes activation and fresh-clone origin is the user-owned recovery repository.')
