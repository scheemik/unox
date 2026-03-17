import numpy as np
import glob 

from data0.paths import verify_path
from utils.data_split import data_split
from data0.config import get_config
from data0.verify_dtype import verify_number

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
        uarr : `unox.uarray`
            The dataset of the input NetCDF file.
        input_config : `str` or `dict`
            Path to the input configuration JSON file or a dictionary containing the configuration.
        output_metadata : `dict`
            The dictionary of metadata describing the output of a model run.
        split_year : `int`, optional
            The year at which to split the training and validation data.
            Defaults to 2019.
        stage : `int`, optional
            The stage of the data to plot (1 or 2).

        Returns
        -------
        xtrain : `np.ndarray`
            Concatenated training input features.
        ytrain : `np.ndarray`
            Concatenated training target variables.
        output_metadata : `dict`
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

    # Get the input configuration file
    if isinstance(input_config, type({})):
        config_dict = input_config
    else:
        config_dict = get_config(input_config)

    # Load the input files
    inputfiles = config_dict['input_set']
    # Assemble the file paths
    x_files_path = f"inputfiles/{inputfiles}/stage{stage}/x/"
    y_files_path = f"inputfiles/{inputfiles}/stage{stage}/y/"
    # Ensure the directories exist
    x_files_path = verify_path(x_files_path)
    y_files_path = verify_path(y_files_path)
    # Load and sort the files
    x_files = sorted(glob.glob(f"inputfiles/{inputfiles}/stage{stage}/x/X_20*.npy"))
    y_files = sorted(glob.glob(f"inputfiles/{inputfiles}/stage{stage}/y/Y_20*.npy"))
    print("")
    print(f"\tNumber of x_files: {len(x_files)}")
    print(f"\tNumber of y_files: {len(y_files)}")

    # Decide on split index based on stage
    if stage == 1:
        split_index = 14
        meta_stage = 'stage1'
    elif stage == 2:
        split_index = 5
        meta_stage = 'stage2'
    else:
        raise ValueError("Stage must be 1 or 2.")
    # Gather just the training files
    xtrain_files, ytrain_files = x_files[:split_index], y_files[:split_index]
    # Check the shapes of the input arrays
    print(f"\tShape of first xtrain file: {np.load(xtrain_files[0]).shape}")
    print(f"\tShape of first ytrain file: {np.load(ytrain_files[0]).shape}")
    # Concatenate training data
    xtrain = np.concatenate([ np.load(s) for s in xtrain_files], axis=0)
    ytrain = np.concatenate([ np.load(s) for s in ytrain_files], axis=0)
    print("After concatenation:")
    print(f"\tShape of xtrain: {xtrain.shape}")
    print(f"\tShape of ytrain: {ytrain.shape}")

    # Get years from the xtrain files
    meta_years = []
    for file in xtrain_files:
        # Get the file name (after last slash in file path)
        foo = file.split('/')[-1]
        # Get just the digits in the file name
        bar = ''.join(char for char in foo if char.isdigit())
        # Add as an int to the list
        meta_years.append(int(bar))
    output_metadata['train_years'][meta_stage] = meta_years

    # Add the shape for which to build the unet input layer
    ## Important to note this hear as the lat-lon grid of the data 
    ## may change after calling `get_npy_from_netcdf()`
    output_metadata['unet_build_shape'] = xtrain.shape[1:]  # omit the first dimension (time)

    return xtrain, ytrain, output_metadata