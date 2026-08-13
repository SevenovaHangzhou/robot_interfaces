cmake_minimum_required(VERSION 3.8)
project(robot_autonomy_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(robot_system_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/ExecuteDemoTask.action"
  DEPENDENCIES robot_system_interfaces
)

ament_package()
