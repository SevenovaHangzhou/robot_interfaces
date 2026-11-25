# Navigation execution contract v1

Design authority: [robot_driver#334](https://github.com/SevenovaHangzhou/robot_driver/issues/334).
Correction decision: [robot_driver#339](https://github.com/SevenovaHangzhou/robot_driver/issues/339).
Endpoint registration and QoS authority: `endpoints.yaml` (N-07, R-OUT-30,
R-OUT-31, R-OUT-31C, R-OUT-32). This document defines their application schema.
This v1 is the existing published Navigation v3.0.4 / simulation v.1.0 protocol,
27 header fields plus four 16-field modules. PR24's undeployed conflicting
31+4×15 interpretation is withdrawn by explicit user decision; see release below.

## Request, active state and lifecycle

Navigation provides the request on the command path, consistent with N-04.
`/rt/base/terminal_rotation_request` is `std_msgs/msg/Bool`, Q_CONTROL, 50 Hz.
It is intent only, not enable authority, a velocity command, an arrival result,
or a bypass of normal velocity/feedback/mode/safety gates. Exactly one Navigation
writer is permitted. A true sample received while eligible renews a lease measured
using the receiving controller's local monotonic clock: fresh at age <=300 ms,
expired at age >300 ms. False clears on the next core tick without waiting for
lease expiry. ROS time changes never renew or
extend the lease; Bool has no sender timestamp. Delivery delays are not measured
as sender age and must not be represented as such.

Inactive lifecycle, disable, fault, and leaving VELOCITY_READY invalidate intent.
Requests received while ineligible must not arm a later transition. Re-enable,
reactivation, or return from FJT requires a new true sample; never latch, replay,
or restore old intent. Expiry/false releases terminal intent and its alignment
state, but does not independently refresh or override the unchanged cmd_vel
watchdog. Acceptance requires a fresh cmd_vel and all ordinary safety conditions.

`/rt/base/terminal_rotation_active` is `std_msgs/msg/Bool`, Q_CONTROL, 50 Hz
(reliable, volatile, depth 1, compatible with Navigation's reliable subscriber).
True means the execution core granted terminal rotation, never an echo or arrival.
First admission requires a fresh zero vx/vy/wz command, valid feedback, active
fault-free execution, every measured wheel speed <=0.01 m/s, and zero drive
output continuously for 0.05 s. The 300 ms lease is not an admission delay.
Once granted, rotating wheels do not trigger repeated standstill admission.
Translation intent, false/expired request, invalid feedback, fault, disable or
inactive lifecycle revoke authority; reactivation requires a new request.
Publish false while the publisher is alive when unavailable; absence is unknown.
Consumer receipt freshness is <=300 ms. Authorized pure rotation permits
1.5 rad/s and 1.5 rad/s²; ordinary motion permits 0.8 rad/s and π/8 rad/s².
Normal revocation uses controlled braking before translation, not a velocity
jump; emergency safety stopping remains authoritative.

## Execution array

`/rt/base/execution_state` and the explicitly requested compatibility endpoint
`/rt_control/chassis/execution_state` both publish `std_msgs/msg/Float64MultiArray`
at 100 Hz, Q_FAST_STATE. They publish the same coherent captured snapshot, with
identical layout/data/sequence/time; they are not independent measurements. A
consumer selects one endpoint, never fuses or counts both as independent evidence.

`data` contains exactly **91** doubles: **27** header fields and four **16**-field
module blocks. `layout.data_offset=0`; one dimension uses
`label="rt_base_execution_state_v1"`, `size=91`, `stride=91`. The released
consumer decodes data indexes, not layout labels: changing a label cannot
disambiguate the withdrawn conflicting layout. Machine-readable indexes and
acceptance policy are registered under `navigation_execution_v1` in endpoints.yaml.
Sequence is an exactly representable nonnegative integer (0..2^53-1), advances
once per captured snapshot and is identical on both aliases. Restart/wrap resets
continuity; neither sequence nor publication time proves hardware freshness.

An accepted snapshot requires ready=1, status in {1,2,3}, and **all 91 values
finite**. Boolean values are exactly 0 or 1. Snapshot ROS age must be <=0.1 s
and future offset <=0.01 s; accepted stamps must advance. ROS time, not local
monotonic lease time, is transmitted. All parties use the same ROS clock.
Ready means active, fresh valid feedback and no execution-blocking latched fault.
Status 3 permits state recovery but never overrides the command watchdog.
Feedback failure must protect/stop and invalidate ready. Unknown or stale values
remain quiet NaN, never zero, command/reference substitutions or stale samples
restamped to appear fresh. A ready=0 or nonfinite snapshot is intentionally
rejected. Active=false and ready=false are different states.

Vectors use body-frame base_footprint, +x forward, +y left, +z up, positive yaw
counterclockwise. SI units apply. Capture once at the control update consistency
boundary and publish that snapshot on both aliases; no unsynchronized reads of
mutating real-time state. No stopped/arrival decision relies on this array alone.

### Header: absolute indexes

| Index | Name | Unit / meaning |
| --- | --- | --- |
| 0 | schema_version | Exactly 1 |
| 1 | snapshot_ros_time | s, ROS snapshot timestamp |
| 2 | sequence | Exact nonnegative integer |
| 3 | ready | Boolean: active, feedback valid, no blocking latched fault |
| 4 | status | CoreStatus enumeration below |
| 5 | gated | Boolean, actual core steering gate |
| 6 | waiting_for_alignment | Boolean, actual body alignment waiting state |
| 7 | translation_branch | -1 unset, 0 forward, 1 reversed; whole-translation lock |
| 8 | reference_vx | m/s, internal shaped reference |
| 9 | reference_vy | m/s |
| 10 | reference_wz | rad/s, restore angular axis from R*wz |
| 11 | reference_ax | m/s² |
| 12 | reference_ay | m/s² |
| 13 | reference_alpha | rad/s², restore angular axis from equivalent radius |
| 14 | measured_vx | m/s, actual feedback solution |
| 15 | measured_vy | m/s |
| 16 | measured_wz | rad/s |
| 17 | max_steering_rate | rad/s, π/2 |
| 18 | max_steering_acceleration | rad/s², π |
| 19 | max_steering_jerk | rad/s³, 1.7453292519943295 |
| 20 | max_translation_acceleration | m/s², 1.0 |
| 21 | max_body_jerk | Core shaping parameter 4.0; angular axis uses core equivalent radius |
| 22 | max_wheel_acceleration | m/s², 2.0 |
| 23 | max_wheel_speed | m/s, 2.0 |
| 24 | gate | rad, effective gate threshold, continuous mode π/2 |
| 25 | release | rad, effective release threshold, continuous mode π/2 |
| 26 | flip_hysteresis | rad, π/60 |

CoreStatus values: `0=inactive`, `1=running`, `2=alignment_gated`,
`3=command_timeout`, `4=feedback_fault`, `5=invalid_command`, `6=steering_limit`,
`7=steering_hold_fault`. These report the execution core's current status; they
are not control-mode codes and not a replacement for fault/enable interfaces.
Limits are the effective runtime limits after configuration, not model defaults
or illustrative constants. Body references are the execution core's limited
reference, not a separately reconstructed planner output.

### Modules: relative offsets

Module m (zero-based m=0..3) begins at `27 + 16*m`: blocks 27..42,
43..58, 59..74, 75..90. Each carries a unique physical module ID in {1,2,3,4}.
Consumers match by ID and accept valid block reordering; duplicate/missing IDs
are invalid. Preferred order is physical wiring module1..4 from our driver
mapping, not guessed FR/RR/FL/RL and not wheel_observations order.
Our hardware, model, geometry and calibration remain authoritative. Handoff
mapping examples must not overwrite them. Publish real effective x/y/radius and
limits; unknown geometry is NaN, not a guessed value to satisfy the parser.

| Offset | Name | Unit / meaning |
| --- | --- | --- |
| 0 | module_id | Integer physical identity 1..4 |
| 1 | actual_heading | rad, motor-derived normalized measured control-axis heading (module.steering_actual), matching the executing core's prediction seed |
| 2 | actual_wheel_speed | m/s, actual signed wheel surface speed |
| 3 | reference_heading | rad, limited steering trajectory |
| 4 | reference_heading_rate | rad/s, reference not measured rate |
| 5 | reference_heading_acceleration | rad/s² |
| 6 | reference_wheel_speed | m/s, actual core limited/gated wheel reference |
| 7 | reversed | Boolean, selected equivalent reversed rolling branch |
| 8 | holding | Boolean, actual per-module internal holding state |
| 9 | final_heading_target | rad, branch-selected goal before steering shaping |
| 10 | heading_error | rad, actual selected goal.error_rad: goal minus safe-clamped motor steering_position, not external encoder angle |
| 11 | effective_heading_min | rad, effective lower bound |
| 12 | effective_heading_max | rad, effective upper bound |
| 13 | wheel_radius | m, actual configured radius |
| 14 | module_x | m, actual module center in body frame |
| 15 | module_y | m, actual module center in body frame |

Holding cannot be inferred from zero wheel speed. TranslationBranch cannot be
inferred from individual Reversed flags. Goal and ReferenceAngle must remain
distinct. Gate/Release/FlipHysteresis come from the executing core, not nominal
configuration. Continuous mode uses π/2 gate/release and cosine compensation
max(0, cos(goal-actual)); explicit align-first mode may use 5°/3° and is not
selected during ordinary navigation. The published consumer checks effective
limits and geometry with absolute tolerance 1e-5. Its reference setup uses
±120° effective steering limits and 0.1 m wheels. Report any actual geometry,
mapping or limit incompatibility for joint configuration review; never hide it
with fabricated values. Numeric layout compatibility alone does not prove
prediction equivalence: replay the same feedback, initial state, commands, dt
and authorization through driver and released predictor, comparing every step's
body reference, goal/reference angles/rates/accelerations, wheel reference,
branches, Holding and gates. Preserve safety and report incompatible semantics.

Execution-array heading is the motor-derived measured control-axis θ used by the
executing core, not a command or reference. JointState steering instead uses the
calibrated external encoder; neither path substitutes for an invalid other path.
Both use normalized body heading corresponding to θ=-q for the existing model.
All actual/reference/target/limit angles share this convention; do not wrap a
bounded angle independently into another branch. The equivalent reverse branch
changes rolling direction rather than changing module identity. Measured wheel
surface speed is measured wheel angular speed times the configured radius;
invalid radius makes this numeric result NaN. Feedback validity is not inferred
from successful command publication.

## Normalized JointState compatibility output

`/rt_control/chassis/joint_states` publishes `sensor_msgs/msg/JointState` at
100 Hz with Q_FAST_STATE from the same captured snapshot. `header.frame_id` is
`base_footprint`; `header.stamp` is the same ROS snapshot time. Preferred `name` order is
`[module_1_steering, module_1_wheel, module_2_steering, module_2_wheel,
module_3_steering, module_3_wheel, module_4_steering, module_4_wheel]`.
Both position and velocity have eight entries matched by name (valid reorderings
are accepted); effort is empty. Steering positions are measured normalized θ,
using our authoritative model conversion. Steering velocity is a valid hardware
measurement, or an observation from at least two consecutive fresh actual encoder
samples: (theta_k-theta_prev)/(sample_time_k-sample_time_prev). Use an advancing
hardware sequence and sample timestamp when available. Current hw_canopen exposes
position, feedback_age_ms and ready, not a device sequence or timestamp. Its
supported host-receive observer identifies a new sample by a strict receive-age
fall, observed at 1 kHz against 4 ms SYNC, and reconstructs local monotonic receive
time from observation time minus receive age. This is host reception provenance,
not device sampling time; never invent a hardware sequence or device timestamp.
Require advancing reconstructed receive time and a reasonable interval. Repeated
cached observations are not samples and must not enter the difference calculation.
Unchanged or rising ages never trigger differentiation, and an existing rate
ages out. Reject out-of-bounds angles and implausible jumps exceeding the maximum
steering slew times receive interval plus the configured angular tolerance.
Age quantization, missed updates and receive-age resets can make continuity
ambiguous: invalidate/reset history rather than claiming distinct hardware samples.
This observer cannot identify hidden device resets or prove device-time sampling;
retain that limitation in integration evidence. Explicit reset, activation,
dropout, clock reversal and calibration/mapping changes clear history. Until two
valid observations establish continuity, publish NaN, never fallback 0, command
rate or reference rate. Conversion must preserve the physical bounded branch
(unwrap raw encoders before conversion where required). Any filter requires
measured latency proving moving steering cannot appear stopped.

The array's actual_heading uses module.steering_actual, the motor-derived measured
control-axis state used for prediction initialization. Its heading_error is the
production generator's selected goal.error_rad, computed from the goal and
safe-clamped motor steering_position. JointState position/rate instead use the
external calibrated encoder and the receive observer above. Do not recompute the
array error from the external angle or assume it always equals goal minus the
unclamped array angle. Preserve core control/safety behavior and disclose these
observation and clamp distinctions in predictor replay.

Wheel position is measured radians; wheel velocity is measured signed rad/s,
**not** execution-array m/s. Unknown entries stay NaN; do not integrate commands
to fabricate position. Current stopped checks require positive ROS stamps,
age <=0.2 s and future offset <=0.05 s for odom and JointState, odom child frame
base_footprint, body translation/yaw <=0.008 m/s and <=0.008 rad/s, each wheel
<=0.08 rad/s and each steering rate <=0.01 rad/s, with finite steering angles.
The stopped window is continuous 0.2 s, timeout 8 s. These are consumer checks,
not extra admission delays on every ordinary command.

This topic uses neutral module names for navigation-normalized feedback. It
must not feed robot_state_publisher, overwrite `/joint_states`, or redefine URDF
joint signs. No robot_description, physical wiring, motor mapping, geometry,
calibration, existing `/rt/base/wheel_observations`, cmd_vel, or odom behavior is
changed. Existing wheel_observations retains its separate identity/order and
sample provenance. Neither compatibility output creates a second hardware source.

## Compatibility and release

The user explicitly confirmed that no running downstream consumers adopted
PR24's 31+4×15 layout and approved withdrawing it as an **undeployed invalid
contract**, despite PR24 being merged. Thus this correction retains v1 and 91
fields to match the already published Navigation v3.0.4
(`3f09209babca43a716d842f58fe30a5e1fbe48a2`) and simulation v.1.0
(`e48feba61073c02bec666f052e55f1fc547257cf`), which remain unchanged.
This is not permission to reinterpret a deployed schema or mix publishers.
If any consumer of the withdrawn layout is discovered, stop rollout and arrange
a separately identified migration; never alternate layouts on the same topic.

RT-Control, Navigation and Autonomy review the corrected interface SHA; driver
PR336 pins that reviewed SHA. Release the correction first, then integrate the
producer against unchanged published consumers with actual parser/stopped-check
tests and stepwise predictor replay; verify DDS QoS (SensorDataQoS consumers for
execution/JointState, reliable consumer for rotation_active). One publisher per
endpoint, both execution aliases from one snapshot. No hardware deployment is
authorized here. Rollback removes this adaptation and restores the last approved
**pre-adaptation** driver/interface combination, stopping use of the new outputs;
never roll back to PR24's conflicting 31+4×15 layout or revert unrelated user
changes on main. Preserve the independent Navigation domain and all existing
hardware/model/calibration ownership. Cross-domain and hardware smoke acceptance
remain separate from offline contract tests.
