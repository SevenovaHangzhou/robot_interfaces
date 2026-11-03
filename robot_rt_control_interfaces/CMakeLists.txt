cmake_minimum_required(VERSION 3.8)
project(robot_rt_control_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(std_msgs REQUIRED)
find_package(unique_identifier_msgs REQUIRED)
find_package(robot_system_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ObservationMeta.msg"
  "msg/OutputState.msg"
  "msg/OutputCommandResult.msg"
  "msg/JointControlMode.msg"
  "msg/RollingJointControlState.msg"
  "msg/RollingLimitsSource.msg"
  "msg/RollingRejectCode.msg"
  "msg/RollingServiceResult.msg"
  "msg/RollingSessionState.msg"
  "msg/RollingStopReason.msg"
  "msg/SafetyState.msg"
  "msg/DigitalInputState.msg"
  "msg/DigitalInputStateArray.msg"
  "msg/ModuleState.msg"
  "msg/ModuleStateArray.msg"
  "msg/MotionExecutionState.msg"
  "msg/ProtectiveStopState.msg"
  "msg/SensorStatus.msg"
  "msg/SensorStatusArray.msg"
  "msg/VacuumChannelState.msg"
  "msg/VacuumState.msg"
  "msg/VacuumStateEvent.msg"
  "srv/SetControlEnabled.srv"
  "srv/CloseRollingJointSession.srv"
  "srv/OpenRollingJointSession.srv"
  "srv/SetJointControlMode.srv"
  "srv/ResetProtectiveStop.srv"
  "srv/SetLedRgbw.srv"
  "srv/SetPumpEnabled.srv"
  "action/MoveAxis.action"
  "action/MoveHead.action"
  "action/SetVacuumValves.action"
  DEPENDENCIES builtin_interfaces std_msgs unique_identifier_msgs robot_system_interfaces
)

ament_package()
