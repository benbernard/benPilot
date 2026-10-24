# Five July Pacifica safety-test failures: diagnosis

**Owner disposition, October 23, 2026:** Ben personally reviewed these inherited findings and approved them as nonissues given the existing protections. Their review is complete for this task. This diagnosis preserves the original observations and test outcomes; references below to pending review describe the earlier investigation.

October 23, 2026. Baseline: **b47add65d32e232b939d4915cca0b5a9ddafc48d**, original July 0.9.8(v3.18). No production code or inherited test was changed. No full build was retried and no device was accessed.

All five failures occur in the untouched baseline's fresh-process `TestChryslerSafety` run: 32 tests, 24 passed, 5 failed, 3 skipped. They are genuine failed assertions. They were not introduced by the new recovery fork or an updater repair. The descriptions below distinguish an outdated/incomplete test expectation from what the implementation actually permits; they do not waive safety validation.

| Exact failure | Original assertion and observed result | Cause and classification |
|---|---|---|
| `test_buttons` | The test expects simultaneous cancel+resume to be rejected; TX hook returns true. | The July Chrysler-specific button filter is commented out. The generic TX wrapper still enforces the message whitelist and relay-malfunction gate, but does not supply the test's button-content/control-state rule. In-memory probes also found empty, resume, cancel and combined button messages accepted with controls either false or true. This is actual permissive baseline behavior, not a compiler/DBC artifact; its safety requirements need explicit review. |
| `test_cruise_engaged_prev` | After an ACC-active status, the test expects stored engagement true; it stays false. | The fixture sends ACC status alone. July JVE gates that logic on a preceding forward-gear input; the fresh process starts with `forward_gear=false`. RX accepts the status frame, then deliberately calls the cruise helper with false. Also, stationary forward-gear behavior deliberately forces the engagement transition independently of ACC, so merely adding a gear message would not make the old universal expectation adequate. This is a missing-state/changed-semantics fixture mismatch, not a failed frame decode. |
| `test_enable_control_allowed_from_cruise` | The test sends inactive then active ACC status and expects controls true; they remain false. | Same missing forward-gear prerequisite. In a separate probe, valid forward-gear and moving-speed inputs caused inactive/active ACC to produce false/true controls and engagement as expected. At standstill in forward gear, July's `long_allowed` path produces true controls/engagement even for inactive ACC. This explains the old assertion's failure but is not a complete validation of JVE's engagement policy. |
| `test_fwd_hook` | The fixture expects a camera heartbeat message to forward to bus 0; the hook returns blocked (`-1`). | The fixture blacklist lists two messages. July's forwarding hook additionally blocks `LKAS_HEARTBIT`; the fixture omits it. This is a stale expected blacklist compared with the baseline implementation, not loss of forwarding caused by the build environment. Whether replacement heartbeat behavior is correct needs JVE-specific coverage. |
| `test_spam_can_buses` | The fixture expects an unlisted message to be rejected; July accepts `DAS_3`. | The fixture TX list contains three messages; the production whitelist contains six, adding `DAS_3`, `DAS_5` and `LKAS_HEARTBIT`. The broad eight-byte scan first stops at `DAS_3`; it cannot cover the added heartbeat's actual length. Memory-only probes confirmed the added messages are accepted with controls initially false and pedals unpressed. The longitudinal-message hook checks pedals but does not add a controls-allowed condition for those messages. The list is stale, while the acceptance is real baseline behavior needing review; it is not sufficient simply to expand the list and declare safety validated. |

## What was directly verified

The preserved compiled scratch checkout reports the original full SHA and no tracked source differences. The five-failure log predates this follow-up. Six new focused probes ran as fresh processes against the existing compiled baseline, with its source mounted read-only in a network-disabled, capability-dropped container. No new firmware, library or application build occurred.

The probes used both `chrysler_pacifica_2017_hybrid_generated` (inherited test DBC) and `chrysler_pacifica_2017_hybrid` (JVE production DBC). The observed button, forwarding, added-message and engagement results match between them. The production DBC has other JVE extensions, so this does not establish full DBC equivalence or overall port coverage.

For the engagement probes, the original packer/RX path accepted the simulated ACC, transmission and speed inputs. Observed state transitions, without writing internal safety globals:

| Simulated input condition | Controls allowed | Stored engagement |
|---|---:|---:|
| Fresh state, ACC active, no prior gear input | false | false |
| Forward gear, stationary, ACC inactive | true | true |
| Forward gear, moving, ACC inactive | false | false |
| Forward gear, moving, ACC active | true | true |

These are observations of an in-memory test library, not commands sent to a vehicle and not proof of safe longitudinal operation. No CAN payloads, vehicle wiring or activation procedure are part of this report.

## Environment and invocation issues separated

Earlier cache-directory, AGNOS I2C-header and generated-DBC omissions were build-recipe problems. They were corrected before the five-failure fresh-process run. The current failures are assertion mismatches, not import errors, missing DBC lookup, missing symbols or rejected simulated RX frames. The generated-versus-production DBC comparison does not change their explanations.

The combined 96-test family run had 21 failures. The recovered Chrysler initializer sets a static Ram-platform flag true for Ram modes without clearing it in the non-Ram branch. Fresh-process Pacifica execution removes eight additional steering-related failures seen after the Ram classes. This is a baseline reinitialization/test-order concern, not grounds to discard the remaining five. It may matter to safety-mode switching as well as test invocation; no claim is made about the fitted device's runtime transitions without inventory/replay evidence.

No full-family or full-target rebuild was repeated for this diagnosis. The separate Qualcomm model-generation blocker remains unchanged.

## Source evidence

- [Inherited Pacifica fixture, lists, helpers and button assertion](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/opendbc_repo/opendbc/safety/tests/test_chrysler.py#L11-L73).
- [Generic forwarding and spam assertions](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/opendbc_repo/opendbc/safety/tests/common.py#L717-L731), [generic cruise assertions](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/opendbc_repo/opendbc/safety/tests/common.py#L921-L937).
- [July gear/engagement path](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/opendbc_repo/opendbc/safety/safety/safety_chrysler.h#L81-L110), [TX and forwarding policy](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/opendbc_repo/opendbc/safety/safety/safety_chrysler.h#L187-L214), [production whitelist](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/opendbc_repo/opendbc/safety/safety/safety_chrysler.h#L268-L275), [platform initialization](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/opendbc_repo/opendbc/safety/safety/safety_chrysler.h#L311-L333).
- [Generic TX wrapper and forwarding routing](https://github.com/j-vanetten/openpilot/blob/b47add65d32e232b939d4915cca0b5a9ddafc48d/opendbc_repo/opendbc/safety/safety.h#L240-L292).

Raw observations are preserved in `safety-diagnostic-observations.jsonl`; the original failure log remains `pacifica-fresh-process-safety.log`.

## Consequence for step one

The recovered update endpoint can remain exact-source. These failures do not justify changing driving/safety behavior or suppressing tests/warnings to restore the endpoint. Conversely, recognizing fixture mismatches does not justify calling the release validated. Before reinstall, identify the actual installed firmware/source/local changes and determine whether preserving that exact installed state avoids introducing any firmware or policy change. Any future JVE-specific test work should add explicit, independently reviewed behavioral requirements and retain the original failing evidence. No such test rewrite or safety change was made here.

Existing device address/access and parked confirmation are still pending. Backup, complete target validation, compatibility review and the required deployment confirmation remain gates.
