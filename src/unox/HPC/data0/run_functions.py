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
    default_config = 'model_configs/sample_config.json',
    default_version = 1,
    verbose = True,
):
    """ Process command line arguments given to `run_model.py`.

        Parameters
        ----------
        cmd_args : `list`
            The list of command line arguments given to `run_model.py`.
            Assumes the arguments are:
            - arg 0: script name (i.e., `run_model.py`)
            - arg 1: savedir, the directory in which to save model outputs
            - arg 2: version, the version of the packages to import (0 or 1)
        default_config : `str`, optional
            The default config file to use if none is found in `cmd_args`.
            Default is 'model_configs/sample_config.json'.
        default_version : `int`, optional
            The default version to use if none is found in `cmd_args`.
            Default is 1.
        verbose : `bool`, optional
            Whether to print the processed command line arguments.
            Default is True.

        Returns
        -------
        savedir : `str`
            The path to the directory in which to save model outputs.
        config_dict : `dict`
            The model configuration dictionary.
        config_path : `str`
            The path to the configuration file used.
        version : `int`
            The version of the packages to use for running the model (0 or 1).
    """ 
    # Verify argument types
    if not isinstance(cmd_args, list):
        raise TypeError(f"(process_cmd_args) `cmd_args` must be a list. Got type: {type(cmd_args)}")
    if not isinstance(default_config, str):
        raise TypeError(f"(process_cmd_args) `default_config` must be a string. Got type: {type(default_config)}")
    if not isinstance(default_version, int):
        raise TypeError(f"(process_cmd_args) `default_version` must be an int. Got type: {type(default_version)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(process_cmd_args) `verbose` must be a bool. Got type: {type(verbose)}")
    
    # Load the first input argument: the save directory
    try:
        savedir = cmd_args[1]
    except:
        raise ValueError(f"(process_cmd_args) `cmd_args[1]` must be the save directory, but none was provided.")
    # Verify the savedir path
    if not isinstance(savedir, str):
        raise TypeError(f"(process_cmd_args) `savedir` (`cmd_args[1]`) must be a string. Got type: {type(savedir)}")
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

    # Use the save directory to load the config file
    config_path = f"{savedir}model_config.json"
    # Get the config dictionary (`get_config` verifies type of `config_path`)
    try:
        config_dict = get_config(config_path)
    except:
        config_dict = get_config(default_config)
    if verbose:
        print(f"\t     config_file: {config_path}")
    # If wasn't already present, write the config dictionary to a json file in `savedir``
    if not savedir in config_path:
        with open(f"{savedir}model_config.json", 'w') as file:
            file.write(json.dumps(config_dict, indent=4))

    # Load the third input argument: the version of the packages to use
    try:
        version = cmd_args[2]
    except:
        version = default_version 
    # Command line arguments are sometimes typed into a string
    if isinstance(version, str):
        try: 
            version = int(version)
        except:
            raise ValueError(f"(process_cmd_args) `version` could not be cast to an integer. Given: {version}")
    # Verify that `version` is a number
    if not verify_number(version):
        raise TypeError(f"(process_cmd_args) `version` (`cmd_args[3]`) must be a number. Got type: {type(version)}")
    else:
        version = int(version)
    if verbose:
        print(f"\targv[2], version: {version}")
    
    # If using the old version of the packages, create directories for staged output
    if version == 0:
        print(f"You have specified to use version {version} of the code, however, this version is not fully supported. Please use version 1 of the code, or make the necessary changes to support version {version}.")
        exit(0)
        stage1_dir = make_file_path(f"{savedir}stage1_output/")
        stage2_dir = make_file_path(f"{savedir}stage2_output/")
    
    return savedir, config_dict, config_path, version

def make_predictions_metadata_dict(
    savedir,
    config_path,
    config_dict,
    version,
    model_fmt,
):
    """ Create the dictionary of metadata for a run to be output to a dictionary.

        Parameters
        ----------
        savedir : `str`
            The path to the directory in which the data for this run is saved.
        config_path : `str`
            The path to the configuration JSON file.
        config_dict : `dict`
            The dictionary of the configuration file.
        version : `int`
            The version of the code used in this run (0 or 1).
        model_fmt : `str`
            The format in which to output the trained model for this run.
            Either 'h5', 'keras', or 'both'.

        Returns
        -------
        predictions_metadata : `dict`
            The output metadata dictionary.
    """
    # Verify argument types
    if not isinstance(savedir, str):
        raise TypeError(f"(make_predictions_metadata_dict) `savedir` must be a str. Got type: {type(savedir)}")
    if not isinstance(config_path, str):
        raise TypeError(f"(make_predictions_metadata_dict) `config_path` must be a str. Got type: {type(config_path)}")
    if not isinstance(config_dict, (str, type({}))):
        raise TypeError(f"(make_predictions_metadata_dict) `config_dict` must be a str or dict. Got type: {type(config_dict)}")
    if not isinstance(version, int):
        raise TypeError(f"(make_predictions_metadata_dict) `version` must be an int. Got type: {type(version)}")
    if not isinstance(model_fmt, str):
        raise TypeError(f"(make_predictions_metadata_dict) `model_fmt` must be a str. Got type: {type(model_fmt)}")

    # Create the metadata dictionary
    predictions_metadata = {
        'savedir': savedir,
        'config_path': config_path,
        'config_dict': config_dict,
        'version': version,
        'model_fmt': model_fmt,
        'train_years': {
            'stage1': [],
            'stage2': [],
        },
        'pred_years': {
            'stage1': [],
            'stage2': [],
        },
    }
    return predictions_metadata

def prepare_input(
    uarr,
    model_config,
    predictions_metadata,
    stage = 1,
):
    """ Prepare the input data for the model.

        Get the training data from the input NetCDF dataset as numpy arrays and concatenate them along the time dimension.

        Parameters
        ----------
        uarr : `unox.uarray`
            The dataset of the input NetCDF file.
        model_config : `str` or `dict`
            Path to the input configuration JSON file or a dictionary containing the configuration.
        predictions_metadata : `dict`
            The dictionary of metadata describing the output of a model run.
        stage : `int`
            The stage of the data to plot (1 or 2).

        Returns
        -------
        xtrain : `np.ndarray`
            Concatenated training input features.
        ytrain : `np.ndarray`
            Concatenated training target variables.
        predictions_metadata : `dict`
            The dictionary of metadata describing the output of a model run with values added for `train_years` and `unet_build_shape`.
    """
    # Verify argument types
    uarr._verify()
    # Verify model_config
    if not isinstance(model_config, type({})):
        if isinstance(model_config, str):
            try:
                model_config = get_config(model_config)
            except:
                raise ValueError(f"(prepare_input) `model_config` string argument could not be found as a file. Got: {model_config}")
        else:
            raise TypeError(f"(prepare_input) `model_config` must be a str or dict. Got type: {type(model_config)}.")
    # Verify predictions_metadata
    if not isinstance(predictions_metadata, type({})):
        raise TypeError(f"(prepare_input) `predictions_metadata` must be a dict. Got type: {type(predictions_metadata)}.")
    if 'dates' not in model_config:
        raise ValueError(f"(prepare_input) `model_config` must have a `dates` key containing the date information for preparing the input data.")
    if not isinstance(model_config['dates'], type({})):
        raise TypeError(f"(prepare_input) `model_config['dates']` must be a dict. Got type: {type(model_config['dates'])}.")
    for date_key in ['train_test_start', 'train_test_end', 'verification_start', 'verification_end', 'stage_2_start', 'stage_2_end']:
        if date_key not in model_config['dates']:
            raise ValueError(f"(prepare_input) `model_config['dates']` must have a `{date_key}` key for preparing the input data.")
        if not isinstance(model_config['dates'][date_key], str):
            raise TypeError(f"(prepare_input) `model_config['dates']['{date_key}']` must be a string. Got type: {type(model_config['dates'][date_key])}.")
    # Verify the stage and set the appropriate dates
    if stage == 1:
        x_s = 'x'
        start_date = model_config['dates']['train_test_start']
        end_date = model_config['dates']['train_test_end']
    elif stage == 2:
        x_s = 'x2'
        start_date = model_config['dates']['stage_2_start']
        end_date = model_config['dates']['stage_2_end']
    else:
        raise ValueError(f"(prepare_input) `stage` must be either 1 or 2. Got: {stage}")

    print(f"Preparing input data for stage {stage} of training.")
    print(f"\tstart_date: {start_date}")
    print(f"\tend_date: {end_date}")

    # Get the data arrays
    print(f"Getting array of x input data")
    xtrain, in_lats, in_lons, in_time = get_npy_from_netcdf(
        uarr.xr, 
        model_config, 
        start_date, 
        end_date, 
        x_or_y=x_s,
    )
    print(f"Getting array of y input data")
    ytrain, in_lats, in_lons, in_time = get_npy_from_netcdf(
        uarr.xr, 
        model_config, 
        start_date, 
        end_date, 
        x_or_y='y',
    )

    print(f"\tShape of xtrain: {xtrain.shape}")
    print(f"\tShape of ytrain: {ytrain.shape}")
    # Add the shape for which to build the unet input layer
    ## Important to note this here as the lat-lon grid of the data may change after calling `get_npy_from_netcdf()`
    predictions_metadata['unet_build_shape'] = xtrain.shape[1:]  # omit the first dimension (time)
    return xtrain, ytrain, predictions_metadata

