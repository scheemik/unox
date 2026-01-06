import json

from unox.HPC.data0 import config as ucfg

def test_get_config():
    """Test the get_config function."""
    # Test with valid parameters
    valid_configs = [
        'sample_config',
        'inputfiles/_input_configs/sample_config.json',
    ]
    # Define expected results
    expected_configs = [
        'inputfiles/_input_configs/sample_config.json',
        'inputfiles/_input_configs/sample_config.json',
    ]
    for i in range(len(expected_configs)):
        with open(f"{expected_configs[i]}", 'r') as file:
            expected_configs[i] = json.load(file)
        actual_config = ucfg.get_config(valid_configs[i])
        assert actual_config == expected_configs[i], f"get_config did not return expected config for '{valid_configs[i]}'"