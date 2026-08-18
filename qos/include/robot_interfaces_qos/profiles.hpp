// 跨域通信的命名 QoS 剖面。
//
// 跨域通信只使用本文件提供的剖面，不得逐条自定义。
// 数值与 contract/endpoints.yaml 的 qos_profiles 一致。

#ifndef ROBOT_INTERFACES_QOS__PROFILES_HPP_
#define ROBOT_INTERFACES_QOS__PROFILES_HPP_

#include <chrono>

#include "rclcpp/qos.hpp"

namespace robot_interfaces_qos
{

/// 周期控制命令（/cmd_vel_safe）。
///
/// deadline 与 lifespan 均为 500 ms，与 RT-Control 的 500 ms 本地接收间隔
/// 看门狗一致。两者必须同步修改：lifespan 短于看门狗会让消息在看门狗
/// 到期前先被 DDS 丢弃。
inline rclcpp::QoS control()
{
  rclcpp::QoS qos{rclcpp::KeepLast(1)};
  qos.reliable();
  qos.durability_volatile();
  qos.deadline(std::chrono::milliseconds(500));
  qos.lifespan(std::chrono::milliseconds(500));
  return qos;
}

/// ELECTRI-102 rolling joint future-suffix command.
///
/// A newer self-contained suffix supersedes an older one. Reliable replay of
/// an expired suffix is less useful than keeping only the newest sample.
inline rclcpp::QoS rolling_command()
{
  rclcpp::QoS qos{rclcpp::KeepLast(1)};
  qos.best_effort();
  qos.durability_volatile();
  qos.deadline(std::chrono::milliseconds(100));
  qos.lifespan(std::chrono::milliseconds(100));
  return qos;
}

/// ELECTRI-102 rolling joint acknowledgement and controller state.
inline rclcpp::QoS rolling_state()
{
  rclcpp::QoS qos{rclcpp::KeepLast(5)};
  qos.reliable();
  qos.durability_volatile();
  qos.deadline(std::chrono::milliseconds(100));
  qos.lifespan(std::chrono::milliseconds(200));
  return qos;
}

/// 高频状态（/joint_states 125 Hz、/odom、/wheel/odom 50 Hz）。
inline rclcpp::QoS fast_state()
{
  rclcpp::QoS qos{rclcpp::KeepLast(5)};
  qos.reliable();
  qos.durability_volatile();
  return qos;
}

/// 中频状态（/vacuum/state、/control/safety_state）。
inline rclcpp::QoS state()
{
  rclcpp::QoS qos{rclcpp::KeepLast(5)};
  qos.reliable();
  qos.durability_volatile();
  return qos;
}

/// 版本与就绪基线（readiness、/robot_model/info、/calibration/info、
/// /map、N-03）。晚加入的订阅者需要立即拿到最后一条。
inline rclcpp::QoS latched()
{
  rclcpp::QoS qos{rclcpp::KeepLast(1)};
  qos.reliable();
  qos.transient_local();
  return qos;
}

/// /diagnostics。
inline rclcpp::QoS diagnostic()
{
  rclcpp::QoS qos{rclcpp::KeepLast(10)};
  qos.reliable();
  qos.durability_volatile();
  return qos;
}

}  // namespace robot_interfaces_qos

#endif  // ROBOT_INTERFACES_QOS__PROFILES_HPP_
