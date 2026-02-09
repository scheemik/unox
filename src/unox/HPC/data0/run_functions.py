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
    """ Process command line arguments given to `run_model.py`

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
            config_path : str
                The path to the configuration file used.
            version : int
                The version of the packages to use for running the model (0 or 1).
    """ 
    # Verify argument types
    if not isinstance(cmd_args, list):
        raise TypeError(f"(process_cmd_args) `cmd_args` must be a list. Got type: {type(cmd_args)}")
    
    # Load the first input argument: the save directory
    try:
        savedir = cmd_args[1]
    except:
        savedir = default_savedir
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
        print(f"\targv[3], version: {version}")
    
    # If using the old version of the packages, create directories for staged output
    if version == 0:
        stage1_dir = make_file_path(f"{savedir}stage1_output/")
        stage2_dir = make_file_path(f"{savedir}stage2_output/")
    
    return savedir, config_dict, config_path, version

def make_output_metadata_dict(
    savedir,
    config_path,
    config_dict,
    version,
    model_fmt,
):
    """ Creates the dictionary of metadata for a run to be output to a dictionary. 

        Parameters
        ----------
        savedir : str
            The path to the directory in which the data for this run is saved.
        config_path : str
            The path to the configuration JSON file. 
        config_dict : dict
            The dictionary of the configuration file.
        version : int
            The version of the code used in this run (0 or 1).
        n_epochs : int
            The number of epochs the model was run over.
        model_fmt : str
            The format in which to output the trained model for this run.
            Either 'h5', 'keras', or 'both'.
        split_year : int
            The year at which to split the training and validation data.
            Defaults to 2019.
        split_value : float
            The ratio with which the data was split between training and validation.
            For example, a value of 0.9 would give 90% to training and 10% to validation. 
        
        Returns
        -------
        output_metadata : dict
            The output metadata dictionary.
    """
    # Verify argument types
    if not isinstance(savedir, str):
        raise TypeError(f"(make_output_metadata_dict) `savedir` must be a str. Got type: {type(savedir)}")
    if not isinstance(config_path, str):
        raise TypeError(f"(make_output_metadata_dict) `config_path` must be a str. Got type: {type(config_path)}")
    if not isinstance(config_dict, (str, type({}))):
        raise TypeError(f"(make_output_metadata_dict) `config_dict` must be a str or dict. Got type: {type(config_dict)}")
    if not isinstance(version, int):
        raise TypeError(f"(make_output_metadata_dict) `version` must be an int. Got type: {type(version)}")
    if not isinstance(model_fmt, str):
        raise TypeError(f"(make_output_metadata_dict) `model_fmt` must be a str. Got type: {type(model_fmt)}")

    # Create the metadata dictionary
    output_metadata = {
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
    return output_metadata

def prepare_input(
    uarr,
    input_config,
    output_metadata,
    split_year = 2019,
    stage = 1,
):
    """ Prepare the input data for the model.

        Get the training data from the input NetCDF dataset as numpy arrays
        and concatenate them along the time dimension.

        Parameters
        ----------
        uarr : unox.uarray
            The dataset of the input NetCDF file.
        input_config : str or dict
            Path to the input configuration JSON file or a dictionary containing the configuration.
        output_metadata : dict
            The dictionary of metadata describing the output of a model run.
        split_year : int, optional
            The year at which to split the training and testing data.
            Defaults to 2019.
        stage : int
            The stage of the data to plot (1 or 2).
        
        Returns
        -------
        xtrain : np.ndarray
            Concatenated training input features.
        ytrain : np.ndarray
            Concatenated training target variables.
        output_metadata : dict
            The dictionary of metadata describing the output of a model run with values added for `train_years` and `unet_build_shape`.
    """
    # Verify argument types
    uarr._verify()
    # Verify input_config
    if not isinstance(input_config, (str, type({}))):
        raise TypeError(f"(prepare_input) `input_config` must be a str or dict. Got type: {type(input_config)}.")
    # Verify output_metadata
    if not isinstance(output_metadata, type({})):
        raise TypeError(f"(prepare_input) `output_metadata` must be a dict. Got type: {type(output_metadata)}.")
    # Verify split_year
    if not verify_number(split_year):
        raise TypeError(f"(get_npy_from_netcdf) `split_year` must be a number. Got type: {type(split_year)}")
    # Verify split_year is present in the dataset
    years = uarr._get_years()
    if split_year not in years:
        raise ValueError(f"(get_npy_from_netcdf) `split_year` must be a year present in `uarr`. Available years: {years}")
    if stage not in [1, 2]:
        raise ValueError(f"(set_of_maps) `stage` must be either 1 or 2. Got: {stage}.")

    # Create blank lists to hold x and y training data
    xtrain_list = []
    ytrain_list = []
    # Set parameters based on the stage
    if stage == 1:
        start_year = min(years)
        x_s = 'x'
        meta_stage = 'stage1'
    elif stage == 2:
        start_year = uarr.xr.attrs['stage_2_cutoff']+1
        x_s = 'x2'
        meta_stage = 'stage2'
    else:
        raise ValueError(f"(prepare_input) `stage` must be either 1 or 2. Got: {stage}")
    # Check to make sure that `split_year` is larger than `start_year`
    if split_year <= start_year:
        raise ValueError(f"(prepare_input) `split_year` ({split_year}) must be greater than `start_year` ({start_year})")
    # If before the split year, add x and y data to train lists
    for year in range(start_year, split_year):
        this_x_train_arr, in_lats, in_lons = get_npy_from_netcdf(uarr.xr, year, input_config, x_or_y=x_s)
        xtrain_list.append(this_x_train_arr)
        this_y_train_arr, in_lats, in_lons = get_npy_from_netcdf(uarr.xr, year, input_config, x_or_y='y')
        ytrain_list.append(this_y_train_arr)
        output_metadata['train_years'][meta_stage].append(year)
    # Check the shapes of the input arrays
    print(f"\tShape of first xtrain file: {xtrain_list[0].shape}")
    print(f"\tShape of first ytrain file: {ytrain_list[0].shape}")
    # Concatenate training data
    xtrain = np.concatenate(xtrain_list, axis=0)
    ytrain = np.concatenate(ytrain_list, axis=0)
    print("After concatenation:")
    print(f"\tShape of xtrain: {xtrain.shape}")
    print(f"\tShape of ytrain: {ytrain.shape}")
    # Add the shape for which to build the unet input layer
    ## Important to note this hear as the lat-lon grid of the data 
    ## may change after calling `get_npy_from_netcdf()`
    output_metadata['unet_build_shape'] = xtrain.shape[1:]  # omit the first dimension (time)
    return xtrain, ytrain, output_metadata

