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
  "msg/JointControlMode.msg"
  "msg/RollingJointControlState.msg"
  "msg/DigitalInputState.msg"
  "msg/DigitalInputStateArray.msg"
  "msg/MotionExecutionState.msg"
  "msg/SensorStatus.msg"
  "msg/SensorStatusArray.msg"
  "srv/RtEnable.srv"
  "srv/SetEnabled.srv"
  "srv/SetJointControlMode.srv"
  "srv/SetLedRgbw.srv"
  "action/MoveHead.action"
  DEPENDENCIES builtin_interfaces std_msgs unique_identifier_msgs robot_system_interfaces
)

ament_package()
