"""Inspect the compiled ELF without executing its installer entry point."""
import hashlib
import json
from pathlib import Path
import struct
import sys

payload = json.loads((Path(__file__).resolve().parents[2] / 'recovery/installer/payload-ref.json').read_text())
path = Path(sys.argv[1])
data = path.read_bytes()
assert data[:6] == b'\x7fELF\x02\x01', 'Expected little-endian 64-bit ELF'
assert struct.unpack_from('<H', data, 18)[0] == 183, 'Expected AArch64 machine type'
assert len(data) < 370_000, 'Installer exceeds the original source size limit'
for value in (b'https://github.com/benbernard/benPilot.git',
              payload['commit'].encode(), payload['branch'].encode(),
              b'Installing benPilot...', b'Based on jvePilot by John Van Etten'):
  assert value in data, f'Missing expected installer identity: {value!r}'
print(f'PASS: AArch64 ELF, pinned branded July payload and explicit jvePilot attribution; {len(data)} bytes; SHA256 {hashlib.sha256(data).hexdigest()}')
