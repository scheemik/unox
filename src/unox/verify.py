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
        raise TypeError("Path must be a string.")
    if not os.path.exists(path):
        path0 = '..' + path
        if not os.path.exists(path0):
            path1 = '../' + path
            if not os.path.exists(path1):
                raise FileNotFoundError(f"Path {path} does not exist.")
            else:
                return path1
        else:
            return path0
    else:
        return path