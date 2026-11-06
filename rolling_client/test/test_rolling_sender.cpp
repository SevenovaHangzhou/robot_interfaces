#include <gtest/gtest.h>

#include <chrono>
#include <functional>
#include <memory>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "robot_interfaces_qos/profiles.hpp"
#include "robot_interfaces_rolling_client/rolling_sender.hpp"

namespace robot_interfaces_rolling_client
{
namespace
{

using namespace std::chrono_literals;

class RollingSenderTest : public ::testing::Test
{
protected:
  static void SetUpTestSuite() {rclcpp::init(0, nullptr);}
  static void TearDownTestSuite() {rclcpp::shutdown();}

  void SetUp() override
  {
    motion_ = std::make_shared<rclcpp::Node>("rolling_sender_test_motion");
    controller_ = std::make_shared<rclcpp::Node>("rolling_sender_test_controller");
    executor_.add_node(motion_);
    executor_.add_node(controller_);
  }

  /// Spins both nodes, running step each round, until done() or the timeout.
  bool spinUntil(const std::function<bool()> & done, const std::function<void()> & step = {})
  {
    const auto deadline = std::chrono::steady_clock::now() + 5s;
    while (std::chrono::steady_clock::now() < deadline) {
      if (step) {
        step();
      }
      executor_.spin_some(10ms);
      if (done()) {
        return true;
      }
    }
    return false;
  }

  void publishState(std::uint8_t state, std::uint64_t last_sequence)
  {
    ControllerState message;
    message.epoch = 3U;
    message.state = state;
    message.last_sequence = last_sequence;
    message.last_result = ControllerState::ACCEPTED;
    state_publisher_->publish(message);
  }

  Window window()
  {
    Window result;
    result.replace_from = motion_->now() + rclcpp::Duration(50ms);
    Point point;
    point.positions.fill(0.0);
    point.velocities.fill(0.0);
    result.points.push_back(point);
    return result;
  }

  rclcpp::Node::SharedPtr motion_;
  rclcpp::Node::SharedPtr controller_;
  rclcpp::executors::SingleThreadedExecutor executor_;
  rclcpp::Publisher<ControllerState>::SharedPtr state_publisher_;
};

TEST_F(RollingSenderTest, FirstBatchWaitsForTheControllerAndStartsTheStream)
{
  RollingSender sender(*motion_, 100ms);
  EXPECT_EQ(sender.send(window()), SendResult::kNotConnected);

  state_publisher_ = controller_->create_publisher<ControllerState>(
    kStateTopic, robot_interfaces_qos::rolling_state());
  std::vector<Batch> received;
  auto reader = controller_->create_subscription<Batch>(
    kCommandTopic, robot_interfaces_qos::rolling_command(),
    [&received](const Batch & batch) {received.push_back(batch);});

  SendResult result = SendResult::kNotConnected;
  ASSERT_TRUE(
    spinUntil(
      [&result] {return result == SendResult::kSent;},
      [&] {
        publishState(ControllerState::HOLDING, 0U);
        result = sender.send(window());
      }));
  ASSERT_TRUE(spinUntil([&received] {return !received.empty();}));
  EXPECT_EQ(received.size(), 1U);
  EXPECT_EQ(received.front().epoch, 3U);
  EXPECT_EQ(received.front().sequence, 1U);

  ASSERT_TRUE(
    spinUntil(
      [&sender] {return sender.status().phase == Phase::kStreaming;},
      [this] {publishState(ControllerState::STARTING, 1U);}));
  EXPECT_EQ(sender.status().first_sequence, 1U);
}

}  // namespace
}  // namespace robot_interfaces_rolling_client
