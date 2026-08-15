uint8 OK=0
uint8 WARN=1
uint8 FAULT=2

# Cross-domain error envelope.
# code is the canonical DREE value from ErrorCode.msg; SUCCESS=0 is the only
# exception. Mapping/navigation internal diagnostic identifiers are
# domain-private and MUST NOT be stored in this field.
uint32 code
string message
# retryable MUST match the R digit encoded in code. Consumers make retry
# decisions from this field rather than parsing code.
bool retryable
uint8 severity
string source
string detail
