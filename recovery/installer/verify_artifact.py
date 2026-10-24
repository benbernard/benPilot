"""Inspect the compiled ELF without executing its installer entry point."""
import hashlib
import argparse
import json
from pathlib import Path
import struct

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('artifact', type=Path)
parser.add_argument('--payload-ref', type=Path,
                    default=Path(__file__).with_name('payload-ref.json'))
args = parser.parse_args()
payload = json.loads(args.payload_ref.read_text())
path = args.artifact
data = path.read_bytes()
assert data[:6] == b'\x7fELF\x02\x01', 'Expected little-endian 64-bit ELF'
assert struct.unpack_from('<H', data, 18)[0] == 183, 'Expected AArch64 machine type'
assert len(data) < 370_000, 'Installer exceeds the original source size limit'
for value in (b'https://github.com/benbernard/benPilot.git',
              payload['commit'].encode(), payload['branch'].encode(),
              b'Installing benPilot...', b'Based on jvePilot by John Van Etten'):
  assert value in data, f'Missing expected installer identity: {value!r}'
model_names = {'tici': 'comma three', 'tizi': 'comma 3X'}
message = f'Requires {model_names[payload["required_model"]]} with AGNOS 11.13. No installation changes made.'
assert message.encode() in data, 'Installer has the wrong hardware preflight message'
print(f'PASS: AArch64 ELF, pinned branded July payload and explicit jvePilot attribution; {len(data)} bytes; SHA256 {hashlib.sha256(data).hexdigest()}')
