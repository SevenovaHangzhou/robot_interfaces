// Motion-side Rolling sender: publishes M-09 windows and follows R-OUT-07.
//
//   RollingSender sender(node, std::chrono::milliseconds(100));
//   // every planning cycle (M-09: 30 Hz); the last window has final = true
//   sender.send(window);       // SendResult says whether it was published
//   sender.status().phase;     // kStreaming, kCompleted, kStopped, kRejected, ...
//   sender.reset();            // after an ended trajectory, before the next one
//
// Thread safety: all calls and the state callback are serialized by one mutex.

#ifndef ROBOT_INTERFACES_ROLLING_CLIENT__ROLLING_SENDER_HPP_
#define ROBOT_INTERFACES_ROLLING_CLIENT__ROLLING_SENDER_HPP_

#include <chrono>
#include <mutex>

#include "rclcpp/rclcpp.hpp"
#include "robot_interfaces_rolling_client/rolling_stream.hpp"

namespace robot_interfaces_rolling_client
{

/// M-09 and R-OUT-07 ROS names.
inline constexpr char kCommandTopic[] = "/rt/arms/rolling/target_batch";
inline constexpr char kStateTopic[] = "/rt/arms/rolling/state";

class RollingSender
{
public:
  /// node must outlive the sender. first_ack_timeout: see RollingStream.
  RollingSender(rclcpp::Node & node, std::chrono::nanoseconds first_ack_timeout);

  SendResult send(const Window & window);
  bool reset();
  Status status() const;

private:
  mutable std::mutex mutex_;
  RollingStream stream_;
  rclcpp::Publisher<Batch>::SharedPtr publisher_;
  rclcpp::Subscription<ControllerState>::SharedPtr subscription_;
};

}  // namespace robot_interfaces_rolling_client

#endif  // ROBOT_INTERFACES_ROLLING_CLIENT__ROLLING_SENDER_HPP_
