import numpy as np
import os
from datetime import datetime

from unox.HPC.data0.verify_path import verify_path

def time_this(func):
    """
    A decorator which can be applied to a function to print the execution time.

    Parameters
    ----------
    func : function
        The function for which to time.

    Returns
    -------
    None

    Examples
    --------
    @time_this
    def my_function():
        # Do some calculations
        ...
        return result
    >>> my_function()
    Function my_function executed in 2.91s
    """
    def wrap_func(*args, **kwargs):
        # Get the time at the start of the execution
        t1 = datetime.now()
        # Execute the function
        result = func(*args, **kwargs)
        # Get the time at the end of the execution
        t2 = datetime.now()
        # Calculate the difference and output the execution time
        print(f'\tFunction {func.__name__!r} execution time: {t2-t1}')
        return result
    return wrap_func

def load_lats_lons(
    path='datafiles/',
    ):
    """Load latitude and longitude data from files.

    Loads arrays of latitude and longitude values that cover 
    the region of interest.

    Parameters
    ----------
    path : str
        Relative path to the directory containing data files.

    Returns
    -------
    lats : numpy.ndarray
        Array of latitude values.
    lons : numpy.ndarray
        Array of longitude values.

    Examples
    --------
    >>> lats, lons = load_lats_lons()
    """
    # Verify the paths
    lat_path = verify_path(path+'lats.npy')
    lon_path = verify_path(path+'lons.npy')
    with open(lat_path, 'rb') as f:
        lats = np.load(f)
    with open(lon_path, 'rb') as f:
        lons = np.load(f)
    return lats, lons

def show_available_data(
    path='inputfiles/no2_sample_input/', 
    verb=False,
    ):
    """Print a list of available data in the given directory.
    
    For the given path, this function will print all the files in the directory.

    Parameters
    ----------
    path : str
        Relative path to the directory containing data files.
    verb : bool
        Verbose mode. If True, print the file paths. Defaults to False.

    Returns
    -------
    data_files : list
        List of file paths in the given directory.

    Examples
    --------
    >>> data_files = show_available_data('inputfiles/no2_sample_input/')
    ['inputfiles/no2_sample_input/stage1/y/Y_2019.npy',
     'inputfiles/no2_sample_input/stage1/y/Y_2005.npy',
     'inputfiles/no2_sample_input/stage1/y/Y_2006.npy',
     ...
     'inputfiles/no2_sample_input/stage2/x/X_2014.npy',
     'inputfiles/no2_sample_input/stage2/x/X_2015.npy']
    """
    # Check if the path exists
    path = verify_path(path)
    # Recursively get all files in the directory
    data_files = recursive_paths(path)
    # Print the file paths, if Verbose mode is enabled
    if verb:
        for data_file in data_files:
            print(data_file)
    return data_files

def recursive_paths(
    path,
    ):
    """Create list recursively of all files in the given path.

    Calls itself recursively to get all files in the given path.
    Assumes the path is a directory that exists, as is confirmed
    when called from show_available_data()

    Parameters
    ----------
    path : str
        Relative path to the directory containing data files.

    Returns
    -------
    path_list : list
        List of file paths in the given directory.

    Examples
    --------
    >>> path_list = recursive_paths('datafiles')
    ['datafiles/README.md',
     'datafiles/concatenate.py',
     'datafiles/download_era5.sh',
     ...
     'datafiles/sample_data/daily_42602_2019.csv',
     'datafiles/sample_data/nox_2019_t106_US.nc']
    """
    # Create an empty list in which to store the paths
    path_list = []
    # Iterate through all entries in the directory
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            # If the entry is a directory, call this function recursively
            for this_path in recursive_paths(full_path):
                # Exclude hidden files, that is, where they start with a `.`
                #   after the last `/` in the path
                if not this_path.split('/')[-1].startswith('.'):
                    path_list.append(this_path)
        else:
            # If the entry is a file, add it to the list
            # Exclude hidden files, that is, where they start with a `.`
            #   after the last `/` in the path
            if not full_path.split('/')[-1].startswith('.'):
                path_list.append(full_path)
    return path_list

def get_input_data(
    stage=1, 
    x_or_y='y', 
    year=2019,
    input_set='no2_sample_input',
    path_prefix='',
    ):
    """Get the path of a input data file.

    Builds the path to a specific input data file
    based on the stage, x_or_y, and year.

    Parameters
    ----------
    stage : int
        Stage of the data (1 or 2).
    x_or_y : str
        'x' or 'y' to specify the type of data.
    year : int
        Year of the data.
    input_set : str
        Name of the directory under `inputfiles/` containing the data files.
    path_prefix : str
        Prefix to the path to the directory containing data files.
    
    Returns
    -------
    file_path : str
        Path to the input data file.
    
    Examples
    --------
    >>> file_path = get_input_data(stage=1, x_or_y='y', year=2019)
    '../inputfiles/no2_sample_input/stage1/y/Y_2019.npy'
    """
    # Verify the stage and x_or_y values
    if stage not in [1, 2]:
        raise ValueError("Stage must be 1 or 2.")
    if x_or_y not in ['x', 'y']:
        raise ValueError("x_or_y must be 'x' or 'y'.")
    # Build the file path
    file_path = f'{path_prefix}inputfiles/{input_set}/stage{stage}/{x_or_y}/{x_or_y.upper()}_{year}.npy'
    # Verify the path
    file_path = verify_path(file_path)
    # Find the available data files
    data_files = show_available_data(f'{path_prefix}inputfiles/{input_set}/')
    # Check if the file exists
    if file_path not in data_files:
        raise FileNotFoundError(f"File {file_path} not found.")
    return file_path

def get_one_input_var_array(
    var,
    **kwargs,
    ):
    """
    Get the array of a single input variable for a given year.

    Parameters
    ----------
    var : str
        Name of the variable to get.
    **kwargs : dict
        Additional keyword arguments to pass to `get_input_data()`.
        Should include `stage`, `year`, and `input_set`.
    
    Returns
    -------
    var_array : numpy.ndarray
        Array of the specified variable.
    var_index : int
        Index of the specified variable in the input data array.
    """
    # Determine if the variable is an x or y variable
    from unox.input import x_or_y_var, input_vars_dict
    x_or_y = x_or_y_var(var)
    # Get the file path
    file_path = get_input_data(x_or_y=x_or_y, **kwargs)
    # Load the array
    input_array = np.load(file_path)
    # Determine which var list `var` is in and at which index
    for key in input_vars_dict.keys():
        if var in input_vars_dict[key][f'{x_or_y}_vars']:
            var_index = input_vars_dict[key][f'{x_or_y}_vars'].index(var)
            var_array = input_array[:, :, :, var_index]
            return var_array, var_index
    raise ValueError(f"Variable '{var}' not found in input_vars_dict: {input_vars_dict}")

def get_one_t_input_var_array(
    var,
    this_date,
    **kwargs,
    ):
    """
    Get an array of a single variable at the given date from the given input file.

    Parameters
    ----------
    var : str
        Name of the variable to get.
    this_date : np.datetime64 or str
        Date and time to select from the data file.
        Expected format is 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DD'.
    **kwargs : dict
        Additional keyword arguments to pass to `get_input_data()`.
        Should include `var`, `stage`, and `input_set`.
    
    Returns
    -------
    var_array : numpy.ndarray
        Array of the specified variable at the given date.
    """
    # Get the year from the date
    from unox.data import get_YMD_from_date, get_DOY
    year, month, day = get_YMD_from_date(this_date)
    # Get the input array for the year
    year_array, index = get_one_input_var_array(var, year=year, **kwargs)
    # Get the DOY from the date
    doy = get_DOY(this_date)
    # Return the array for that date
    return year_array[doy, :, :]

def get_pred_data(
    stage=1, 
    HPC_run='no2_example_run', 
    year=2019,
    path_prefix='',
    ):
    """Get the path of a prediction data file.

    Builds the path to a specific prediction data file
    based on the stage, HPC_run ID, and year.

    Parameters
    ----------
    stage : int
        Stage of the data (1 or 2).
    HPC_run : str
        ID of the HPC run.
    year : int
        Year of the data.
    path_prefix : str
        Prefix to the path to the directory containing data files.

    Returns
    -------
    file_path : str
        Path to the prediction data file.

    Examples
    --------
    >>> file_path = get_pred_data(stage=1, HPC_run='no2_example_run', year=2019)
    '../HPC_runs/no2_example_run/stage1_output/pred_X_2019.npy'
    """
    # Verify the stage value
    if stage not in [1, 2]:
        raise ValueError("Stage must be 1 or 2.")
    # Build the file path
    file_path = f'{path_prefix}HPC_runs/{HPC_run}/stage{stage}_output/pred_X_{year}.npy'
    # Verify the path
    file_path = verify_path(file_path)
    # Find the available data files
    data_files = show_available_data(f'{path_prefix}HPC_runs/')
    # Check if the file exists
    if file_path not in data_files:
        raise FileNotFoundError(f"File {file_path} not found.")
    return file_path

def interpret_user_input(
    user_input,
):
    """Interprets a yes/no input from the user.

    Takes input from prompting the user for a yes/no input and returns True/False appropriately.

    Parameters
    ----------
    user_input : str
        The input the user entered.

    Returns
    -------
    bool
        True if the user input is 'y' or 'yes', False if 'n' or 'no'.

    Examples
    --------
    >>> proceed = interpret_user_input(input('Do you wish to continue? (y/n): '))
    Do you wish to continue? (y/n): y
    >>> proceed
    True
    """
    # Verify argument types
    if not isinstance(user_input, str):
        raise TypeError(f"user_input must be a string. Got type: {type(user_input)}")
    # Get user input
    while True:
        input_yn = user_input.strip().lower()
        if input_yn in ['y', 'yes']:
            return True
        elif input_yn in ['n', 'no']:
            return False
        else:
            raise ValueError(f"Invalid input: {user_input}. Please enter 'y' or 'n'.")