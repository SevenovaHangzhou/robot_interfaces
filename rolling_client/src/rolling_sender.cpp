#include "robot_interfaces_rolling_client/rolling_sender.hpp"

#include "robot_interfaces_qos/profiles.hpp"

namespace robot_interfaces_rolling_client
{

RollingSender::RollingSender(rclcpp::Node & node, std::chrono::nanoseconds first_ack_timeout)
: stream_(first_ack_timeout)
{
  publisher_ = node.create_publisher<Batch>(kCommandTopic, robot_interfaces_qos::rolling_command());
  subscription_ = node.create_subscription<ControllerState>(
    kStateTopic, robot_interfaces_qos::rolling_state(),
    [this](const ControllerState & state) {
      std::lock_guard<std::mutex> lock(mutex_);
      stream_.onState(state, std::chrono::steady_clock::now());
    });
}

SendResult RollingSender::send(const Window & window)
{
  std::lock_guard<std::mutex> lock(mutex_);
  Batch batch;
  // Best-effort data reaches only matched readers; the first batch result confirms delivery.
  const bool reader_matched = publisher_->get_subscription_count() > 0U;
  const SendResult result =
    stream_.prepare(window, std::chrono::steady_clock::now(), reader_matched, batch);
  if (result == SendResult::kSent) {
    publisher_->publish(batch);
  }
  return result;
}

bool RollingSender::reset()
{
  std::lock_guard<std::mutex> lock(mutex_);
  return stream_.reset();
}

Status RollingSender::status() const
{
  std::lock_guard<std::mutex> lock(mutex_);
  return stream_.status();
}

}  // namespace robot_interfaces_rolling_client
