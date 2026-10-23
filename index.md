---
layout: default
title: benPilot
---

# benPilot

A recovery fork of **[jvePilot by John Van Etten (j-vanetten)](https://github.com/j-vanetten/openpilot)**, based on [comma.ai openpilot](https://github.com/commaai/openpilot). Original attribution, licenses and source history are preserved.

## UI-branded July candidate

The new application identifies itself as **benPilot 0.9.8(v3.18)-benPilot.1** in its app name, settings, welcome and alert labels. The Software screen credits jvePilot and its author. Existing settings keys and serialized schemas stay unchanged, as do the original July control logic, safety checks, models and firmware source.

- [Review candidate 3, source, checksums and build limits](https://github.com/benbernard/benPilot/releases/tag/benpilot-ui-july-c3-candidate-3)
- [Download the pinned installer bootstrap](https://github.com/benbernard/benPilot/releases/download/benpilot-ui-july-c3-candidate-3/install-benpilot-comma3-candidate)
- [Inspect the exact branded payload](https://github.com/benbernard/benPilot/tree/2a8c27188bf10021736621bab4ce6975fc38edcc)

**Candidate only — do not load it before backup and compatibility review.** The bootstrap requires comma three (`tici`) with AGNOS 11.13 and refuses an existing installation. It is not a complete prebuilt driving image. Before device work, confirm the vehicle is parked, inventory installed source/OS/firmware, verify private installation/settings/calibration backup and rollback, and obtain the required deployment confirmation. Device validation and inherited safety-test disagreements remain pending.

Payload channel: `benPilot-release`, pinned at `2a8c27188bf10021736621bab4ce6975fc38edcc`. It retains the original July release behavior and normal update/failure checks. This page does not confirm successful installation or vehicle compatibility.

## Original recovery preserved

[Candidate 2](https://github.com/benbernard/benPilot/releases/tag/benpilot-july-c3-candidate-2) still downloads the original July jvePilot UI. The original source remains on [`jvePilot-release`](https://github.com/benbernard/benPilot/tree/jvePilot-release), commit `b47add65d32e232b939d4915cca0b5a9ddafc48d`, version 0.9.8(v3.18).

[Source repository and recovery evidence](https://github.com/benbernard/benPilot) · [Original-source recovery release](https://github.com/benbernard/benPilot/releases/tag/jve-july-2025-recovery-source-1)
