cmake_minimum_required(VERSION 3.8)
project(robot_motion_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(unique_identifier_msgs REQUIRED)
find_package(robot_system_interfaces REQUIRED)
find_package(robot_perception_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/ExecuteMotionStage.action"
  "msg/DualArmPoseTargets.msg"
  "msg/RollingJointPoint.msg"
  "msg/RollingJointTargetBatch.msg"
  "msg/PickTarget.msg"
  "msg/PickPair.msg"
  "msg/ArmExecutionState.msg"
  "msg/ArmTaskResult.msg"
  "msg/ManipulationState.msg"
  "action/PickAndCarry.action"
  "action/PlaceCarriedBoxes.action"
  "action/MoveToPosture.action"
  "srv/TerminateTask.srv"
  "srv/ResetTask.srv"
  "srv/GetEndEffectorPoseAtTime.srv"
  "action/MoveJoints.action"
  "action/MoveDualTcp.action"
  DEPENDENCIES
    builtin_interfaces
    geometry_msgs
    std_msgs
    unique_identifier_msgs
    robot_system_interfaces
    robot_perception_interfaces
)

ament_package()
