cmake_minimum_required(VERSION 3.8)
project(robot_interfaces_rolling_client)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rclcpp REQUIRED)
find_package(robot_interfaces_qos REQUIRED)
find_package(robot_motion_interfaces REQUIRED)
find_package(robot_rt_control_interfaces REQUIRED)

set(dependencies
  builtin_interfaces
  rclcpp
  robot_interfaces_qos
  robot_motion_interfaces
  robot_rt_control_interfaces
)

add_library(${PROJECT_NAME} SHARED
  src/rolling_stream.cpp
  src/rolling_sender.cpp
)
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic -Wconversion)
target_include_directories(${PROJECT_NAME} PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>"
)
ament_target_dependencies(${PROJECT_NAME} ${dependencies})

install(DIRECTORY include/ DESTINATION include)
install(TARGETS ${PROJECT_NAME} EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_rolling_stream test/test_rolling_stream.cpp)
  target_link_libraries(test_rolling_stream ${PROJECT_NAME})
  ament_add_gtest(test_rolling_sender test/test_rolling_sender.cpp)
  target_link_libraries(test_rolling_sender ${PROJECT_NAME})
endif()

ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_dependencies(${dependencies})
ament_package()
