"""Unit tests for config_manager module."""
import unittest
import os
import json
import tempfile
import shutil
from src.config_manager import load_config, DEFAULT_CONFIG


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        """Create temporary directory for test configs."""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_config.json")

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_load_default_config(self):
        """Test loading default config when file doesn't exist."""
        config = load_config(self.config_path)
        self.assertIn("messages", config)
        self.assertIn("presets", config)
        self.assertIn("witness_mode", config)
        self.assertTrue(os.path.exists(self.config_path))

    def test_load_existing_config(self):
        """Test loading existing config file."""
        custom_config = {"messages": ["Custom message"], "presets": {"custom": 99}}
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(custom_config, f)

        config = load_config(self.config_path)
        self.assertEqual(config["messages"], ["Custom message"])
        self.assertEqual(config["presets"]["custom"], 99)

    def test_default_config_structure(self):
        """Test default config has required structure."""
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
            "witness_mode": True
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(dirty_config, f)
        loaded = load_config(self.config_path)
        self.assertEqual(loaded["messages"], ["A", "B"])
        self.assertIn("safe_word", loaded)
        self.assertTrue(len(loaded["safe_word"]) > 0)


if __name__ == "__main__":
    unittest.main()
