cmake_minimum_required(VERSION 3.8)
project(robot_motion_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(robot_system_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/NavigateToPoseTask.action"
  "action/ExecuteMotionStage.action"
  "msg/DualArmPoseTargets.msg"
  DEPENDENCIES
    geometry_msgs
    robot_system_interfaces
)

ament_package()
