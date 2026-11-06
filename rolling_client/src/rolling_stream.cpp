#include "robot_interfaces_rolling_client/rolling_stream.hpp"

#include <algorithm>
#include <stdexcept>

namespace robot_interfaces_rolling_client
{

RollingStream::RollingStream(std::chrono::nanoseconds first_ack_timeout)
: first_ack_timeout_(first_ack_timeout)
{
  if (first_ack_timeout_ <= std::chrono::nanoseconds::zero()) {
    throw std::invalid_argument("first_ack_timeout must be positive");
  }
}

void RollingStream::onState(const ControllerState & state, SteadyTime now)
{
  last_state_ = state;
  last_state_time_ = now;
  status_.controller_state = state.state;

  if (status_.phase != Phase::kAwaitingAck && status_.phase != Phase::kStreaming) {
    return;
  }
  if (state.epoch != status_.epoch) {
    status_.phase = Phase::kInterrupted;
    return;
  }

  if (status_.phase == Phase::kAwaitingAck) {
    if (state.last_sequence != status_.last_sent_sequence) {
      // A reported result counts even when it arrives late; only its absence times out.
      checkFirstAckTimeout(now);
      return;
    }
    if (state.last_result != ControllerState::ACCEPTED) {
      status_.phase = Phase::kRejected;
      status_.last_rejection = state.last_result;
      status_.last_rejected_sequence = state.last_sequence;
      return;
    }
    status_.phase = Phase::kStreaming;
    status_.first_sequence = state.last_sequence;
  } else if (
    state.last_result != ControllerState::ACCEPTED &&
    state.last_sequence != status_.last_rejected_sequence)
  {
    ++status_.rejections;
    status_.last_rejection = state.last_result;
    status_.last_rejected_sequence = state.last_sequence;
  }

  // R-OUT-07: stop_reason is STOP_NONE from the batch that started this trajectory until the
  // trajectory stops, so any other value is this trajectory's stop.
  if (state.stop_reason == ControllerState::STOP_COMPLETED) {
    status_.phase = Phase::kCompleted;
    status_.stop_reason = state.stop_reason;
  } else if (state.stop_reason != ControllerState::STOP_NONE) {
    status_.phase = Phase::kStopped;
    status_.stop_reason = state.stop_reason;
  }
}

SendResult RollingStream::prepare(
  const Window & window, SteadyTime now, bool reader_matched, Batch & batch)
{
  checkFirstAckTimeout(now);
  switch (status_.phase) {
    case Phase::kStreaming:
      fill(window, batch);
      return SendResult::kSent;
    case Phase::kAwaitingAck:
      return SendResult::kAwaitingFirstAck;
    case Phase::kIdle:
      break;
    default:
      return SendResult::kEnded;
  }
  const bool state_fresh = last_state_.has_value() && now - last_state_time_ <= kStateMaxAge;
  if (!state_fresh || !reader_matched) {
    return SendResult::kNotConnected;
  }
  if (last_state_->state != ControllerState::HOLDING) {
    return SendResult::kControllerBusy;
  }
  if (status_.epoch != last_state_->epoch) {
    // A new activation numbers its batches afresh.
    status_.epoch = last_state_->epoch;
    status_.last_sent_sequence = 0U;
  }
  status_.phase = Phase::kAwaitingAck;
  fill(window, batch);
  first_sent_time_ = now;
  return SendResult::kSent;
}

bool RollingStream::reset()
{
  if (status_.phase == Phase::kAwaitingAck || status_.phase == Phase::kStreaming) {
    return false;
  }
  Status cleared;
  // Sequences stay increasing within an epoch across trajectories.
  cleared.controller_state = status_.controller_state;
  cleared.epoch = status_.epoch;
  cleared.last_sent_sequence = status_.last_sent_sequence;
  status_ = cleared;
  return true;
}

void RollingStream::checkFirstAckTimeout(SteadyTime now)
{
  if (status_.phase == Phase::kAwaitingAck && now - first_sent_time_ >= first_ack_timeout_) {
    status_.phase = Phase::kStartTimedOut;
  }
}

void RollingStream::fill(const Window & window, Batch & batch)
{
  // The controller reports the newest sequence it received in this epoch.
  const std::uint64_t sequence =
    std::max(last_state_->last_sequence, status_.last_sent_sequence) + 1U;
  batch.epoch = status_.epoch;
  batch.sequence = sequence;
  batch.replace_from = window.replace_from;
  batch.points = window.points;
  batch.final = window.final;
  status_.last_sent_sequence = sequence;
}

}  // namespace robot_interfaces_rolling_client
