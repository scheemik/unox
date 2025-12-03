import json
import subprocess

import unox.HPC.data0.run_functions as rf
from unox.HPC.data0.paths import make_file_path, remove_non_empty_directory
from unox.HPC.data0.config import get_config

def test_process_cmd_args():
    """Test the process_cmd_args function."""
    # Define test run script (defined relative to this file?)
    test_run_script = 'tests/test_HPC/test_data0/arg_script.py'
    # Define test save directory
    test_save_dir = 'my_savedir'
    # Define test configuration file
    test_config_file = 'tests/data_for_tests/test_config.json'
    # Define sample configuration file
    test_sample_config = 'sample_config'
    test_sample_config_path = f"inputfiles/_input_configs/{test_sample_config}.json"
    # Define default save directory
    default_savedir = 'HPC_runs/test_unet0/'
    # Define test cases
    test_cases = [
        {   # Test with all arguments provided
            'cmd_args': [test_run_script, test_save_dir, test_config_file, 0],
            'expected_savedir': f'{test_save_dir}/',
            'expected_config_file': test_config_file,
            'expected_version': 0,
            'expected_stdout': f"Script name (sys.argv[0]): {test_run_script}\nCommand line arguments: ['{test_run_script}', '{test_save_dir}', '{test_config_file}', '0']\n\targv[1], savedir: {test_save_dir}/\n\targv[2], config_file: {test_config_file}\n\targv[3], version: 0\n",
        },
        {   # Test with missing version argument
            'cmd_args': [test_run_script, test_save_dir, test_config_file],
            'expected_savedir': f'{test_save_dir}/',
            'expected_config_file': test_config_file,
            'expected_version': 1,                          # default
            'expected_stdout': f"Script name (sys.argv[0]): {test_run_script}\nCommand line arguments: ['{test_run_script}', '{test_save_dir}', '{test_config_file}']\n\targv[1], savedir: {test_save_dir}/\n\targv[2], config_file: {test_config_file}\n\targv[3], version: 1\n",
        },
        {   # Test with missing config and version arguments
            'cmd_args': [test_run_script, test_save_dir],
            'expected_savedir': f'{test_save_dir}/',
            'expected_config_file': test_sample_config,        # default
            'expected_version': 1,                          # default
            'expected_stdout': f"Script name (sys.argv[0]): {test_run_script}\nCommand line arguments: ['{test_run_script}', '{test_save_dir}']\n\targv[1], savedir: {test_save_dir}/\n\targv[2], config_file: {test_sample_config_path}\n\targv[3], version: 1\n",
        },
        {   # Test with only script name
            'cmd_args': [test_run_script],
            'expected_savedir': default_savedir,     # default
            'expected_config_file': test_sample_config,        # default
            'expected_version': 1,                          # default
            'expected_stdout': f"Script name (sys.argv[0]): {test_run_script}\nCommand line arguments: ['{test_run_script}']\n\targv[1], savedir: {default_savedir}\n\targv[2], config_file: {test_sample_config_path}\n\targv[3], version: 1\n",
        },
    ]
    # Test each case
    for case in test_cases:
        # Use the function directly
        savedir, config_dict, version = rf.process_cmd_args(case['cmd_args'], verbose=False)
        assert savedir == case['expected_savedir'], f"Expected savedir {case['expected_savedir']}, got {savedir}"
        # Get the config file to compare
        expected_config = get_config(case['expected_config_file'])
        assert config_dict == expected_config, f"Expected config_dict from {case['expected_config_file']} does not match actual."
        assert version == case['expected_version'], f"Expected version {case['expected_version']}, got {version}"
        # Clean up the created directory
        remove_non_empty_directory(savedir)

        # Use a subprocess to run a script with input arguments which calls the function
        # Need to add `python` to the list of command arguments as that is what will call the script
        sub_pro_cmd_args = ['python'] + [str(arg) for arg in case['cmd_args']]
        # Run the subprocess and capture the `stdout` as text
        result = subprocess.run(sub_pro_cmd_args, capture_output=True, text=True)
        # Get the `stdout` text to compare
        actual_stdout = result.stdout
        assert actual_stdout == case['expected_stdout'], f"Expected stdout: \n{case['expected_stdout']}\nGot: \n{result}"
        # Clean up the created directory
        remove_non_empty_directory(savedir)
    
    # Define the command line arguments
    cmd_args = [test_run_script, test_save_dir]
    # Define the expected stdout
    expected_stdout = f"Script name (sys.argv[0]): {test_run_script}\nCommand line arguments: ['{test_run_script}', '{test_save_dir}']\n\targv[1], savedir: {test_save_dir}/\n\targv[2], config_file: {test_save_dir}/input_config.json\n\targv[3], version: 1\n"
    # Test in the case where a config file already exists
    for i in range(2): 
        # Create a test save directory
        make_file_path(test_save_dir)
        # Load the test configuration file
        test_config = get_config(test_config_file)
        # Save that test configuration file in the test save directory
        with open(f"{test_save_dir}/input_config.json", 'w') as file:
            file.write(json.dumps(test_config, indent=4))
        # Use the function directly
        if i == 0:
            savedir, config_dict, version = rf.process_cmd_args(cmd_args, verbose=False)
            assert savedir == test_save_dir+'/', f"Expected savedir {test_save_dir}, got {savedir}"
            # Compare the configuration dictionaries
            assert config_dict == test_config, f"Expected config_dict from {test_config_file} does not match actual."
            assert version == 1, f"Expected version 1, got {version}"
        # Use a subprocess to run a script with input arguments which calls the function
        if i == 1:
            # Need to add `python` to the list of command arguments as that is what will call the script
            sub_pro_cmd_args = ['python'] + [str(arg) for arg in cmd_args]
            # Run the subprocess and capture the `stdout` as text
            result = subprocess.run(sub_pro_cmd_args, capture_output=True, text=True)
            # Get the `stdout` text to compare
            actual_stdout = result.stdout
            assert actual_stdout == expected_stdout, f"Expected stdout: \n{expected_stdout}\nGot: \n{result}"
        # Clean up the created directory
        remove_non_empty_directory(savedir)