string LEFT=left
string RIGHT=right

uint8 VACUUM_UNKNOWN=0
uint8 VACUUM_ATTACHED=1
uint8 VACUUM_INTERMEDIATE=2
uint8 VACUUM_RELEASED=3

uint8 VALVE_TARGET_UNKNOWN=0
uint8 VALVE_TARGET_SUCTION=1
uint8 VALVE_TARGET_RELEASE=2

string channel
string sensor_id
float64 pressure_kpa
float64 raw_value
string raw_unit
ObservationMeta pressure_observation
uint8 vacuum_state
OutputState valve
bool last_request_known
unique_identifier_msgs/UUID last_request_id
unique_identifier_msgs/UUID last_attempt_id
uint8 last_valve_target
builtin_interfaces/Time last_output_confirmed_at
bool last_output_confirmation_valid
