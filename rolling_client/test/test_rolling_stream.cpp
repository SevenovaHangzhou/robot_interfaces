#include <gtest/gtest.h>

#include <chrono>
#include <cstdint>

#include "robot_interfaces_rolling_client/rolling_stream.hpp"

namespace robot_interfaces_rolling_client
{
namespace
{

using std::chrono::milliseconds;
constexpr milliseconds kAckTimeout{100};
constexpr std::uint32_t kEpoch = 3U;

ControllerState report(
  std::uint8_t state, std::uint32_t epoch, std::uint64_t sequence,
  std::uint8_t result = ControllerState::ACCEPTED,
  std::uint8_t stop_reason = ControllerState::STOP_NONE)
{
  ControllerState message;
  message.state = state;
  message.epoch = epoch;
  message.last_sequence = sequence;
  message.last_result = result;
  message.stop_reason = stop_reason;
  return message;
}

Window window(bool final = false)
{
  Window result;
  result.replace_from.sec = 1000;
  result.points.resize(2U);
  result.points[1].time_from_start.nanosec = 200000000U;
  result.final = final;
  return result;
}

class RollingStreamTest : public ::testing::Test
{
protected:
  void controller(const ControllerState & state) {stream_.onState(state, now_);}
  SendResult send(const Window & content = window(), bool reader_matched = true)
  {
    return stream_.prepare(content, now_, reader_matched, batch_);
  }
  const Status & status() const {return stream_.status();}

  void startStreaming()
  {
    controller(report(ControllerState::HOLDING, kEpoch, 7U));
    ASSERT_EQ(send(), SendResult::kSent);
    controller(report(ControllerState::STARTING, kEpoch, batch_.sequence));
    ASSERT_EQ(status().phase, Phase::kStreaming);
  }

  RollingStream stream_{kAckTimeout};
  Batch batch_;
  SteadyTime now_{std::chrono::seconds(1000)};
};

TEST_F(RollingStreamTest, StartWaitsForFreshStateAndMatchedReader)
{
  EXPECT_EQ(send(), SendResult::kNotConnected);

  controller(report(ControllerState::HOLDING, kEpoch, 7U));
  EXPECT_EQ(send(window(), false), SendResult::kNotConnected);

  now_ += kStateMaxAge + milliseconds(1);
  EXPECT_EQ(send(), SendResult::kNotConnected);
  EXPECT_EQ(status().phase, Phase::kIdle);
}

TEST_F(RollingStreamTest, FirstBatchUsesControllerEpochAndNextSequence)
{
  controller(report(ControllerState::HOLDING, kEpoch, 7U));

  ASSERT_EQ(send(window(true)), SendResult::kSent);

  EXPECT_EQ(batch_.epoch, kEpoch);
  EXPECT_EQ(batch_.sequence, 8U);
  EXPECT_TRUE(batch_.final);
  EXPECT_EQ(status().phase, Phase::kAwaitingAck);
}

TEST_F(RollingStreamTest, WindowsWaitForTheFirstBatchResult)
{
  controller(report(ControllerState::HOLDING, kEpoch, 7U));
  ASSERT_EQ(send(), SendResult::kSent);

  EXPECT_EQ(send(), SendResult::kAwaitingFirstAck);

  controller(report(ControllerState::STARTING, kEpoch, 8U));
  EXPECT_EQ(status().phase, Phase::kStreaming);
  EXPECT_EQ(status().first_sequence, 8U);
  EXPECT_EQ(status().controller_state, ControllerState::STARTING);
  ASSERT_EQ(send(), SendResult::kSent);
  EXPECT_EQ(batch_.sequence, 9U);
}

TEST_F(RollingStreamTest, FirstBatchWithoutResultTimesOut)
{
  controller(report(ControllerState::HOLDING, kEpoch, 7U));
  ASSERT_EQ(send(), SendResult::kSent);
  now_ += kAckTimeout;

  EXPECT_EQ(send(), SendResult::kEnded);
  EXPECT_EQ(status().phase, Phase::kStartTimedOut);

  ASSERT_TRUE(stream_.reset());
  controller(report(ControllerState::HOLDING, kEpoch, 7U));
  ASSERT_EQ(send(), SendResult::kSent);
  EXPECT_EQ(batch_.sequence, 9U);
}

TEST_F(RollingStreamTest, LateReportedResultStillCounts)
{
  controller(report(ControllerState::HOLDING, kEpoch, 7U));
  ASSERT_EQ(send(), SendResult::kSent);
  now_ += kAckTimeout;

  controller(report(ControllerState::RUNNING, kEpoch, 8U));

  EXPECT_EQ(status().phase, Phase::kStreaming);
}

TEST_F(RollingStreamTest, RejectedFirstBatchEndsTheTrajectory)
{
  controller(report(ControllerState::HOLDING, kEpoch, 7U));
  ASSERT_EQ(send(window(true)), SendResult::kSent);

  controller(report(ControllerState::HOLDING, kEpoch, 8U, ControllerState::FINAL_NOT_AT_REST));

  EXPECT_EQ(status().phase, Phase::kRejected);
  EXPECT_EQ(status().last_rejection, ControllerState::FINAL_NOT_AT_REST);
  EXPECT_EQ(send(), SendResult::kEnded);
}

TEST_F(RollingStreamTest, IdleSenderDoesNotJoinAnotherTrajectory)
{
  controller(report(ControllerState::STARTING, kEpoch, 7U));
  EXPECT_EQ(send(), SendResult::kControllerBusy);

  controller(report(ControllerState::RUNNING, kEpoch, 7U));
  EXPECT_EQ(send(), SendResult::kControllerBusy);
}

TEST_F(RollingStreamTest, FinalTrajectoryCompletes)
{
  startStreaming();
  ASSERT_EQ(send(window(true)), SendResult::kSent);
  controller(report(ControllerState::RUNNING, kEpoch, batch_.sequence));
  EXPECT_EQ(status().phase, Phase::kStreaming);

  controller(
    report(
      ControllerState::HOLDING, kEpoch, batch_.sequence, ControllerState::ACCEPTED,
      ControllerState::STOP_COMPLETED));

  EXPECT_EQ(status().phase, Phase::kCompleted);
  EXPECT_EQ(status().stop_reason, ControllerState::STOP_COMPLETED);
}

TEST_F(RollingStreamTest, ShortFinalTrajectoryCanCompleteInItsFirstResult)
{
  controller(report(ControllerState::HOLDING, kEpoch, 7U));
  ASSERT_EQ(send(window(true)), SendResult::kSent);

  controller(
    report(
      ControllerState::HOLDING, kEpoch, 8U, ControllerState::ACCEPTED,
      ControllerState::STOP_COMPLETED));

  EXPECT_EQ(status().phase, Phase::kCompleted);
  EXPECT_EQ(status().first_sequence, 8U);
}

TEST_F(RollingStreamTest, StopIsReportedWithItsReason)
{
  startStreaming();

  controller(
    report(
      ControllerState::STOPPING, kEpoch, batch_.sequence, ControllerState::ACCEPTED,
      ControllerState::STOP_UPDATE_TIMEOUT));

  EXPECT_EQ(status().phase, Phase::kStopped);
  EXPECT_EQ(status().stop_reason, ControllerState::STOP_UPDATE_TIMEOUT);
  EXPECT_EQ(status().controller_state, ControllerState::STOPPING);
  EXPECT_EQ(send(), SendResult::kEnded);
}

TEST_F(RollingStreamTest, RejectionWhileStreamingIsCountedOnceAndStreamingContinues)
{
  startStreaming();
  ASSERT_EQ(send(), SendResult::kSent);
  const auto rejected = batch_.sequence;

  const auto message =
    report(ControllerState::RUNNING, kEpoch, rejected, ControllerState::LIMIT_EXCEEDED);
  controller(message);
  controller(message);

  EXPECT_EQ(status().phase, Phase::kStreaming);
  EXPECT_EQ(status().rejections, 1U);
  EXPECT_EQ(status().last_rejected_sequence, rejected);
  EXPECT_EQ(send(), SendResult::kSent);
}

TEST_F(RollingStreamTest, EpochChangeInterruptsAndRenumbers)
{
  startStreaming();

  controller(report(ControllerState::HOLDING, kEpoch + 1U, 0U));

  EXPECT_EQ(status().phase, Phase::kInterrupted);
  ASSERT_TRUE(stream_.reset());
  ASSERT_EQ(send(), SendResult::kSent);
  EXPECT_EQ(batch_.epoch, kEpoch + 1U);
  EXPECT_EQ(batch_.sequence, 1U);
}

TEST_F(RollingStreamTest, ActiveTrajectoryCannotBeReset)
{
  controller(report(ControllerState::HOLDING, kEpoch, 7U));
  ASSERT_EQ(send(), SendResult::kSent);
  EXPECT_FALSE(stream_.reset());

  controller(report(ControllerState::STARTING, kEpoch, 8U));
  EXPECT_FALSE(stream_.reset());
}

TEST(RollingStreamConstruction, RejectsNonPositiveAckTimeout)
{
  EXPECT_THROW(RollingStream(std::chrono::nanoseconds::zero()), std::invalid_argument);
}

}  // namespace
}  // namespace robot_interfaces_rolling_client
