uint8 INSTALLATION_UNKNOWN=0
uint8 INSTALLATION_NOT_INSTALLED=1
uint8 INSTALLATION_INSTALLED=2

uint8 IMPLEMENTATION_UNKNOWN=0
uint8 IMPLEMENTATION_NOT_IMPLEMENTED=1
uint8 IMPLEMENTATION_NOT_ADMITTED=2
uint8 IMPLEMENTATION_AVAILABLE=3

string module_id
uint8 installation_state
uint8 implementation_state
bool enabled
bool configuration_valid
bool data_valid
string operational_state
string[] capability_names
robot_system_interfaces/ErrorInfo[] errors
