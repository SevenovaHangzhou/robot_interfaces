# Fine-grained result for set-mode, open, and close services.
# ErrorInfo supplies the cross-domain DREE envelope; clients branch on this value
# and ErrorInfo.retryable, never on strings.

uint8 NONE=0
uint8 WRONG_PROTOCOL=1
uint8 WRONG_REQUEST=2
uint8 WRONG_MODE=3
uint8 NOT_ENABLED=4
uint8 SESSION_BUSY=5
uint8 SESSION_EXISTS=6
uint8 WRONG_BOOT=7
uint8 WRONG_SESSION=8
uint8 WRONG_CLIENT=9
uint8 AXIS_SET_MISMATCH=10
uint8 SOURCE_STATE_STALE=11
uint8 SOURCE_MOVING=12
uint8 TAKEOVER_MISMATCH=13
uint8 UNSAFE_HOLD=14
uint8 FEEDBACK_STALE=15
uint8 LIMITS_UNAVAILABLE=16
uint8 SWITCH_REJECTED=17
uint8 SWITCH_TIMEOUT=18
uint8 RESTART_REQUIRED=19
uint8 NOT_READY=20

uint8 value
