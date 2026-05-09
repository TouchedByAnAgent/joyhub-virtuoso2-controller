import unittest

from touched_by_an_agent.protocol import (
    DEVICE,
    all_actuator_commands,
    all_off_commands,
    bytes_from_hex,
    preset_commands,
    preset_names,
    suction_command,
    wave_command,
)


class ProtocolTests(unittest.TestCase):
    def test_device_identity_is_specific_to_validated_unit(self):
        self.assertEqual(DEVICE.name, "J-Virtuoso2 / Virtuoso 2")
        self.assertEqual(DEVICE.address, "FF:25:07:11:DD:36")
        self.assertEqual(DEVICE.product_code, "3131")
        self.assertEqual(DEVICE.ic_code, "8d")
        self.assertEqual(DEVICE.ability_code, "01100000")
        self.assertEqual(DEVICE.ability_limit, "060050000000")
        self.assertEqual(DEVICE.switch_code, "0803")

    def test_wave_commands_cover_vibration_and_tongue_levels(self):
        self.assertEqual(wave_command(0, 0), "a00300000000aa")
        self.assertEqual(wave_command(vibration_level=1), "a00351000000aa")
        self.assertEqual(wave_command(vibration_level=9), "a003ff000000aa")
        self.assertEqual(wave_command(tongue_level=1), "a00300480000aa")
        self.assertEqual(wave_command(tongue_level=9), "a00300ff0000aa")
        self.assertEqual(wave_command(9, 9), "a003ffff0000aa")

    def test_suction_commands_cover_p_levels(self):
        self.assertEqual(suction_command(0), "a00d00000000")
        self.assertEqual(suction_command(1), "a00d000001ff")
        self.assertEqual(suction_command(2), "a00d000002ff")
        self.assertEqual(suction_command(3), "a00d000003ff")
        with self.assertRaises(ValueError):
            suction_command(4)

    def test_all_actuator_combination_sends_suction_first(self):
        self.assertEqual(all_actuator_commands(), ("a00d000003ff", "a003ffff0000aa"))

    def test_presets_are_complete_and_validated(self):
        names = preset_names()
        self.assertIn("all-off", names)
        self.assertIn("all-actuators-max", names)
        self.assertIn("vibration-9", names)
        self.assertIn("tongue-9", names)
        self.assertIn("combined-9", names)
        self.assertIn("suction-p3", names)
        self.assertEqual(preset_commands("all-off"), all_off_commands())
        self.assertEqual(preset_commands("all-actuators-max"), all_actuator_commands())

    def test_hex_conversion_rejects_odd_length(self):
        self.assertEqual(bytes_from_hex("a00d000003ff"), bytes([0xA0, 0x0D, 0x00, 0x00, 0x03, 0xFF]))
        with self.assertRaises(ValueError):
            bytes_from_hex("abc")


if __name__ == "__main__":
    unittest.main()
