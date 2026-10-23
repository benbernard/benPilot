# July comma-three installer candidate

This branch builds a small ARM64 installer bootstrap. It does **not** contain a complete prebuilt driving release and is not validated for installation on the fitted device yet. The payload remains exact original July commit `b47add65d32e232b939d4915cca0b5a9ddafc48d`, 0.9.8(v3.18), from the user-owned `jvePilot-release` channel. No controller, model, DBC, panda or safety code is changed by this branch.

The separate [source recovery and validation draft](https://github.com/benbernard/jvepilot-recovery/pull/1) records the native model-generation requirement and inherited Pacifica safety-test disagreements. These remain deployment gates.

## Bootstrap changes

- Select the explicit user-owned recovery repository and `jvePilot-release` rather than upstream/default refs.
- Refuse targets other than comma three (`tici`) with AGNOS 11.13. The guard runs before installation writes; it does not flash, downgrade or waive OS requirements.
- Refuse an existing installation directory. Remove only temporary installation staging, not `/data/openpilot`. The later reviewed reinstall procedure and verified backup remain prerequisites.
- Fresh-clone the recovery source instead of using a cache that could retain a discontinued origin. Existing cache is untouched.
- Check the cloned full HEAD against the exact July SHA before moving it into the installation path or writing the continuation script. A changed ref fails closed.
- Preserve the inherited TLS/Git mechanism, meaningful updater checks and all payload driving/safety behavior. No access keys are added and no firmware signing/security checks are changed.

On later authorized use after the required backup/compatibility review, this bootstrap would clone source and activate its ordinary launcher. That launcher builds natively when no `prebuilt` marker exists. Such a native build can generate firmware as well as models; the actual installed firmware/signatures and resulting build must be reviewed before authorizing that procedure. Merely downloading the bootstrap does not run it, back up settings or install software.

## Verification and limits

The installer target compiled successfully through the recovered `larch64`/QCOM2 SCons path in an isolated Ubuntu 24.04 ARM64 container. Private Qt and Wayland development headers were added to the build environment; production dependencies and payload source were not changed. ELF headers identify AArch64 PIE with `/lib/ld-linux-aarch64.so.1`. All required libraries resolve in that build environment. This does not establish the actual device's library ABI, Qt/Wayland runtime, current OS or setup-screen behavior.

Four isolated tests compile the actual preflight method with filesystem/process doubles. Wrong OS, wrong model and an existing installation invoke no installation commands. The permitted case requests only temporary staging cleanup and a fresh clone. The doubles never execute shell commands. A separate static check verifies that exact-SHA validation precedes activation. The real Qt installer executable has not been launched.

`installer-manifest.json`, `guard-tests.log`, `elf-metadata.txt` and `linkage-check.txt` preserve the candidate hash, source patch identity and verification limits. The build image derives from the previously frozen July build environment, adding only the documented Qt/Wayland headers. `build-installer.sh` clones the read-only original bare source at the pinned baseline, applies the reviewed patch, enables installer build graph entries only in disposable scratch space, and builds only the installer target. It never runs the inherited destructive/force-pushing release builder.

The release download will be labeled **candidate / prerelease**. Do not enter it into the comma setup screen yet. First establish existing parked SSH access, inventory full installed source/local edits/OS/firmware, verify private settings/full-state backup and rollback, then present the concrete compatibility and reinstall plan for the required confirmation. No device changes or road testing occurred during preparation.
