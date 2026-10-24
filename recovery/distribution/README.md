# Installation URL and update releases

Enter **`benpilot.bernards.space`** at the device's **Custom Software** prompt. The same URL downloads a compiled ARM64 installer for **comma three (`tici`) and comma 3X (`tizi`) on AGNOS 11.13**. Other hardware, OS versions and existing installations are refused before installation writes. Read the release and backup requirements at [the website](https://benpilot.bernards.space/about).

The previous `benpilot.crabanddog.com` and `comma.bernards.space` addresses remain aliases to the same release.

The short URL returns an uncached redirect to an immutable GitHub release asset. `/release` is an alias, `/manifest.json` describes the currently published bootstrap and payload, and `/about` opens the human-readable website. Downloaded executables are never selected from arbitrary request parameters or unreviewed integration commits.

## Installation versus updates

The installer fetches its exact recorded application commit and creates local branch `benPilot-release`. An old universal installer therefore remains pinned even after that remote branch advances. The ordinary updater subsequently reads the same repository and channel for newer releases. Device users use **Settings → Software → CHECK / DOWNLOAD → INSTALL**. The updater downloads while offroad and keeps its existing checks and warnings.

`benPilot` is the integration branch. Merging there builds candidates; it does not automatically change the application update channel. `benPilot-release` contains approved application source. `gh-pages` contains the review website. The three roles remain separate.

This is a source-installer distribution. The application builds natively through its ordinary launcher. A complete prebuilt driving image, native Qualcomm model generation and physical-device validation remain pending. This task changes no vehicle controls, models, firmware, persistent settings or existing safety behavior. Ben's reviewed baseline safety findings remain accepted.

## Prepare and promote a release

1. Prepare the application payload on a candidate ref. Update all installer payload references and the recorded installer patch when its pin changes. Preserve a fast-forward path from `benPilot-release`; never force-push that branch. A candidate payload can be ahead of the live channel while CI checks it.
2. Build the installer locally with `BENPILOT_INSTALLER_TARGET=universal`. Record its size and SHA-256 in `recovery/installer/universal/release.json`, with a fresh immutable tag. Commit and open a PR to `benPilot`.
3. Wait for both recovery CI jobs on the exact PR head. Scope checks run 90 genuine preflight cases, the pinned-checkout/channel-advance fixture and promotion rejection tests. The ARM64 recipe compiles all three bootstraps and checks their ELF identities. It also compiles the shared UI. Merge through the PR; keep the checked source.
4. Run the promotion helper from a clean checkout of the successful CI source. The default mode checks the exact CI source and every job, downloads its artifact, verifies the committed size/hash and ELF/source identity, and prepares hosting files without publishing:

   ```sh
   python3 recovery/distribution/promote.py --ci-run RUN_ID --hosting-dir /path/to/homelab-task/nas/homepage/benpilot
   ```

   Add `--publish` to create and verify an immutable prerelease. The helper refuses an existing release tag. It advances `benPilot-release` only through a normal fast-forward push to the checked payload, then verifies the anonymous public bootstrap download. Do not use an unrelated green workflow or a stale run.
5. Commit the generated `nginx.conf` and `release.json` in a new homelab-config task branch. Its PR and normal `homepage` pipeline publish the stable redirect. Confirm that the public URL, manifest, bootstrap hash and website match the new release. Keep the previous manifest/redirect commit for rollback. No device installation occurs during promotion.

The installer release process checks packaging and source identity. Changes to native application inputs still require the corresponding native/model/device validation before they can be called a validated driving release.

## What sunnypilot does

Research checked October 23, 2026:

- The official [URL installation guide](https://github.com/sunnypilot/user-docs/blob/master/docs/setup/url-method.md) distinguishes first installation through Custom Software from later updates and branch selection in Settings.
- Its [recommended branches](https://community.sunnypilot.ai/t/recommended-branches/235) map short URLs to named channels, with separate current recommendations for comma three, 3X and four. Multi-device support does not imply that every model uses one current branch.
- An HTTPS HEAD request to `release.sunnypilot.ai` returned an `application/octet-stream` attachment named `installer_openpilot`, rather than a website. The reviewed response was 1,295,328 bytes. We did not execute it.
- The organization's [installer-generator source](https://github.com/sunnypilot/openpilot-installer-generator) documents historical AGNOS/NEOS user-agent selection and repository/branch aliases. This establishes that generator's design, not that every detail matches today's production backend.

benPilot follows the short-URL, compiled-bootstrap and named-channel pattern. Its July payload already supports both three and 3X, so one hardware-aware bootstrap covers those two devices. It does not add comma two or four support or adopt sunnypilot's driving code.
