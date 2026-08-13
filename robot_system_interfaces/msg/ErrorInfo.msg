uint8 OK=0
uint8 WARN=1
uint8 FAULT=2

# Internal diagnostic code used inside mapping/navigation nodes.
# External consumers should use ErrorReport.code from /navigation/error/status
# and /navigation/error/events.
string code
string message
bool retryable
uint8 severity
string source
string detail
