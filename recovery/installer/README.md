# benPilot UI-branded July comma-three installer candidate

A [separate comma 3X bootstrap](comma3x/README.md) uses the same pinned application with a `tizi`-only guard. The comma-three candidate and its original assets remain unchanged.

benPilot originates from **jvePilot by John Van Etten (j-vanetten)**, based on comma.ai openpilot. The new bootstrap pins the branded application source at `2a8c27188bf10021736621bab4ce6975fc38edcc` on the public `benPilot-release` channel. Its app/settings/welcome/alert labels and version identify **benPilot**, version **0.9.8(v3.18)-benPilot.1**, with visible origin credit. Persistent `jvePilot.settings.*` keys and serialized schemas stay compatible. Original July control, safety, models, firmware and AGNOS requirements remain unchanged.

The original July source remains at `b47add65d32e232b939d4915cca0b5a9ddafc48d` on `jvePilot-release`; candidate 2 and its bytes stay available unchanged. Candidate 3 is separate, not a silent replacement. The `benPilot-release` alias has exactly the original July release flags, keeping release-only behavior unchanged. Existing channels, the upstream/fork identity check and genuine update/failure handling are retained. This classification does not claim validation on the fitted vehicle.

## Bootstrap and source guards

The installer selects the explicit user-owned repository, branch and full payload SHA recorded in `payload-ref.json`. It refuses any model other than comma three (`tici`), any OS other than AGNOS 11.13, and an existing `/data/openpilot` directory before installation writes. The allowed case cleans only temporary staging, performs a fresh clone, and checks full HEAD before activation. No security checks, keys, firmware verification or updater warnings are bypassed.

CI verifies that the public ref is reachable at the pinned SHA/tree and that the pinned production application matches the reviewed source apart from installer/build documentation. Both the original and new branch are exercised with real disposable Git remotes for current/new/missing/unreachable refs. Actual preflight tests use command/filesystem doubles and never execute installation commands.

`build-installer.sh` builds only the bootstrap from the original July source plus the recorded installer patch, in an isolated ARM64 environment. It never runs the inherited destructive release builder. The source payload contains no `prebuilt` marker or stale compiled UI. On later authorized use the ordinary launcher would build natively; that can generate firmware as well as models, so actual installed source/OS/firmware, backup/rollback and resulting build require review first.

## Build evidence and deployment limits

The installer is an AArch64 ELF bootstrap, not a complete prebuilt driving release. Its manifest records the source/payload/patch identities and binary hash. The true UI compiles through the QCOM2/larch64 path with documented **Ubuntu-only** GL/EGL dependencies in disposable CI checkouts. That UI binary is named `benpilot-ui-ubuntu-compile-check`; neither it nor the host dispatch library is an AGNOS deployment artifact. Production UI build rules and GPU behavior are untouched. Qt smoke checks execute only the small brand/version helper and compiled translation lookup, never the UI service or graphics adapter entry points.

Full native model generation and actual fitted-device ABI/UI/firmware validation remain incomplete. Ben personally reviewed the inherited safety findings on October 23, 2026 and approved them as nonissues given the existing protections. Original test results remain recorded. Green recovery/installer/UI compile CI does not establish full device validation. Nothing has been installed or road-tested.

Do not enter the candidate URL in the setup screen yet. First obtain the existing SSH address/alias and parked confirmation; inventory full installed commit, local edits, OS and firmware; verify private full-state/settings/calibration backup and rollback; then present the concrete compatibility/reinstall plan and obtain the required deployment confirmation. No purchases, credentials or access grants are required by this source preparation.
