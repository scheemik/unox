import os

def verify_path(
    path,
):
    """Verify that the filepath exists.

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
    # Verify argument types
    if not isinstance(path, str):
        raise TypeError(f"(verify_path) `path` must be a string. Got type: {type(path)}")
    if not os.path.exists(path):
        path0 = '..' + path
        if not os.path.exists(path0):
            path1 = '../' + path
            if not os.path.exists(path1):
                raise FileNotFoundError(f"(verify_path) The path {path} does not exist.")
            else:
                return path1
        else:
            return path0
    else:
        return path

def remove_non_empty_directory(
    base_dir,
):
    """Remove a non-empty directory and all its contents.

    This function will recursively delete all files and directories in the given path.

    Parameters
    ----------
    base_dir : str
        Relative path to the directory to be removed.
    """
    # Verify the path
    top = verify_path(base_dir)
    # Check if the path is a directory
    if not os.path.isdir(top):
        raise ValueError(f"(remove_non_empty_directory) The path {top} is not a directory.")
    # Recursively remove all files and directories in the given path
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            print(f'Removing file: {os.path.join(root, name)}')
            os.remove(os.path.join(root, name))
        for name in dirs:
            print(f'Removing directory: {os.path.join(root, name)}')
            os.rmdir(os.path.join(root, name))
    # Finally remove the top directory itself
    os.rmdir(top)  

def make_file_path(
    path,
):
    """Create a file path.

    If the given path doesn't exist, create the specified directory structure.

    Parameters
    ----------
    path : str
        Relative path to make.

    Returns
    -------
    path : str
        The verified path to the data files.

    Examples
    --------
    >>> make_file_path('datafiles/some/more/data/a_file.txt')
    'datafiles/some/more/data/'
    """
    # Verify argument types
    if not isinstance(path, str):
        raise TypeError(f"(make_file_path) `path` must be a string. Got type: {type(path)}")
    # If the path contains a file extension, remove the full file name
    if '.' in path.split('/')[-1]:
        dir_path = os.path.dirname(path)
    else:
        dir_path = path
    # Verify the path
    try:
        dir_path = verify_path(dir_path)
    except FileNotFoundError:
        # If the path doesn't exist, create it
        pass
    if not os.path.exists(dir_path):
        # Use the `exist_ok=True` argument to avoid raising an error 
        # if the path (or some of the path) already exists
        os.makedirs(dir_path, exist_ok=True)
    # Verify the path
    dir_path = verify_path(dir_path)
    return dir_path