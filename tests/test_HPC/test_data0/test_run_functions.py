import json

import unox.HPC.data0.run_functions as rf
from unox.HPC.data0.paths import make_file_path, remove_non_empty_directory
from unox.HPC.data0.config import get_config

def test_process_cmd_args():
    """Test the process_cmd_args function."""
    # Define test save directory
    test_save_dir = 'my_savedir'
    # Define test configuration file
    test_config_file = 'tests/data_for_tests/test_config.json'
    # Define test cases
    test_cases = [
        {   # Test with all arguments provided
            'cmd_args': ['run_model.py', test_save_dir, test_config_file, 0],
            'expected_savedir': 'my_savedir/',
            'expected_config_file': test_config_file,
            'expected_version': 0,
        },
        {   # Test with missing version argument
            'cmd_args': ['run_model.py', test_save_dir, test_config_file],
            'expected_savedir': 'my_savedir/',
            'expected_config_file': test_config_file,
            'expected_version': 1,                          # default
        },
        {   # Test with missing config and version arguments
            'cmd_args': ['run_model.py', test_save_dir],
            'expected_savedir': 'my_savedir/',
            'expected_config_file': 'sample_config',         # default
            'expected_version': 1,                          # default
        },
        {   # Test with only script name
            'cmd_args': ['run_model.py'],
            'expected_savedir': 'HPC_runs/test_unet0/',     # default
            'expected_config_file': 'sample_config',         # default
            'expected_version': 1,                          # default
        },
    ]
    # Test each case
    for case in test_cases:
        savedir, config_dict, version = rf.process_cmd_args(case['cmd_args'], verbose=False)
        assert savedir == case['expected_savedir'], f"Expected savedir {case['expected_savedir']}, got {savedir}"
        # Get the config file to compare
        expected_config = get_config(case['expected_config_file'])
        assert config_dict == expected_config, f"Expected config_dict from {case['expected_config_file']} does not match actual."
        assert version == case['expected_version'], f"Expected version {case['expected_version']}, got {version}"
        # Clean up the created directory
        remove_non_empty_directory(savedir)
    # Create a test save directory
    make_file_path(test_save_dir)
    # Load the test configuration file
    test_config = get_config(test_config_file)
    # Save that test configuration file in the test save directory
    with open(f"{test_save_dir}/input_config.json", 'w') as file:
        file.write(json.dumps(test_config, indent=4))
    # Test the case where the config file already exists
    cmd_args = ['run_model.py', test_save_dir]
    savedir, config_dict, version = rf.process_cmd_args(cmd_args, verbose=False)
    assert savedir == test_save_dir+'/', f"Expected savedir {test_save_dir}, got {savedir}"
    # Get the config file to compare
    expected_config = get_config(case['expected_config_file'])
    assert config_dict == test_config, f"Expected config_dict from {test_config_file} does not match actual."
    assert version == 1, f"Expected version 1, got {version}"
    # Clean up the created directory
    remove_non_empty_directory(savedir)

    # Import the test argument script
    # import arg_script as arg_script
    # # Run `arg_script.py` with test arguments a, b, c
    # import subprocess
    # test_args = ['python', 'tests/test_HPC/test_data0/arg_script.py', 'a', 'b', 'c']
    # result = subprocess.run(test_args, capture_output=True, shell=True)
    # The result should be the same as `test_args[1:]`
    # assert result
    # 