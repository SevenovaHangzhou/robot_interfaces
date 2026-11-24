cmake_minimum_required(VERSION 3.8)
project(robot_navigation_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(robot_system_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Landmark.msg"
  "msg/LandmarkArray.msg"
  "msg/LocalizationStatus.msg"
  "msg/DroppedBoxCandidate.msg"
  "srv/AddCurrentLandmark.srv"
  "srv/AddLandmark.srv"
  "srv/GetLandmark.srv"
  "srv/GetSemanticMap.srv"
  "srv/RemoveLandmark.srv"
  "srv/SetMappingTurnState.srv"
  "srv/UpdateLandmark.srv"
  "action/NavigateToPoseTask.action"
  "action/DetectDroppedBoxes.action"
  DEPENDENCIES builtin_interfaces geometry_msgs std_msgs robot_system_interfaces
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
