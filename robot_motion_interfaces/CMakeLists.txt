cmake_minimum_required(VERSION 3.8)
project(robot_motion_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(unique_identifier_msgs REQUIRED)
find_package(robot_system_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Landmark.msg"
  "msg/LandmarkArray.msg"
  "msg/LocalizationStatus.msg"
  "action/NavigateToPoseTask.action"
  "srv/AddCurrentLandmark.srv"
  "srv/AddLandmark.srv"
  "srv/GetLandmark.srv"
  "srv/GetSemanticMap.srv"
  "srv/RemoveLandmark.srv"
  "srv/SetMappingTurnState.srv"
  "srv/UpdateLandmark.srv"
  "action/ExecuteMotionStage.action"
  "msg/DualArmPoseTargets.msg"
  "msg/RollingJointPoint.msg"
  "msg/RollingJointTargetBatch.msg"
  "msg/PickTarget.msg"
  "msg/PickPair.msg"
  "msg/ArmExecutionState.msg"
  "msg/ArmTaskResult.msg"
  "msg/ManipulationState.msg"
  "msg/DroppedBoxCandidate.msg"
  "action/PickAndCarry.action"
  "action/PlaceCarriedBoxes.action"
  "action/MoveToPosture.action"
  "srv/TerminateTask.srv"
  "action/DetectDroppedBoxes.action"
  DEPENDENCIES
    builtin_interfaces
    geometry_msgs
    std_msgs
    unique_identifier_msgs
    robot_system_interfaces
)

ament_package()
