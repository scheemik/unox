import json
import subprocess

import unox.HPC.data0.run_functions as rf
from unox.HPC.data0.paths import make_file_path, remove_non_empty_directory
from unox.HPC.data0.config import get_config
from unox.HPC.data0.dataset import uarray

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
        savedir, config_dict, config_file, version = rf.process_cmd_args(case['cmd_args'], verbose=False)
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
            savedir, config_dict, config_file, version = rf.process_cmd_args(cmd_args, verbose=False)
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

def test_make_output_metadata_dict():
    """Test the make_output_metadata_dict function."""
    # Define a test cases
    test_cases = [
        {
            'savedir': 'HPC_runs/test_unet0/',
            'config_path': 'tests/data_for_tests/test_config.json',
            'config_dict': None,
            'version': 1,
            'model_fmt': 'keras',
        }
    ]
    # Test each case
    for this_case in test_cases:
        # Get the configuration dictionary
        this_case['config_dict'] = get_config(this_case['config_path'])
        # Add training and prediction year keys to this case's dictionary
        this_case['train_years'] = {
            'stage1': [],
            'stage2': [],
        }
        this_case['pred_years'] = {
            'stage1': [],
            'stage2': [],
        }
        # Make the output metadata dictionary
        output_metadata = rf.make_output_metadata_dict(
            this_case['savedir'],
            this_case['config_path'],
            this_case['config_dict'],
            this_case['version'],
            this_case['model_fmt'],
        )
        # Compare to the expected value
        assert output_metadata == this_case, f"Expected output metadata dictionary: \n{this_case}\nGot: \n{output_metadata}"
    # Test with invalid inputs
    invalid_inputs = {
        'savedir': [1234, None, True, [], {}],
        'config_path': [1234, None, True, [], {}],
        'config_dict': ['invalid', 1234, None, True, []],
        'version': ['invalid', None, True, [], {}],
        'model_fmt': [1234, None, True, [], {}],
    }
    for invalid_key in invalid_inputs.keys():
        for i_key in invalid_inputs[invalid_key]:
            try:
                npy_arr, lats, lons = uload.get_npy_from_netcdf(
                    invalid_netcdf,
                    2019,
                    input_config,
                    var='u10',
                )
            except Exception as e:
                assert True, f"get_npy_from_netcdf raised an exception on invalid netcdf input: {e}"
            else:
                assert False, f"get_npy_from_netcdf(var) did not raise an exception on invalid netcdf input: {invalid_netcdf}"

def test_prepare_input():
    """Test the prepare_input function."""
    # Define a test cases
    test_cases = [
        {
            'savedir': 'HPC_runs/test_unet0/',
            'config_path': 'sample_config',
            'version': 1,
            'n_epochs': 250,
            'model_fmt': 'keras',
            'input_fmt': 'nc',
            'split_year': 2019,
            'split_value': 0.9,
            'stage': 1,
            'xtrain_shape': (5096, 56, 120, 9),
            'ytrain_shape': (5096, 56, 120, 1),
        },
        {
            'savedir': 'HPC_runs/test_unet0/',
            'config_path': 'sample_config',
            'version': 0,
            'n_epochs': 5,
            'model_fmt': 'h5',
            'input_fmt': 'npy',
            'split_year': 2015,
            'split_value': 0.5,
            'stage': 2,
            'xtrain_shape': (364, 56, 120, 9),
            'ytrain_shape': (364, 56, 120, 1),
        },
    ]
    # Test each case
    for this_case in test_cases:
        # Get the configuration dictionary
        config_dict = get_config(this_case['config_path'])
        # Load the input netcdf file
        uarr = uarray(config_dict['input_set'], is_input_set=True)
        # Make the output metadata dictionary
        output_metadata = rf.make_output_metadata_dict(
            this_case['savedir'],
            this_case['config_path'],
            config_dict,
            this_case['version'],
            this_case['n_epochs'],
            this_case['model_fmt'],
            this_case['input_fmt'],
            this_case['split_year'],
            this_case['split_value'],
        )
        # Prepare the input data
        xtrain, ytrain, actual_output_metadata = rf.prepare_input(uarr, config_dict, output_metadata, this_case['split_year'], stage=this_case['stage'])
        # Add expected `train_years` dictionary to `output_metadata`
        output_metadata["train_years"] = {
            "stage1": [
                2005,
                2006,
                2007,
                2008,
                2009,
                2010,
                2011,
                2012,
                2013,
                2014,
                2015,
                2016,
                2017,
                2018
            ],
            "stage2": [
                2014,
                2015,
                2016,
                2017,
                2018
            ]
        }
        # Compare `xtrain` to the expected value
        assert xtrain.shape == this_case['xtrain_shape'], f"Expected xtrain.shape: {this_case['xtrain_shape']}. Got: {xtrain.shape}"
        # Compare `xtrain` to the expected value
        assert ytrain.shape == this_case['ytrain_shape'], f"Expected ytrain.shape: {this_case['ytrain_shape']}. Got: {ytrain.shape}"
        # Compare `output_metadata` to the expected value
        assert output_metadata == actual_output_metadata, f"Expected output metadata dictionary: \n{output_metadata}\nGot: \n{actual_output_metadata}"
    # Define invalid test cases
    test_cases = [
        {
            'savedir': 'HPC_runs/test_unet0/',
            'config_path': 'sample_config',
            'version': 1,
            'n_epochs': 250,
            'model_fmt': 'keras',
            'input_fmt': 'nc',
            'split_year': 2004,         # Cannot have split_year <= start_year
            'split_value': 0.9,
            'stage': 1,                 # star_year for stage 1 is 2005
        },
        {
            'savedir': 'HPC_runs/test_unet0/',
            'config_path': 'sample_config',
            'version': 0,
            'n_epochs': 5,
            'model_fmt': 'h5',
            'input_fmt': 'npy',
            'split_year': 2014,         # Cannot have split_year <= start_year
            'split_value': 0.5,
            'stage': 2,                 # star_year for stage 2 is 2014
        },
    ]
    # Test each case
    for this_case in test_cases:
        # Get the configuration dictionary
        config_dict = get_config(this_case['config_path'])
        # Load the input netcdf file
        uarr = uarray(config_dict['input_set'], is_input_set=True)
        # Make the output metadata dictionary
        output_metadata = rf.make_output_metadata_dict(
            this_case['savedir'],
            this_case['config_path'],
            config_dict,
            this_case['version'],
            this_case['n_epochs'],
            this_case['model_fmt'],
            this_case['input_fmt'],
            this_case['split_year'],
            this_case['split_value'],
        )
        try:
            # Prepare the input data
            xtrain, ytrain, actual_output_metadata = rf.prepare_input(uarr, config_dict, output_metadata, this_case['split_year'], stage=this_case['stage'])
        except Exception as e:
            assert True, f"prepare_input raised an exception on invalid `split_year` and `stage` input: {e}"
        else:
            assert False, f"prepare_input did not raise an exception on invalid `split_year` ({this_case['split_year']}) and `stage` ({this_case['stage']}) input."