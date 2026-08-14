"""跨域通信的命名 QoS 剖面（Python）。

跨域通信只使用本模块提供的剖面，不得逐条自定义。
数值与 profiles.hpp 及 contract/endpoints.yaml 保持一致。
"""

from rclpy.duration import Duration
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

__all__ = ["control", "fast_state", "state", "latched", "diagnostic"]

# /cmd_vel_safe 的看门狗间隔。与 profiles.hpp 及 RT-Control 实现同源。
CMD_VEL_WATCHDOG_MS = 500


def control() -> QoSProfile:
    """周期控制命令（/cmd_vel_safe）。

    deadline 与 lifespan 均为 500 ms，与 RT-Control 的 500 ms 本地接收间隔
    看门狗一致。两者必须同步修改：lifespan 短于看门狗会让消息在看门狗
    到期前先被 DDS 丢弃。
    """
    return QoSProfile(
        depth=1,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        deadline=Duration(nanoseconds=CMD_VEL_WATCHDOG_MS * 1_000_000),
        lifespan=Duration(nanoseconds=CMD_VEL_WATCHDOG_MS * 1_000_000),
    )


def fast_state() -> QoSProfile:
    """高频状态（/joint_states 125 Hz、/odom、/wheel/odom 50 Hz）。"""
    return QoSProfile(
        depth=5,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )


def state() -> QoSProfile:
    """中频状态（/vacuum/state、/control/safety_state）。"""
    return QoSProfile(
        depth=5,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )


def latched() -> QoSProfile:
    """版本与就绪基线（readiness、/robot_model/info、/calibration/info、
    /map、N-03）。晚加入的订阅者需要立即拿到最后一条。
    """
    return QoSProfile(
        depth=1,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.TRANSIENT_LOCAL,
    )


def diagnostic() -> QoSProfile:
    """/diagnostics。"""
    return QoSProfile(
        depth=10,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
