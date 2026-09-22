"""First unit tests for STTM: the pure logic behind `kb-rgb`.

The script has no `.py` extension (it is installed as `kb-rgb`), so it is
loaded from its path with importlib. Nothing here touches a keyboard, OpenRGB
or the network.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_loader(
        name, importlib.machinery.SourceFileLoader(name, str(ROOT / filename))
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kb = load("kb_rgb_under_test", "kb-rgb")


class RgbToHsv(unittest.TestCase):
    def test_primaries(self):
        self.assertEqual(kb.rgb_to_hsv_bytes(255, 0, 0), [0, 255, 255])
        self.assertEqual(kb.rgb_to_hsv_bytes(0, 255, 0), [85, 255, 255])
        self.assertEqual(kb.rgb_to_hsv_bytes(0, 0, 255), [170, 255, 255])

    def test_black_and_white(self):
        self.assertEqual(kb.rgb_to_hsv_bytes(0, 0, 0), [0, 0, 0])
        self.assertEqual(kb.rgb_to_hsv_bytes(255, 255, 255), [0, 0, 255])

    def test_grey_has_no_saturation(self):
        hsv = kb.rgb_to_hsv_bytes(128, 128, 128)
        self.assertEqual(hsv[1], 0)


class ParseOverrides(unittest.TestCase):
    def test_hex_colour_becomes_rgb(self):
        rgb, _, _, _, _, _, positional = kb.parse_overrides(["--rgb", "ff8000", "keyboard"])
        self.assertEqual(rgb, (255, 128, 0))
        self.assertEqual(positional, ["keyboard"])

    def test_hash_prefix_is_accepted(self):
        rgb, *_ = kb.parse_overrides(["--rgb", "#00ff00"])
        self.assertEqual(rgb, (0, 255, 0))

    def test_symbolic_colour_is_a_theme_source_not_an_rgb(self):
        # Round 99: a symbolic KB_COLOR (`tint`, `outline`, `logo`, `live`) must
        # reach the theme lookup, not be parsed as a colour.
        rgb, _, _, _, _, theme_src, _ = kb.parse_overrides(["--rgb", "outline"])
        self.assertIsNone(rgb)
        self.assertEqual(theme_src, "outline")

    def test_mode_flag_is_passed_through(self):
        _, _, _, _, mode, _, _ = kb.parse_overrides(["--mode", "blsw"])
        self.assertEqual(mode, "blsw")

    def test_hsv_value_and_saturation_flags(self):
        _, hsv, vforce, sforce, _, _, _ = kb.parse_overrides(
            ["--hsv", "10,20,30", "--value", "12", "--sat", "200"]
        )
        self.assertEqual(hsv, [10, 20, 30])
        self.assertEqual((vforce, sforce), (12, 200))


if __name__ == "__main__":
    unittest.main()
