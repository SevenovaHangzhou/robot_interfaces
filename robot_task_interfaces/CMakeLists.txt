cmake_minimum_required(VERSION 3.8)
project(robot_task_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(robot_system_interfaces REQUIRED)
find_package(robot_control_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/BoxPose.msg"
  "msg/CameraViewPose.msg"
  "msg/PickSequence.msg"
  "msg/WallTaskPlan.msg"
  "action/ExecuteDemoTask.action"
  "action/BuildWallTaskPlan.action"
  "action/RefineSequencePoses.action"
  "action/MoveToCameraViewPose.action"
  "action/PlanAndExecutePick.action"
  "action/PlanAndExecutePlace.action"
  DEPENDENCIES
    std_msgs
    builtin_interfaces
    geometry_msgs
    robot_system_interfaces
    robot_control_interfaces
)

ament_package()
