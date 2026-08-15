cmake_minimum_required(VERSION 3.8)
project(robot_perception_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(unique_identifier_msgs REQUIRED)
find_package(robot_system_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ObstacleCloud.msg"
  "msg/BoxPose.msg"
  "msg/CameraViewPose.msg"
  "msg/PickSequence.msg"
  "msg/WallTaskPlan.msg"
  "action/BuildWallTaskPlan.action"
  "action/RefineSequencePoses.action"
  DEPENDENCIES
    std_msgs
    sensor_msgs
    builtin_interfaces
    geometry_msgs
    unique_identifier_msgs
    robot_system_interfaces
)

ament_package()
