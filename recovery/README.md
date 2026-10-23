# July JVE Pilot recovery for comma three

Updated October 23, 2026. **Source recovery and partial target compilation completed. A complete validated device build is blocked. Nothing has been installed.**

## Recovery source and reachable update channel

The user-owned fork is [benbernard/jvepilot-recovery](https://github.com/benbernard/jvepilot-recovery). Its [jvePilot-release branch](https://github.com/benbernard/jvepilot-recovery/tree/jvePilot-release) points to original-author commit **b47add65d32e232b939d4915cca0b5a9ddafc48d**, tree **2f99cbea39fd86565c4732fe7293750a8fde5715**, July 20, 2025, version **0.9.8(v3.18)**. It was recovered independently from the [original author's repository](https://github.com/j-vanetten/openpilot/commit/b47add65d32e232b939d4915cca0b5a9ddafc48d), matching the mirror archive. The commit is not signature-verified. The license and original attribution are retained.

The public branch was independently verified using GitHub's branch API and `git ls-remote`. It is the exact recovered tree, with no updater, driving, model, DBC, panda, safety or Starboard changes. Normal update behavior remains intact. This restores a reachable source channel; it is not yet evidence that the device's particular warning is fixed. Its actual origin, target and exception still need reading.

The fork's default branch remains the original author's discontinuation notice on gh-pages. The explicit recovery ref above is the intended channel; do not install a default-branch checkout or follow an unverified installer shortcut. The explicit release ref is reachable independently of the default branch.

## Build and test evidence

The isolated environment used Linux ARM64, Ubuntu 24.04, Python 3.12.3, uv 0.6.14 and the July `uv.lock` without resolution changes. Ubuntu and uv images were pinned by digest. Exact installed APT and Python package manifests were captured. The final OCI image was saved locally so reproduction does not depend on today's mutable package repositories.

Execution occurred only in disposable containers with network disabled, all capabilities dropped, resource limits and no vehicle/USB/CAN interfaces, home, personal credentials or Docker socket mounts. The source repository was read-only; scratch clones held generated files. The Mac's recovered review/repair worktrees have no application-code changes.

The real `larch64`/QCOM2 SCons path was selected in the container. These targets compiled successfully: `common/params_pyx.so`, `opendbc_python` (CAN parser/packer and libdbc), `cereal/libcereal.a`, and `selfdrive/pandad/pandad`. ELF headers identify AArch64 outputs. These are partial build artifacts, not an installation bundle; they have not been run on a device or validated against its installed AGNOS/ABI. No deployable panda firmware was built or signed.

The unchanged `check_for_update` method was tested against real disposable local Git remotes, extracted without importing device services. Cases passed: same reachable release, a genuine newer release, absent target plus fetch failure, and unreachable origin. The harness does not execute staging, OS updating, alert counters or device parameter writes; it does not claim OverlayFS/interruption/OS-flash coverage. No updater failure checks were removed or suppressed.

**Safety validation is unresolved.** The unmodified Chrysler-family suite ran 96 tests: 66 passed, 21 failed, 9 skipped. A fresh process running only `TestChryslerSafety` (the Pacifica class) ran 32 tests: 24 passed, 5 failed, 3 skipped. Its steering-limit tests passed in that fresh process. The combined run's additional Pacifica steering failures are consistent with the recovered initializer retaining Ram platform state between classes; the results do not establish equivalent failures in a freshly initialized Pacifica device.

The five remaining fresh-process failures are `test_buttons`, `test_cruise_engaged_prev`, `test_enable_control_allowed_from_cruise`, `test_fwd_hook`, and `test_spam_can_buses`. Static source inspection shows the JVE implementation and inherited test expectations differ in cruise/gear state handling, button filtering and permitted/forwarded messages. This is an explanation to investigate, not permission to dismiss tests or a validated replacement suite. Neither safety source nor tests were changed to obtain a pass. These failures block a claim of completed validation.

The genuine Qualcomm model build loaded the unchanged local ONNX model, then failed at opening **`/dev/kgsl-3d0`**, absent from the Mac's ARM64 Linux VM. This confirms that ARM64 alone does not provide the required Qualcomm GPU. CPU-generated or mocked model outputs were not substituted. The [original model build rules](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/selfdrive/modeld/SConscript) and [QCOM runtime](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/tinygrad_repo/tinygrad/runtime/ops_qcom.py) establish the requirement.

The [focused diagnosis of all five failures](SAFETY-FAILURE-DIAGNOSIS.md) now separates missing-state fixtures, stale expected message lists and actual baseline button/control-state acceptance. Six memory-only probes agree between the generated test DBC and JVE production DBC. No assertions or safety code were changed; the failures remain recorded.

## Exact remaining gates

1. Obtain the already configured comma IP/SSH alias and parked confirmation. The existing Mac configuration contains no comma host; no speculative host connection was attempted. JVE documents the standard comma GitHub-key SSH mechanism, plus the comma Prime proxy where already configured. No keys/access were added.
2. Privately read the full installed SHA, clean/modified/untracked state, actual origin and update target/error, AGNOS, hardware and firmware. The Software photo matches the July version/branch/prefix, and Ben confirms comma three; neither proves the full installed tree. The recovered source requests **AGNOS 11.13**; installed AGNOS remains unknown.
3. Back up the complete installed checkout/Git objects/local changes, params/calibration/JVE settings and applicable persistent state through existing verified access. Verify extraction, hashes, consistency and a self-contained rollback. Keep credentials and device identifiers private. No backup has occurred yet.
4. Review the five Pacifica safety-test disagreements and match the installed main/auxiliary firmware before proposing a reinstall that could trigger firmware updates. Preserve the existing behavior; do not change safety controls or weaken assertions to meet this step.
5. Complete model generation and full native dependency/ABI validation on identified compatible, isolated Qualcomm hardware or a trustworthy matching build environment. Using the fitted device for scratch compilation would need a concrete parked/offline procedure, verified backup, storage assessment and required execution approval first. No such action is currently performed.
6. Present exact artifacts, differences, compatibility, a meaningful updater check and proven rollback for the required device/security confirmation before deployment. No road test or vehicle control is in scope.

The smallest immediate unblock is the existing device IP/alias plus confirmation that the Pacifica is safely parked. No new hardware purchase is required to complete source recovery or the offline checks already performed.

## Reproduce the isolated checks

These files are build/test evidence, not an installer. A complete exact-source bare repository is supplied read-only to the container; the script explicitly checks out and verifies the original July SHA/tree. The frozen dependency image is retained locally (archive SHA-256 431f6b1f833124fe9b34495b2592e72571306d3d785bc0ed9422605c0d9df367); it is not published here. For a fresh environment build, stage only `recovery/Dockerfile`, the release's `pyproject.toml` and `uv.lock` into a dedicated Docker context. Build it for `linux/arm64` with tag `jvepilot-july-c3-build:20261023`. APT package versions are recorded in the attached manifest; only the preserved image reproduces those exact repository package bytes offline.

Run `run-isolated.sh` inside that image with network disabled, all capabilities dropped, `no-new-privileges`, 2 CPU / 2500 MiB / 512-PID limits. Mount only the source bare repository at `/source.git` read-only, an empty scratch output directory at `/out` writable, and this script plus `test_update_ref.py` at `/recipe/` read-only. Do not mount home, credentials, Docker socket, USB/CAN or vehicle devices. The script exits nonzero for the unresolved safety failures and labels the result partial even if compilation succeeds.

Included receipts: `validation-result.json`, `source-provenance.json`, APT/Python manifests, `artifact-sha256.txt`, updater-ref test log, fresh Pacifica safety log, and Qualcomm model failure log. Absolute `/out` artifact paths refer to the isolated container. No binary or environment archive is published as a release asset. Initial combined-family safety results remain recorded in the local complete log.

The inherited `release/build_release.sh` is not used: it deletes a build directory, chooses an upstream remote and force-pushes. No source safety changes, firmware signature/security changes or warning suppression are part of this recovery.
