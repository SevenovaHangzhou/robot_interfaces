std_msgs/Header header
unique_identifier_msgs/UUID producer_instance_id
OutputState pump
# Fixed order: left, right. Each channel retains its own observation time.
VacuumChannelState[2] channels
