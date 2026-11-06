"""The Rolling client repeats three registry facts in C++; they must match the registry."""

from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
HEADERS = ROOT / "rolling_client/include/robot_interfaces_rolling_client"


def cpp_constant(header: str, name: str) -> str:
    text = (HEADERS / header).read_text()
    match = re.search(rf"\b{name}(?:\[\])?\s*(?:=\s*\"(?P<string>[^\"]+)\"|\{{(?P<number>\d+)\}})", text)
    if match is None:
        raise AssertionError(f"{name} not found in {header}")
    return match.group("string") or match.group("number")


class RollingClientContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        contract = yaml.safe_load((ROOT / "contract/endpoints.yaml").read_text())
        cls.endpoints = {entry["id"]: entry for entry in contract["endpoints"]}

    def test_topics_are_the_registered_endpoints(self):
        self.assertEqual(
            cpp_constant("rolling_sender.hpp", "kCommandTopic"), self.endpoints["M-09"]["ros_name"])
        self.assertEqual(
            cpp_constant("rolling_sender.hpp", "kStateTopic"), self.endpoints["R-OUT-07"]["ros_name"])

    def test_state_age_limit_is_the_registered_one(self):
        self.assertEqual(
            int(cpp_constant("rolling_stream.hpp", "kStateMaxAge")),
            self.endpoints["R-OUT-07"]["max_age_ms"])


if __name__ == "__main__":
    unittest.main()
