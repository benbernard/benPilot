# comma 3X installer candidate

The July source already supports comma 3X (`tizi`) through the shared QCOM2/larch64 build. This candidate uses the same benPilot application as comma-three candidate 3: version **0.9.8(v3.18)-benPilot.1**, branch `benPilot-release`, commit `2a8c27188bf10021736621bab4ce6975fc38edcc`, tree `b8b0db69ab097f35fbbf6cbef07bbf2e3aefcef6`.

The separate ARM64 bootstrap accepts only **comma 3X on AGNOS 11.13**. It rejects comma three, comma four, unknown hardware, other OS versions and an existing `/data/openpilot` before installation writes. It retains the full source pin, fresh staging and visible jvePilot / John Van Etten credit. Existing comma-three candidate 3, its payload branch and its release assets stay pinned.

## Source and checks

`target.patch` applies after `../recovery-installer.patch`. It changes only the hardware comparison from `tici` to `tizi` and the corresponding error message. `payload-ref.json` differs from the comma-three reference only in `required_model`. No driving, safety, firmware, model, OS or persistent-settings source changes are needed.

`../check_comma3x.py` verifies that exact delta, the existing TIZI hardware mapping and AGNOS requirement, then compiles the real patched preflight method with command/filesystem doubles. It exercises 30 hardware/OS/existing-installation combinations without running installation commands. The comma-three method has the same 30-case check. CI compiles both installers and inspects the ELF architecture, size, source pin and hardware message.

Build with the existing isolated ARM64 recipe and dependency image, setting `BENPILOT_INSTALLER_TARGET=comma3x`. The output is `install-benpilot-comma3x-candidate`. By default the existing CI build step compiles and inspects both installers. Set `BENPILOT_INSTALLER_TARGET=comma3` for the original target alone. Disable network access, omit device mounts, drop capabilities and preserve the workflow's resource limits. Local Colima builds can copy the source repository and recipe into a dedicated container when external-volume bind mounts are unavailable. Copy its output out after compilation.

## Validation boundary

This is a source-installer bootstrap. Native model generation and a complete prebuilt driving image still require a matching Qualcomm GPU environment. The Ubuntu installer build does not establish AGNOS ABI, bootability or fitted-device operation. No device has been contacted, flashed or installed by this build task.

Ben personally reviewed the documented inherited safety findings on October 23, 2026 and approved them as nonissues given the existing protections. They are accepted for this task. Original failed assertions remain recorded in [the diagnosis](../../SAFETY-FAILURE-DIAGNOSIS.md).

Before using the candidate, identify the 3X's installed source, hardware revision, OS and firmware, verify a private backup and restoration path, and agree the installation plan. An incompatible OS must be handled through that plan. Do not delete the working installation or change the OS merely to satisfy the bootstrap guards.
