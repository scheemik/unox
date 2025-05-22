import numpy as np
import os

def load_lats_lons(path='../datafiles/'):
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
    with open(path+'/lats.npy', 'rb') as f:
        lats = np.load(f)
    with open(path+'/lons.npy', 'rb') as f:
        lons = np.load(f)
    return lats, lons

def verify_path(path):
    """Verify that the path to the data files is correct.

    Checks if the path to the data files exists and is valid.
    If not, it raises an error.

    Parameters
    ----------
    path : str
        Relative path to the directory containing data files.

    Raises
    ------
    FileNotFoundError
        If the specified path does not exist.

    Returns
    -------
    path : str
        The verified path to the data files.

    Examples
    --------
    >>> verify_path()
    """
    if not os.path.exists(path):
        path = '../' + path
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path {path} does not exist.")
        else:
            return path
    else:
        return path

def show_available_data(path='original_sample_data/', verb=False):
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
    >>> data_files = show_available_data('original_sample_data/')
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

def recursive_paths(path):
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
    >>> path_list = recursive_paths('original_sample_data/')
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

def get_sample_data(stage=1, x_or_y='y', year=2019):
    """Get the path of a sample data file.

    Builds the path to a specific sample data file
    based on the stage, x_or_y, and year.

    Parameters
    ----------
    stage : int
        Stage of the data (1 or 2).
    x_or_y : str
        'x' or 'y' to specify the type of data.
    year : int
        Year of the data.
    
    Returns
    -------
    file_path : str
        Path to the sample data file.
    
    Examples
    --------
    >>> file_path = get_sample_data(stage=1, x_or_y='y', year=2019)
    '../sample_data/stage1/y/Y_2019.npy'
    """
    # Verify the stage and x_or_y values
    if stage not in [1, 2]:
        raise ValueError("Stage must be 1 or 2.")
    if x_or_y not in ['x', 'y']:
        raise ValueError("x_or_y must be 'x' or 'y'.")
    # Build the file path
    file_path = f'sample_data/stage{stage}/{x_or_y}/{x_or_y.upper()}_{year}.npy'
    # Verify the path
    file_path = verify_path(file_path)
    # Find the available data files
    data_files = show_available_data('sample_data/')
    # Check if the file exists
    if file_path not in data_files:
        raise FileNotFoundError(f"File {file_path} not found.")
    return file_path

def get_pred_data(stage=1, HPC_run='test_unet_601760', year=2019):
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

    Returns
    -------
    file_path : str
        Path to the prediction data file.

    Examples
    --------
    >>> file_path = get_pred_data(stage=1, HPC_run='test_unet_601760', year=2019)
    '../HPC_runs/test_unet_601760/stage1_output/pred_X_2019.npy'
    """
    # Verify the stage value
    if stage not in [1, 2]:
        raise ValueError("Stage must be 1 or 2.")
    # Build the file path
    file_path = f'HPC_runs/{HPC_run}/stage{stage}_output/pred_X_{year}.npy'
    # Verify the path
    file_path = verify_path(file_path)
    # Find the available data files
    data_files = show_available_data('HPC_runs/')
    # Check if the file exists
    if file_path not in data_files:
        raise FileNotFoundError(f"File {file_path} not found.")
    return file_path