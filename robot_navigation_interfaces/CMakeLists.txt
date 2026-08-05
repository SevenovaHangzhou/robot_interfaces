cmake_minimum_required(VERSION 3.8)
project(robot_navigation_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(robot_system_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/LocalizationStatus.msg"
  "action/NavigateToPoseTask.action"
  DEPENDENCIES std_msgs geometry_msgs robot_system_interfaces
)

ament_package()
