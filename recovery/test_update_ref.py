"""Exercise the July check_for_update method against disposable real Git remotes.

The method is extracted verbatim by AST to avoid importing device services.
No fetch_update, Params writes, OverlayFS, OS updater or alert code is executed.
setup_git_options is intentionally a no-op in this harness; Git operations are
restricted to the disposable local repository. This does not test staging.
"""
import ast
from collections import defaultdict
from pathlib import Path
import os
import re
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

SOURCE_ROOT = Path(os.environ.get('BENPILOT_SOURCE_ROOT', Path(__file__).resolve().parents[1]))
SOURCE = SOURCE_ROOT / 'system/updated/updated.py'


class UpdateRefTest(unittest.TestCase):
  def test_available_missing_and_unreachable_refs(self):
    module = ast.parse(SOURCE.read_text())
    method = next(m for cls in module.body if isinstance(cls, ast.ClassDef) and cls.name == 'Updater'
                  for m in cls.body if isinstance(m, ast.FunctionDef) and m.name == 'check_for_update')
    with tempfile.TemporaryDirectory() as tmp:
      repo = Path(tmp) / 'checkout'
      remote = Path(tmp) / 'origin.git'

      def git(*args, cwd=None):
        return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=cwd, text=True,
                                       stderr=subprocess.STDOUT).strip()

      git('init', '--bare', '--initial-branch=jvePilot-release', str(remote))
      git('init', '--initial-branch=jvePilot-release', str(repo))
      git('-c', 'user.name=Recovery Test', '-c', 'user.email=test@example.invalid', 'commit', '--allow-empty', '-m', 'fixture', cwd=repo)
      sha = git('rev-parse', 'HEAD', cwd=repo)
      git('remote', 'add', 'origin', str(remote), cwd=repo)
      git('push', 'origin', 'jvePilot-release', cwd=repo)
      messages = []
      namespace = {'cloudlog': SimpleNamespace(info=messages.append), 'OVERLAY_MERGED': str(repo),
                   'run': lambda cmd, cwd: subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.STDOUT),
                   'setup_git_options': lambda _: None, 'subprocess': subprocess, 'defaultdict': defaultdict, 're': re}
      exec(compile(ast.Module(body=[method], type_ignores=[]), str(SOURCE), 'exec'), namespace)
      updater = SimpleNamespace(target_branch='jvePilot-release',
                                get_branch=lambda _: 'jvePilot-release', get_commit_hash=lambda _: sha)
      check = namespace['check_for_update']
      check(updater)
      self.assertTrue(updater._has_internet)
      self.assertEqual(updater.branches['jvePilot-release'], sha)
      self.assertIn('up to date', messages[-1])

      publisher = Path(tmp) / 'publisher'
      git('clone', str(remote), str(publisher))
      git('-c', 'user.name=Recovery Test', '-c', 'user.email=test@example.invalid', 'commit', '--allow-empty', '-m', 'new fixture release', cwd=publisher)
      next_sha = git('rev-parse', 'HEAD', cwd=publisher)
      git('push', 'origin', 'jvePilot-release', cwd=publisher)
      check(updater)
      self.assertEqual(updater.branches['jvePilot-release'], next_sha)
      self.assertNotEqual(next_sha, sha)
      self.assertIn('update available', messages[-1])

      updater.target_branch = 'missing-release'
      check(updater)
      self.assertTrue(updater._has_internet)
      self.assertIsNone(updater.branches['missing-release'])
      self.assertIn('update available', messages[-1])
      with self.assertRaises(subprocess.CalledProcessError):
        git('fetch', 'origin', 'missing-release', cwd=repo)

      git('remote', 'set-url', 'origin', str(Path(tmp) / 'not-a-repository'), cwd=repo)
      with self.assertRaises(subprocess.CalledProcessError):
        check(updater)
      self.assertFalse(updater._has_internet)
      print('PASS: valid/same ref, new genuine release, absent ref + fetch failure, unreachable origin. No alerts/counters changed.')


if __name__ == '__main__':
  unittest.main()
