cmake_minimum_required(VERSION 3.8)
project(robot_rt_control_interfaces)

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(robot_system_interfaces REQUIRED)
find_package(unique_identifier_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/JointControlMode.msg"
  "msg/RollingJointControlState.msg"
  "msg/RollingLimitsSource.msg"
  "msg/RollingRejectCode.msg"
  "msg/RollingServiceResult.msg"
  "msg/RollingSessionState.msg"
  "msg/RollingStopReason.msg"
  "msg/SafetyState.msg"
  "msg/VacuumChannelFeedback.msg"
  "msg/VacuumChannelState.msg"
  "msg/VacuumChannelResult.msg"
  "msg/VacuumState.msg"
  "srv/CloseRollingJointSession.srv"
  "srv/OpenRollingJointSession.srv"
  "srv/SetControlEnabled.srv"
  "srv/SetJointControlMode.srv"
  "srv/SetPumpEnabled.srv"
  "action/VacuumGrip.action"
  DEPENDENCIES
    builtin_interfaces
    std_msgs
    robot_system_interfaces
    unique_identifier_msgs
)

ament_package()
