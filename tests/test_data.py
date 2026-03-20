import unittest
from pathlib import Path

from src.pipeline_01_config_setup_fun import read_params


class TestCodeIsTested(unittest.TestCase):

    def test_params_file_loads(self):
        params = read_params("config/params.yaml")
        self.assertIn("base", params)
        self.assertIn("data_source", params)

    def test_expected_paths_exist(self):
        self.assertTrue(Path("config/params.yaml").exists())
        self.assertTrue(Path("src/pipeline_06_model_training.py").exists())


if __name__ == '__main__':
    unittest.main()
