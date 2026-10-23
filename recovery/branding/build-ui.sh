#!/bin/bash
set -euo pipefail
exec > >(tee /out/ui-build.log) 2>&1
: "${BENPILOT_BUILD_COMMIT:?Set the exact reviewed source commit}"
[[ "$BENPILOT_BUILD_COMMIT" =~ ^[0-9a-f]{40}$ ]]
git config --global --add safe.directory /source.git
git init /work/checkout
cd /work/checkout
git fetch --no-tags --depth=1 /source.git "$BENPILOT_BUILD_COMMIT"
git -c core.hooksPath=/dev/null checkout --detach "$BENPILOT_BUILD_COMMIT"
test "$(git rev-parse HEAD)" = "$BENPILOT_BUILD_COMMIT"
touch /TICI .lfsconfig
mkdir -p /data/scons_cache
export PYTHONPATH=/work/checkout:/work/checkout/tinygrad_repo
# Compile the actual QCOM2/larch64 UI only. Never start UI/device services.
scons -j2 selfdrive/ui/ui
cp selfdrive/ui/ui /out/benpilot-ui-candidate
readelf -h -l -d /out/benpilot-ui-candidate > /out/ui-elf-metadata.txt
sha256sum /out/benpilot-ui-candidate > /out/UI-SHA256SUMS
python3 /recipe/smoke_brand.py
printf 'UI compiled only; not launched, installed or vehicle validated.\n'
