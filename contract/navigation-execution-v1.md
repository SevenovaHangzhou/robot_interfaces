# Navigation execution contract v1

Design authority: [robot_driver#334](https://github.com/SevenovaHangzhou/robot_driver/issues/334).
Endpoint registration and QoS authority: `endpoints.yaml` (N-07, R-OUT-30,
R-OUT-31, R-OUT-31C, R-OUT-32). This document defines their application schema.
This is our documented v1, not a reconstruction of unavailable navigation source;
no byte/index compatibility with that reference is claimed. All messages use ROS
standard types; there is no custom wrapper or changed robot model.

## Request, active state and lifecycle

Navigation is the `motion` domain for the command path, consistent with N-04.
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

`/rt/base/terminal_rotation_active` is `std_msgs/msg/Bool`, Q_FAST_STATE, 50 Hz.
True means the execution core actually accepted terminal rotation, including its
alignment phase; it is not an echo of the request and does not mean arrival or
stopping. Publish false when intent expires, execution is disabled/faulted, mode
is ineligible, or lifecycle is inactive while the publisher is alive. If the
publisher is absent consumers must treat state as unknown, never active. Consumer
freshness uses local receipt age <=300 ms, not ROS time. A true active value alone
is never permission to command motion.

## Execution array

`/rt/base/execution_state` and the explicitly requested compatibility endpoint
`/rt_control/chassis/execution_state` both publish `std_msgs/msg/Float64MultiArray`
at 100 Hz, Q_FAST_STATE. They publish the same coherent captured snapshot, with
identical layout/data/sequence/time; they are not independent measurements. A
consumer selects one endpoint, never fuses or counts both as independent evidence.

`data` contains exactly **91** doubles: 31 header fields and four 15-field module
blocks. `layout.data_offset=0`; `layout.dim` contains exactly one dimension with
`label="rt_base_execution_state_v1"`, `size=91`, `stride=91`. Reject unknown
versions, dimension labels, offsets, lengths, or out-of-range enum/boolean values.
All integer-valued fields are exactly representable doubles. Sequence starts at
zero per publisher process and increases once per captured snapshot; both aliases
share it. Restart resets sequence; consumers discard old continuity assumptions.
Sequence wraps to zero after 2^53-1. Neither sequence nor publication time proves
that hardware measurements are fresh.

All vectors are body-frame `base_footprint`, +x forward, +y left, +z up; positive
yaw is counterclockwise. SI units apply. Boolean fields are exactly 0 or 1.
Numeric values that are unavailable, stale, unsupported, or not applicable are
quiet NaN, never infinity or a plausible zero and never substituted with a
reference/command. Boolean validity is false when its prerequisites are invalid.
Enums retain their explicitly defined unavailable value. Consumers check validity
and finite values before use. Disabled constraints represented internally by
infinity are NaN on the wire; consumers must not treat that NaN as a finite limit
or as valid feedback. Disabled snapshots continue while the publisher is
alive; they must not claim ready or active. Receipt age >300 ms invalidates the
whole snapshot. Snapshot ROS time is publication/capture time, not an invented
hardware timestamp. No arrival/stopped decision may rely on this array alone.

### Header: absolute indexes

| Index | Name | Unit / meaning |
| --- | --- | --- |
| 0 | schema_version | Exactly 1 |
| 1 | sequence | Snapshot sequence, exact nonnegative integer |
| 2 | snapshot_ros_time | Seconds in ROS clock, NaN if unavailable |
| 3 | ready | Boolean: velocity execution eligible under mode/lifecycle/feedback/safety gates |
| 4 | status | CoreStatus enumeration below |
| 5 | gated | Boolean: drive output suppressed by steering alignment gate |
| 6 | waiting_for_alignment | Boolean: body shaper waiting for wheel alignment, not terminal-only |
| 7 | terminal_rotation_active | Boolean: same execution state as R-OUT-30 |
| 8 | terminal_request_fresh | Boolean: currently eligible true request with live lease |
| 9 | reference_vx | m/s |
| 10 | reference_vy | m/s |
| 11 | reference_wz | rad/s |
| 12 | reference_ax | m/s² |
| 13 | reference_ay | m/s² |
| 14 | reference_alpha | rad/s² |
| 15 | measured_vx | m/s, from actual feedback, not commanded motion |
| 16 | measured_vy | m/s, from actual feedback |
| 17 | measured_wz | rad/s, from actual feedback |
| 18 | max_translation_speed | m/s, effective body translation magnitude limit |
| 19 | max_yaw_speed | rad/s, effective absolute yaw speed limit |
| 20 | max_translation_acceleration | m/s², effective body translation magnitude limit |
| 21 | max_yaw_acceleration | rad/s², effective absolute yaw acceleration limit |
| 22 | max_steering_rate | rad/s, effective absolute steering rate limit |
| 23 | max_steering_acceleration | rad/s², effective absolute steering acceleration limit |
| 24 | max_steering_jerk | rad/s³, effective absolute steering jerk limit |
| 25 | max_wheel_speed | m/s, effective absolute wheel surface speed limit |
| 26 | max_wheel_acceleration | m/s², effective absolute wheel surface acceleration limit |
| 27 | max_body_jerk | m/s³, effective combined (vx, vy, wz*R) jerk norm limit; R is the execution core's configured body characteristic radius |
| 28 | enabled | Boolean: current execution enable state |
| 29 | feedback_valid | Boolean: all required module observations valid and fresh |
| 30 | command_fresh | Boolean: unchanged cmd_vel freshness predicate |

CoreStatus values: `0=inactive`, `1=running`, `2=alignment_gated`,
`3=command_timeout`, `4=feedback_fault`, `5=invalid_command`, `6=steering_limit`,
`7=steering_hold_fault`. These report the execution core's current status; they
are not control-mode codes and not a replacement for fault/enable interfaces.
Limits are the effective runtime limits after configuration, not model defaults
or illustrative constants. Body references are the execution core's limited
reference, not a separately reconstructed planner output.

### Modules: relative offsets

Module m (zero-based m=0..3) begins at `31 + 15*m`. Thus module1 is 31..45,
module2 46..60, module3 61..75, module4 76..90. Order is **physical wiring
module1..4 from the driver mapping**, not guessed FR/RR/FL/RL and not the
FL/FR/RL/RR order of wheel_observations. Existing driver mapping and calibration
remain authoritative and unchanged. x/y identify actual configured placement;
unknown geometry is NaN, never a guessed placement.

| Offset | Name | Unit / meaning |
| --- | --- | --- |
| 0 | actual_heading | rad, calibrated external encoder body heading θ |
| 1 | actual_wheel_speed | m/s, measured signed wheel surface speed |
| 2 | reference_heading | rad, current limited steering reference θ |
| 3 | reference_heading_rate | rad/s |
| 4 | reference_heading_acceleration | rad/s² |
| 5 | final_heading_target | rad, selected equivalent final target θ |
| 6 | heading_error | rad, final target minus actual heading in the selected bounded heading branch |
| 7 | branch | -1 reverse rolling branch, 0 unavailable, +1 forward rolling branch |
| 8 | effective_heading_min | rad, lower bound in θ coordinates |
| 9 | effective_heading_max | rad, upper bound in θ coordinates |
| 10 | wheel_radius | m, configured physical wheel radius |
| 11 | module_x | m, module center in body frame |
| 12 | module_y | m, module center in body frame |
| 13 | feedback_valid | Boolean: module steering and wheel observations valid and fresh |
| 14 | reference_wheel_speed | m/s, signed final limited/gated drive reference |

Heading is calibrated external encoder θ, not a raw count and not a motor
position substituted for an unavailable external encoder. It is the normalized
body heading corresponding to θ=-q for the existing model steering joint q.
All actual/reference/target/limit angles share this convention; do not wrap a
bounded angle independently into another branch. The equivalent reverse branch
changes rolling direction rather than changing module identity. Measured wheel
surface speed is measured wheel angular speed times the configured radius;
invalid radius makes this numeric result NaN. Feedback validity is not inferred
from successful command publication.

## Normalized JointState compatibility output

`/rt_control/chassis/joint_states` publishes `sensor_msgs/msg/JointState` at
100 Hz with Q_FAST_STATE from the same captured snapshot. `header.frame_id` is
`base_footprint`; `header.stamp` is the same ROS snapshot time. `name` is exactly
`[module_1_steering, module_1_wheel, module_2_steering, module_2_wheel,
module_3_steering, module_3_wheel, module_4_steering, module_4_wheel]`.
Both position and velocity have eight entries in this interleaved physical wiring
module order; effort is empty. Steering positions are calibrated external encoder
θ=-q radians. Steering velocities are NaN because measured steering rate is not
available. Wheel positions are actual wheel radians and wheel velocities
actual signed rad/s, **not** the execution array's m/s. Individual unsupported or
invalid numeric entries are NaN; never synthesize wheel position by integrating
commands. Consumer receipt freshness is <=300 ms.

This topic uses neutral module names for navigation-normalized feedback. It
must not feed robot_state_publisher, overwrite `/joint_states`, or redefine URDF
joint signs. No robot_description, physical wiring, motor mapping, geometry,
calibration, existing `/rt/base/wheel_observations`, cmd_vel, or odom behavior is
changed. Existing wheel_observations retains its separate identity/order and
sample provenance. Neither compatibility output creates a second hardware source.

## Compatibility and release

These are additive endpoints. RT-Control, Motion/Navigation, and Autonomy
consumers upgrade to one reviewed robot_interfaces SHA in the same release
window; do not pin unpublished work or mix schema versions. Review is shared by
RT-Control and the consuming domains. Release interface authority first, then
producer/consumer changes together, then cross-domain smoke checks before any
separately authorized deployment. Rollback returns all affected domains to their
previous coordinated SHAs and removes use of the new endpoints; never translate
unknown old 91-field indexes by assumption. No pending model or hardware-mapping
change is implicitly merged by this contract.
