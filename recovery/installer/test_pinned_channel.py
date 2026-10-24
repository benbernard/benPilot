"""Exercise actual pinned checkout commands after the update channel advances."""
import ast

import re
import shlex
import subprocess
import tempfile
from pathlib import Path


def resolve(node: ast.AST, names: dict[str, str]) -> str:
  if isinstance(node, ast.Constant) and isinstance(node.value, str):
    return node.value
  if isinstance(node, ast.Name):
    return names[node.id]
  if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
    return resolve(node.left, names) + resolve(node.right, names)
  raise ValueError('Unexpected command expression')


def git(root: Path, *args: str) -> str:
  return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()


def verify(source: str) -> None:
  expressions = [value for value in re.findall(r'run\(\(([^\n]+)\)\.c_str\(\)\);', source)
                 if 'EXPECTED_COMMIT' in value]
  assert len(expressions) == 2
  with tempfile.TemporaryDirectory(prefix='benpilot-pinned-channel-') as directory:
    root = Path(directory)
    remote = root / 'remote'
    remote.mkdir()
    git(remote, 'init', '-b', 'benPilot-release')
    git(remote, 'config', 'user.name', 'Fixture')
    git(remote, 'config', 'user.email', 'fixture@example.invalid')
    (remote / 'fixture').write_text('original\n')
    git(remote, 'add', 'fixture')
    git(remote, 'commit', '-m', 'Original approved source')
    pinned = git(remote, 'rev-parse', 'HEAD')
    (remote / 'fixture').write_text('newer\n')
    git(remote, 'commit', '-am', 'Later approved source')
    newer = git(remote, 'rev-parse', 'HEAD')
    git(root, 'clone', '--depth=1', '-b', 'benPilot-release', remote.as_uri(), 'device')
    device = root / 'device'
    names = {'EXPECTED_COMMIT': pinned, 'BRANCH_STR': 'benPilot-release'}
    commands = [shlex.split(resolve(ast.parse(value, mode='eval').body, names)) for value in expressions]
    assert commands[0][:4] == ['git', 'fetch', '--depth=1', 'origin']
    assert commands[1][:3] == ['git', 'checkout', '-B']
    for command in commands:
      subprocess.run(command, cwd=device, check=True, capture_output=True)
    assert git(device, 'rev-parse', 'HEAD') == pinned
    assert git(device, 'branch', '--show-current') == 'benPilot-release'
    assert (device / 'fixture').read_text() == 'original\n'
    git(device, 'fetch', 'origin', 'benPilot-release')
    assert git(device, 'rev-parse', 'FETCH_HEAD') == newer
    bad = subprocess.run(['git','fetch','--depth=1','origin','0'*40], cwd=device, capture_output=True)
    assert bad.returncode != 0
    assert git(device, 'rev-parse', 'HEAD') == pinned
  print('PASS: actual installer checkout commands retain pinned initial source after channel advancement, preserve branch updates, and reject a missing revision.')
