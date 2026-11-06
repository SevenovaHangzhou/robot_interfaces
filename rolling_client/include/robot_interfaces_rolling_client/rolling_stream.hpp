// Sender-side protocol state of one Rolling trajectory (M-09 batches, R-OUT-07 state).
//
// Pure logic without ROS communication: the caller supplies the controller state, the
// current steady time and whether the command reader is matched. RollingSender wraps it.
// Every decision follows a value reported by the controller; nothing is inferred from timing
// except the caller's own first-batch timeout.

#ifndef ROBOT_INTERFACES_ROLLING_CLIENT__ROLLING_STREAM_HPP_
#define ROBOT_INTERFACES_ROLLING_CLIENT__ROLLING_STREAM_HPP_

#include <chrono>
#include <cstdint>
#include <optional>

#include "builtin_interfaces/msg/time.hpp"
#include "robot_motion_interfaces/msg/rolling_joint_point.hpp"
#include "robot_motion_interfaces/msg/rolling_joint_target_batch.hpp"
#include "robot_rt_control_interfaces/msg/rolling_joint_control_state.hpp"

namespace robot_interfaces_rolling_client
{

using Batch = robot_motion_interfaces::msg::RollingJointTargetBatch;
using Point = robot_motion_interfaces::msg::RollingJointPoint;
using ControllerState = robot_rt_control_interfaces::msg::RollingJointControlState;
using SteadyTime = std::chrono::steady_clock::time_point;

/// R-OUT-07 max_age_ms. An older controller state is no evidence of an active controller.
inline constexpr std::chrono::milliseconds kStateMaxAge{200};

/// One future suffix of the planned trajectory: an M-09 batch without epoch and sequence.
struct Window
{
  builtin_interfaces::msg::Time replace_from;
  Batch::_points_type points;  // at most Batch::MAX_POINTS
  /// Last window of the trajectory; its last point must be at rest (M-09 final).
  bool final{false};
};

enum class Phase : std::uint8_t
{
  kIdle,            ///< No trajectory; the next send() starts one.
  kAwaitingAck,     ///< First batch published; waiting for its result.
  kStreaming,       ///< First batch accepted; the controller follows the trajectory.
  kCompleted,       ///< A final trajectory reached its end (STOP_COMPLETED).
  kStopped,         ///< The controller stopped the trajectory (Status::stop_reason).
  kRejected,        ///< The first batch was rejected (Status::last_rejection).
  kStartTimedOut,   ///< The first batch got no result within the first-batch timeout.
  kInterrupted,     ///< The epoch changed: mode switch, disable or controller reactivation.
};

enum class SendResult : std::uint8_t
{
  kSent,              ///< Published.
  kNotConnected,      ///< Not published: no fresh controller state or command reader unmatched.
  kControllerBusy,    ///< Not published: no trajectory of ours, but the controller is not HOLDING.
  kAwaitingFirstAck,  ///< Not published: the first batch has no result yet.
  kEnded,             ///< Not published: the trajectory ended; see status(), then reset().
};

struct Status
{
  Phase phase{Phase::kIdle};
  /// Latest R-OUT-07 state value (HOLDING, STARTING, RUNNING, STOPPING).
  std::uint8_t controller_state{ControllerState::HOLDING};
  std::uint32_t epoch{0U};
  /// Sequence of the accepted batch that started the trajectory; 0 before.
  std::uint64_t first_sequence{0U};
  std::uint64_t last_sent_sequence{0U};
  /// Rejections reported while streaming. The controller keeps its last accepted trajectory.
  std::uint32_t rejections{0U};
  /// R-OUT-07 last_result of the latest reported rejection, and its sequence.
  std::uint8_t last_rejection{ControllerState::ACCEPTED};
  std::uint64_t last_rejected_sequence{0U};
  /// R-OUT-07 stop_reason of this trajectory (kCompleted, kStopped).
  std::uint8_t stop_reason{ControllerState::STOP_NONE};
};

class RollingStream
{
public:
  /// first_ack_timeout: how long the first batch may stay without a result.
  explicit RollingStream(std::chrono::nanoseconds first_ack_timeout);

  void onState(const ControllerState & state, SteadyTime now);

  /// Returns kSent and fills batch when the window must be published now.
  SendResult prepare(const Window & window, SteadyTime now, bool reader_matched, Batch & batch);

  /// Clears an ended trajectory before the next one. False while a trajectory is active.
  bool reset();

  const Status & status() const noexcept {return status_;}

private:
  void checkFirstAckTimeout(SteadyTime now);
  void fill(const Window & window, Batch & batch);

  std::chrono::nanoseconds first_ack_timeout_;
  Status status_;
  std::optional<ControllerState> last_state_;
  SteadyTime last_state_time_{};
  SteadyTime first_sent_time_{};
};

}  // namespace robot_interfaces_rolling_client

#endif  // ROBOT_INTERFACES_ROLLING_CLIENT__ROLLING_STREAM_HPP_
