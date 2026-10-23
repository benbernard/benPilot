#!/bin/bash
set -euo pipefail
exec > >(tee /out/compile-and-test.log) 2>&1
date -u
uname -a
uv --version
python3 --version
cp /apt-package-manifest.txt /python-package-manifest.txt /out/
git clone --no-local --no-checkout /source.git /work/checkout
cd /work/checkout
git -c core.hooksPath=/dev/null checkout --detach b47add65d32e232b939d4915cca0b5a9ddafc48d
test "$(git rev-parse HEAD^{tree})" = 2f99cbea39fd86565c4732fe7293750a8fde5715
export PYTHONPATH=/work/checkout:/work/checkout/tinygrad_repo
cd /work
ln -s checkout/system system
python3 /recipe/test_update_ref.py
cd /work/checkout
# Select the actual larch64/QCOM2 compiler path, but never run device services.
touch /TICI
mkdir -p /data/scons_cache
scons -j2 --minimal common/params_pyx.so opendbc_python cereal/libcereal.a selfdrive/pandad/pandad
readelf -h common/params_pyx.so opendbc/can/packer_pyx.so selfdrive/pandad/pandad > /out/artifact-types.txt
mkdir -p /out/partial-larch64
cp common/params_pyx.so opendbc/can/packer_pyx.so opendbc/can/parser_pyx.so opendbc/can/libdbc.so selfdrive/pandad/pandad /out/partial-larch64/
# These are source-level safety simulations. They do not connect to a panda.
cd opendbc_repo
scons -j2 opendbc/dbc/chrysler_pacifica_2017_hybrid_generated.dbc opendbc/safety/tests/libsafety/libsafety.so
set +e
python3 -m unittest opendbc.safety.tests.test_chrysler
safety_status=$?
set -e
printf '%s\n' "$safety_status" > /out/chrysler-safety-exit-status.txt
# A separate interpreter prevents Ram platform globals from carrying into the
# Pacifica class. Retain both results; do not turn failures into a passing build.
set +e
python3 -m unittest opendbc.safety.tests.test_chrysler.TestChryslerSafety > /out/pacifica-fresh-process-safety.log 2>&1
pacifica_status=$?
set -e
printf '%s\n' "$pacifica_status" > /out/pacifica-safety-exit-status.txt
cd /work/checkout
# Probe the unchanged model builder's genuine QCOM requirement. Capture a
# failure rather than substituting CPU outputs or faking Qualcomm validation.
set +e
QCOM=1 python3 tinygrad_repo/examples/openpilot/compile3.py /work/checkout/selfdrive/modeld/models/driving_policy.onnx /out/driving_policy_tinygrad.pkl > /out/qcom-model-build.log 2>&1
qcom_status=$?
set -e
printf '%s\n' "$qcom_status" > /out/qcom-model-exit-status.txt
git diff --stat > /out/generated-source-diff.txt
find /out/partial-larch64 -type f -exec sha256sum {} + > /out/artifact-sha256.txt
printf 'PARTIAL BUILD ONLY. No complete device install bundle. QCOM model exit status: %s\n' "$qcom_status"
exit "$safety_status"
