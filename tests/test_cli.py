import contextlib
from io import StringIO
import unittest

from touched_by_an_agent.cli import build_parser, main


class CliTests(unittest.TestCase):
    def capture_main(self, argv):
        stream = StringIO()
        with contextlib.redirect_stdout(stream):
            code = main(argv)
        return code, stream.getvalue()

    def test_parser_defaults_to_validated_device_address(self):
        args = build_parser().parse_args(["preset", "all-actuators-max", "--dry-run"])
        self.assertEqual(args.address, "FF:25:07:11:DD:36")

    def test_preset_dry_run_prints_automatic_cleanup(self):
        code, out = self.capture_main(["preset", "all-actuators-max", "--dry-run"])
        self.assertEqual(code, 0)
        self.assertIn("a00d000003ff", out)
        self.assertIn("a003ffff0000aa", out)
        self.assertIn("# cleanup", out)
        self.assertIn("a00300000000aa", out)
        self.assertIn("a00d00000000", out)

    def test_raw_send_dry_run_prints_automatic_cleanup(self):
        code, out = self.capture_main(["send", "a003ff000000aa", "--dry-run"])
        self.assertEqual(code, 0)
        self.assertIn("a003ff000000aa", out)
        self.assertIn("# cleanup", out)

    def test_presets_command_lists_verified_presets(self):
        code, out = self.capture_main(["presets"])
        self.assertEqual(code, 0)
        self.assertIn("vibration-9", out)
        self.assertIn("tongue-9", out)
        self.assertIn("combined-9", out)
        self.assertIn("suction-p3", out)
        self.assertIn("all-actuators-max", out)


if __name__ == "__main__":
    unittest.main()
