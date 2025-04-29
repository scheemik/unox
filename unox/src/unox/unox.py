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

def show_available_data(path='original_sample_data/'):
    """Print a list of available data in the given directory.
    
    For the given path, this function will print all the files in the directory.

    Parameters
    ----------
    path : str
        Relative path to the directory containing data files.

    Returns
    -------
    data_files : list
        List of file paths in the given directory.

    Examples
    --------
    >>> data_files = show_available_data('original_sample_data/')
    """
    # Check if the path exists
    if not os.path.exists(path):
        try:
            path = '../' + path
            os.path.exists(path) == True
        except:
            print(f"Path {path} does not exist.")
            return []
    # Recursively get all files in the directory
    data_files = recursive_paths(path)
    # Print the file paths
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
                path_list.append(this_path)
        else:
            # If the entry is a file, add it to the list
            path_list.append(full_path)
    return path_list