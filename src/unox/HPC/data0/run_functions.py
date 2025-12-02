import numpy as np
import json

# Necessary to use relative imports (starting with a dot) to avoid
# errors when running on HPC as the `unox` package is not available
from .paths import verify_path, make_file_path
from .config import get_config
from .verify_dtype import verify_number
from .load_input import get_npy_from_netcdf

def process_cmd_args(
    cmd_args,
    verbose = True,
    default_savedir = 'HPC_runs/test_unet0',
    default_config = 'input_config',
    default_version = 1,
):
    """Process command line arguments given to `run_model.py`

    Parameters
    ----------
    cmd_args : list
        The list of command line arguments given to `run_model.py`.
        Assumes the arguments are:
        - arg 0: script name (i.e., `run_model.py`)
        - arg 1: savedir, the directory in which to save model outputs
        - arg 2: config_file, the model configuration file to use
        - arg 3: version, the version of the packages to import (0 or 1)
    verbose : bool, optional
        Whether to print the processed command line arguments.
        Default is True.
    default_savedir : str, optional
        The default save directory to use if none is found in `cmd_args`.
        Default is 'HPC_runs/test_unet'.
    default_config : str, optional
        The default config file to use if none is found in `cmd_args`.
        Default is 'input_config'.
    default_version : int, optional
        The default version to use if none is found in `cmd_args`.
        Default is 1.
    
    Returns
    -------
    savedir : str
        The path to the directory in which to save model outputs.
    config_dict : dict
        The model configuration dictionary.
    version : int
        The version of the packages to use for running the model (0 or 1).

    """ 
    # Verify argument types
    if not isinstance(cmd_args, list):
        raise TypeError(f"(process_cmd_args) `cmd_args` must be a list. Got {type(cmd_args)}")
    
    # Load the first input argument: the save directory
    try:
        savedir = cmd_args[1]
    except:
        savedir = default_savedir
    # Verify the savedir path
    if not isinstance(savedir, str):
        raise TypeError(f"(process_cmd_args) `savedir` (`cmd_args[1]`) must be a string. Got {type(savedir)}")
    # Add trailing slash if not present
    if not savedir.endswith('/'):
        savedir += '/'
    # Make a new directory if it doesn't exist
    try:
        verify_path(savedir)
    except:
        make_file_path(savedir)
    if verbose:
        print(f"\targv[1], savedir: {savedir}")

    # Load the second input argument: the config file
    try:
        # If a specific config file was given, pull from `inputfiles/_input_configs/`
        config_file = cmd_args[2]
        config_path = config_file
    except:
        # If no config file was specified, use default config
        # that was copied to `savedir` at the start of the run
        config_path = f"{savedir}{default_config}.json"
    # Get the config dictionary (`get_config` verifies type of `config_path`)
    try:
        config_dict = get_config(config_path)
    except:
        # Default to `inputfiles/_input_configs/sample_config.json`
        config_path = "inputfiles/_input_configs/sample_config.json"
        config_dict = get_config(config_path)
    if verbose:
        print(f"\targv[2], config_file: {config_path}")
    # If wasn't already present, write the config dictionary to 
    # a json file in `savedir``
    if not savedir in config_path:
        with open(f"{savedir}input_config.json", 'w') as file:
            file.write(json.dumps(config_dict, indent=4))

    # Load the third input argument: the version of the packages to use
    try:
        version = cmd_args[3]
    except:
        version = default_version 
    # Verify that `version` is a number
    if not verify_number(version):
        raise TypeError(f"(process_cmd_args) `version` (`cmd_args[3]`) must be a number. Got {type(version)}")
    else:
        version = int(version)
    if verbose:
        print(f"\targv[3], version: {version}")
    
    # If using the old version of the packages, create directories for staged output
    if version == 0:
        stage1_dir = make_file_path(f"{savedir}stage1_output/")
        stage2_dir = make_file_path(f"{savedir}stage2_output/")
    
    return savedir, config_dict, version

def prepare_input(
    uarr,
    config_path,
    output_metadata,
    split_year = 2019,
):
    """Prepare the input data for the model.

    Get the training data from the input NetCDF dataset as numpy arrays
    and concatenate them along the time dimension.

    Parameters
    ----------
    uarr : unox.uarray
        The dataset of the input NetCDF file.
    split_year : int, optional
        The year at which to split the training and validation data.
        Defaults to 2019.
    
    Returns
    -------
    """
    # Verify the uarray object
    uarr._verify()
    # Get list of years present in the `from_xr` netcdf
    years = uarr._get_years()
    # Create blank lists to hold x and y training data
    xtrain_list = []
    ytrain_list = []
    # If before the split year, add x and y data to train lists
    for year in range(min(years), split_year):
        this_x_train_arr, in_lats, in_lons = get_npy_from_netcdf(uarr.xr, year, config_path, x_or_y='x')
        xtrain_list.append(this_x_train_arr)
        this_y_train_arr, in_lats, in_lons = get_npy_from_netcdf(uarr.xr, year, config_path, x_or_y='y')
        ytrain_list.append(this_y_train_arr)
        output_metadata['train_years']['stage1'].append(year)
    # Check the shapes of the input arrays
    print(f"\tShape of first xtrain file: {xtrain_list[0].shape}")
    print(f"\tShape of first ytrain file: {ytrain_list[0].shape}")
    # Concatenate training data
    xtrain = np.concatenate(xtrain_list, axis=0)
    ytrain = np.concatenate(ytrain_list, axis=0)
    print("After concatenation:")
    print(f"\tShape of xtrain: {xtrain.shape}")
    print(f"\tShape of ytrain: {ytrain.shape}")
    return xtrain, ytrain, output_metadata