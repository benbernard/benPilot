---
layout: default
title: benPilot
---

# benPilot

A recovery fork of **[jvePilot by John Van Etten (j-vanetten)](https://github.com/j-vanetten/openpilot)**, based on [comma.ai openpilot](https://github.com/commaai/openpilot). Attribution, licenses and source history are preserved. The application identifies as **benPilot 0.9.8(v3.18)-benPilot.1**.

## Install on comma three or 3X

Enter this address at the device's **Custom Software** prompt:

```text
benpilot.bernards.space
```

One compiled installer recognizes **comma three (`tici`) and comma 3X (`tizi`) on AGNOS 11.13**. It downloads the exact reviewed application source and preserves the normal update channel. Other hardware and OS versions are refused. Before replacing a working installation, verify its private backup, compatibility and restoration plan. The bootstrap refuses an existing installation.

- [Review the universal installer release and checksums](https://github.com/benbernard/benPilot/releases/tag/benpilot-july-universal-1)
- [Current installation manifest](https://benpilot.bernards.space/manifest.json)
- [Download the installer directly](https://github.com/benbernard/benPilot/releases/download/benpilot-july-universal-1/install-benpilot)

This is a source installer. A complete prebuilt driving image, native Qualcomm model generation and physical-device validation remain pending. No device installation was performed during publication.

## Get updates

After installation, use **Settings → Software → CHECK / DOWNLOAD → INSTALL**. Updates download while offroad. Both models use `benPilot-release` in the [benPilot repository](https://github.com/benbernard/benPilot). You keep the same installation URL when a new installer is published.

Integration changes produce CI candidates. The release process requires successful checks on the exact source, verifies the built executable, and promotes the approved application channel using fast-forward changes. The short URL moves through a checked hosting release. [Maintainer release instructions and sunnypilot comparison](https://github.com/benbernard/benPilot/blob/benPilot/recovery/distribution/README.md).

The current application payload is `2a8c27188bf10021736621bab4ce6975fc38edcc`. The universal installer keeps that initial checkout pinned even as later approved updates advance the channel. Existing settings keys, serialized schemas, original July controls, safety behavior, models and firmware source remain unchanged. Ben reviewed and accepted the inherited safety findings; the original test results remain recorded.

## Preserved releases

The earlier [comma-three candidate 3](https://github.com/benbernard/benPilot/releases/tag/benpilot-ui-july-c3-candidate-3) and [3X candidate 1](https://github.com/benbernard/benPilot/releases/tag/benpilot-ui-july-c3x-candidate-1) retain their original bytes. The universal URL above is the shared entry point going forward.

[Candidate 2](https://github.com/benbernard/benPilot/releases/tag/benpilot-july-c3-candidate-2) retains the original July UI. Original source remains on [`jvePilot-release`](https://github.com/benbernard/benPilot/tree/jvePilot-release), commit `b47add65d32e232b939d4915cca0b5a9ddafc48d`, version `0.9.8(v3.18)`.

[Source repository and build evidence](https://github.com/benbernard/benPilot) · [Original-source recovery release](https://github.com/benbernard/benPilot/releases/tag/jve-july-2025-recovery-source-1)
