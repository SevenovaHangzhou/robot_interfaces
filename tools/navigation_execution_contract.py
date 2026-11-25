"""Validate the registry's navigation array contract (not a predictor implementation)."""

import math


def decode_snapshot(data, schema, now, previous_stamp=None, expected_fields=None):
    """Return header/modules keyed by identity, or raise ValueError.

    expected_fields maps absolute indexes to the deployment's effective limits and
    geometry. Callers must supply their own hardware-authoritative configuration.
    This offline contract helper does not establish hardware sample provenance.
    """
    if len(data) != schema["size"]:
        raise ValueError("length")
    if schema["all_fields_finite"] and not all(math.isfinite(v) for v in data):
        raise ValueError("nonfinite")
    width = len(schema["header"])
    stride = len(schema["module"])
    header = dict(zip(schema["header"], data[:width]))
    if header["schema_version"] != schema["version"]:
        raise ValueError("version")
    if header["ready"] != schema["accepted_ready"]:
        raise ValueError("ready")
    if header["status"] not in schema["accepted_statuses"]:
        raise ValueError("status")
    stamp = header["snapshot_ros_time"]
    if not math.isfinite(now) or not (-schema["max_future_ms"] / 1000 <= now - stamp <= schema["max_age_ms"] / 1000):
        raise ValueError("timestamp")
    if schema["stamp_must_advance"] and previous_stamp is not None and stamp <= previous_stamp:
        raise ValueError("continuity")
    sequence = header["sequence"]
    low, high = schema["sequence_range"]
    if not low <= sequence <= high or sequence != int(sequence):
        raise ValueError("sequence")
    if header["translation_branch"] not in schema["translation_branches"]:
        raise ValueError("translation branch")
    if any(header[key] not in (0, 1) for key in schema["header_booleans"]):
        raise ValueError("header boolean")
    modules = {}
    for start in range(width, len(data), stride):
        module = dict(zip(schema["module"], data[start:start + stride]))
        identity = module["module_id"]
        if identity not in schema["module_ids"] or identity in modules:
            raise ValueError("module identity")
        if any(module[key] not in (0, 1) for key in schema["module_booleans"]):
            raise ValueError("module boolean")
        modules[identity] = module
    if set(modules) != set(schema["module_ids"]):
        raise ValueError("missing module")
    for index, expected in (expected_fields or {}).items():
        if not math.isfinite(expected) or abs(data[index] - expected) > schema["configuration_absolute_tolerance"]:
            raise ValueError("configuration")
    return header, modules
