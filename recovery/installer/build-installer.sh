#!/bin/bash
set -euo pipefail
exec > >(tee /out/build.log) 2>&1
git clone --no-local --no-checkout /source.git /work/checkout
cd /work/checkout
git -c core.hooksPath=/dev/null checkout --detach b47add65d32e232b939d4915cca0b5a9ddafc48d
git apply --check /recipe/recovery-installer.patch
git apply /recipe/recovery-installer.patch
touch /TICI .lfsconfig
mkdir -p /data/scons_cache
export PYTHONPATH=/work/checkout:/work/checkout/tinygrad_repo
scons -j2 selfdrive/ui/installer/installers/installer_openpilot
cp selfdrive/ui/installer/installers/installer_openpilot /out/install-benpilot-comma3-candidate
readelf -h -l -d /out/install-benpilot-comma3-candidate > /out/elf-metadata.txt
sha256sum /out/install-benpilot-comma3-candidate > /out/SHA256SUMS
git diff --stat > /out/source-diff-stat.txt
printf 'Installer candidate compiled only; not executed or device validated.\n'
