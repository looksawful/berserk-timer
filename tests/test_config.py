"""Unit tests for config_manager module."""
import json
import os
import shutil
import tempfile
import unittest

from src.config_manager import DEFAULT_CONFIG, load_config


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_config.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_default_config(self):
        config = load_config(self.config_path)
        self.assertIn("messages", config)
        self.assertIn("presets", config)
        self.assertIn("witness_mode", config)
        self.assertTrue(os.path.exists(self.config_path))

    def test_load_existing_config(self):
        custom_config = {"messages": ["Custom message"], "presets": {"custom": 99}}
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(custom_config, f)

        config = load_config(self.config_path)
        self.assertEqual(config["messages"], ["Custom message"])
        self.assertEqual(config["presets"]["custom"], 99)

    def test_default_config_structure(self):
        self.assertIsInstance(DEFAULT_CONFIG["messages"], list)
        self.assertIsInstance(DEFAULT_CONFIG["presets"], dict)
        self.assertIn("xs", DEFAULT_CONFIG["presets"])
        self.assertIn("s", DEFAULT_CONFIG["presets"])
        self.assertIn("m", DEFAULT_CONFIG["presets"])
        self.assertIn("l", DEFAULT_CONFIG["presets"])
        self.assertIn("xl", DEFAULT_CONFIG["presets"])
        self.assertIn("safe_word", DEFAULT_CONFIG)

    def test_load_config_sanitizes_messages_and_adds_safe_word(self):
        dirty_config = {
            "messages": ["A", "", "  ", "B"],
            "presets": {"xs": 5},
            "witness_mode": True,
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(dirty_config, f)
        loaded = load_config(self.config_path)
        self.assertEqual(loaded["messages"], ["A", "B"])
        self.assertIn("safe_word", loaded)
        self.assertTrue(len(loaded["safe_word"]) > 0)

    def test_partial_config_gets_required_defaults_without_overwriting_custom_values(self):
        partial = {"messages": ["Custom"], "volume": 9}
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(partial, f)

        loaded = load_config(self.config_path)

        self.assertEqual(loaded["messages"], ["Custom"])
        self.assertEqual(loaded["volume"], 9)
        self.assertEqual(loaded["presets"], DEFAULT_CONFIG["presets"])
        self.assertEqual(loaded["witness_mode"], DEFAULT_CONFIG["witness_mode"])
        self.assertEqual(loaded["safe_word"], DEFAULT_CONFIG["safe_word"])
        self.assertEqual(loaded["sound_file"], DEFAULT_CONFIG["sound_file"])

    def test_malformed_json_recovers_to_defaults_and_repairs_file(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write('{"messages": ["broken"],')

        loaded = load_config(self.config_path)

        self.assertEqual(loaded, DEFAULT_CONFIG)
        with open(self.config_path, encoding="utf-8") as f:
            repaired = json.load(f)
        self.assertEqual(repaired, DEFAULT_CONFIG)

    def test_witness_mode_string_false_is_parsed_as_false(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump({"witness_mode": "false"}, f)

        loaded = load_config(self.config_path)

        self.assertIs(loaded["witness_mode"], False)

    def test_invalid_preset_values_fall_back_without_discarding_valid_custom_presets(self):
        dirty = {
            "presets": {
                "xs": "five",
                "s": 0,
                "m": 15,
                "custom": 99,
                "junk": None,
            }
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(dirty, f)

        loaded = load_config(self.config_path)

        self.assertEqual(loaded["presets"]["xs"], DEFAULT_CONFIG["presets"]["xs"])
        self.assertEqual(loaded["presets"]["s"], DEFAULT_CONFIG["presets"]["s"])
        self.assertEqual(loaded["presets"]["m"], 15)
        self.assertEqual(loaded["presets"]["custom"], 99)
        self.assertNotIn("junk", loaded["presets"])


if __name__ == "__main__":
    unittest.main()
