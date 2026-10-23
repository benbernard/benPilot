"""Inspect the compiled ELF without executing its installer entry point."""
import hashlib
from pathlib import Path
import struct
import sys

path = Path(sys.argv[1])
data = path.read_bytes()
assert data[:6] == b'\x7fELF\x02\x01', 'Expected little-endian 64-bit ELF'
assert struct.unpack_from('<H', data, 18)[0] == 183, 'Expected AArch64 machine type'
assert len(data) < 370_000, 'Installer exceeds the original source size limit'
for value in (b'https://github.com/benbernard/benPilot.git',
              b'b47add65d32e232b939d4915cca0b5a9ddafc48d',
              b'Installing benPilot...', b'Based on jvePilot by John Van Etten'):
  assert value in data, f'Missing expected installer identity: {value!r}'
print(f'PASS: AArch64 ELF, pinned original payload and explicit jvePilot attribution; {len(data)} bytes; SHA256 {hashlib.sha256(data).hexdigest()}')
