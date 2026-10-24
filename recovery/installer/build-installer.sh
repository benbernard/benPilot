#!/bin/bash
set -euo pipefail
exec > >(tee /out/build.log) 2>&1
case "${BENPILOT_INSTALLER_TARGET:-all}" in
  all) targets=(comma3 comma3x) ;;
  comma3) targets=(comma3) ;;
  comma3x) targets=(comma3x) ;;
  *) printf 'Unknown installer target\n' >&2; exit 1 ;;
esac
# This exception is limited to the disposable container's supplied repository.
git config --global --add safe.directory /source.git
git clone --no-local --no-checkout /source.git /work/checkout
cd /work/checkout
git fetch --no-tags --depth=1 /source.git b47add65d32e232b939d4915cca0b5a9ddafc48d
git -c core.hooksPath=/dev/null checkout --detach b47add65d32e232b939d4915cca0b5a9ddafc48d
git apply --check /recipe/recovery-installer.patch
git apply /recipe/recovery-installer.patch
touch /TICI .lfsconfig
mkdir -p /data/scons_cache
export PYTHONPATH=/work/checkout:/work/checkout/tinygrad_repo
: > /out/SHA256SUMS
for target in "${targets[@]}"; do
  artifact="install-benpilot-$target-candidate"
  payload_ref=/recipe/payload-ref.json
  if [[ "$target" == comma3x ]]; then
    git apply --check /recipe/comma3x/target.patch
    git apply /recipe/comma3x/target.patch
    payload_ref=/recipe/comma3x/payload-ref.json
  fi
  scons -j2 selfdrive/ui/installer/installers/installer_openpilot
  cp selfdrive/ui/installer/installers/installer_openpilot "/out/$artifact"
  python3 /recipe/verify_artifact.py "/out/$artifact" --payload-ref "$payload_ref"
  readelf -h -l -d "/out/$artifact" > "/out/$target-elf-metadata.txt"
  sha256sum "/out/$artifact" >> /out/SHA256SUMS
  git diff --stat > "/out/$target-source-diff-stat.txt"
  git diff --binary -- selfdrive/ui/SConscript selfdrive/ui/installer/installer.cc > "/out/$target-recovery-installer.patch"
done
printf 'Installer candidates compiled and inspected only; not executed or device validated.\n'
