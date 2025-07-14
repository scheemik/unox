import numpy as np
import xarray as xr
import warnings
import os
import re

def get_extent(xr_dataset=None,
               lats=None,
               lons=None,
               shift_lons=False):
    """Get the latitude and longitude extent of the given xarray dataset.

    Finds the maximum and minimum latitude and longitude values in the given dataset.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data of which to find the extent.
    lats : numpy.ndarray, optional
        The latitude values to use instead of those in the dataset.
    lons : numpy.ndarray, optional
        The longitude values to use instead of those in the dataset.
    shift_lons : bool, optional
        If True, shift the longitude values from the range [0, 360] to [-180, 180].
    
    Returns
    -------
    extent : tuple
        A tuple of np.float64 in the form (lat_min, lat_max, lon_min, lon_max).
    
    Examples
    --------
    >>> nox = xr.open_dataset('datafiles/nox_2019_t106_US.nc')
    >>> extent = get_extent(nox)
    (24.112, 58.878, -126.0, -59.625)
    
    >>> lats, lons= get_lats_lons(nox)
    >>> extent = get_extent(lats=lats, lons=lons)
    (24.112, 58.878, -126.0, -59.625)
    """
    # If no xarray dataset is provided, use the latitude and longitude values
    if isinstance(xr_dataset, type(None)):
        if isinstance(lats, type(None)) or isinstance(lons, type(None)):
            raise ValueError("Either xr_dataset or both lats and lons must be provided.")
        # Find the min and max lat and lon values
        lat_min = np.unique(np.min(lats))[0]
        lat_max = np.unique(np.max(lats))[0]
        lon_min = np.unique(np.min(lons))[0]
        lon_max = np.unique(np.max(lons))[0]
    else:
        # Verify the xr_dataset
        verify_dataset(xr_dataset)
        # Find the min and max lat and lon values
        # Use np.unique to ensure that the values are unique and take only the first value
        lat_min = np.unique(xr_dataset.lat.min().values)[0]
        lat_max = np.unique(xr_dataset.lat.max().values)[0]
        lon_min = np.unique(xr_dataset.lon.min().values)[0]
        lon_max = np.unique(xr_dataset.lon.max().values)[0]
    # Verify that latitude values are in the range [-90, 90]
    lat_max = verify_lat(lat_max)
    lat_min = verify_lat(lat_min)
    # Verify that longitude values are in the range [-180, 180]
    if shift_lons:
        lon_min = shift_lon(lon_min)
        lon_max = shift_lon(lon_max)
    lon_max = verify_lon(lon_max)
    lon_min = verify_lon(lon_min)
    # Return the extent as a tuple
    return (lat_min, lat_max, lon_min, lon_max)

def get_lats_lons(xr_dataset,
                  shift_lons=False):
    """Get the latitude and longitude values from the given dataset.

    Loads the latitude and longitude values from the given dataset
    and returns them as numpy arrays.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data to verify.

    Returns
    -------
    lats : numpy.ndarray
        Array of latitude values.
    lons : numpy.ndarray
        Array of longitude values.

    Examples
    --------
    >>> lats, lons = get_lats_lons()
    """
    # Verify the xr_dataset
    verify_dataset(xr_dataset)
    # Get the latitude and longitude values
    lats = xr_dataset.lat.values
    lons = xr_dataset.lon.values
    # Verify the latitude and longitude values
    map(verify_lat, lats)
    if shift_lons:
        lons = np.array(list(map(shift_lon, lons)))
    map(verify_lon, lons)
    return lats, lons

def get_latlon_resolution(xr_dataset,
                          shift_lons=False
                          ):
    """Get the latitude and longitude resolution of the given dataset.

    Calculates the resolution of coordinate values in the dataset
    to find the resolution in latitude and longitude separately.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data for which to find the coordinate resolution
    shift_lons : bool, optional
        If True, shift the longitude values from the range [0, 360] to [-180, 180].
    
    Returns
    -------
    lat_res : str
        The resolution in latitude.
    lon_res : str
        The resolution in longitude.

    Examples
    --------
    >>> nox = xr.open_dataset('datafiles/nox_2019_t106_US.nc')
    >>> lat_res, lon_res = get_latlon_resolution(nox)
    (0.25, 0.25)
    """
    # Verify the xr_dataset
    verify_dataset(xr_dataset)
    # Get the latitude and longitude values
    lats, lons = get_lats_lons(xr_dataset, shift_lons=shift_lons)
    # Calculate the resolution in latitude and longitude
    lat_res = np.unique(np.diff(lats))
    if len(lat_res) != 1:
        # Find the average and standard deviation of the latitude resolution
        lat_res = np.diff(lats)
        lat_res_mean = np.mean(lat_res)
        lat_res_std = np.std(lat_res)
        lat_res = f"{lat_res_mean} ± {lat_res_std}"
    else:
        lat_res = str(lat_res[0])
    lon_res = np.unique(np.diff(lons))
    if len(lon_res) != 1:
        # Find the average and standard deviation of the longitude resolution
        lon_res = np.diff(lons)
        lon_res_mean = np.mean(lon_res)
        lon_res_std = np.std(lon_res)
        lon_res = f"{lon_res_mean} ± {lon_res_std}"
    else:
        lon_res = str(lon_res[0])
    # Return the resolution in latitude and longitude
    return lat_res, lon_res

def verify_dataset(xr_dataset):
    """Verify that the given xarray dataset is valid.

    Checks to make sure the given dataset is of the expected type
    and contains the expected coordinates.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data to verify.
    """
    # Verify that xr_dataset is an xarray Dataset or DataArray
    if not isinstance(xr_dataset, xr.Dataset) and not isinstance(xr_dataset, xr.DataArray):
        raise TypeError("xr_dataset must be an xarray Dataset or DataArray.")
    # Verify that the dataset has lat and lon coordinates
    if 'lat' not in xr_dataset.coords or 'lon' not in xr_dataset.coords:
        raise ValueError("xr_dataset must have 'lat' and 'lon' coordinates.")
    # Verify that the dataset has the time coordinate
    if 'time' not in xr_dataset.coords:
        raise ValueError("xr_dataset must have 'time' coordinate.")

def verify_number(value):
    """Verify that the given value is a number.

    If the given value is a number that can be converted to
    an integer but is not a string or character, return True. 
    Otherwise, return False.

    Parameters
    ----------
    value : any
        The value to verify.

    Returns
    -------
    bool
        True if the value is a number, False otherwise.

    Examples
    --------
    >>> value = verify_number(5)
    True
    >>> value = verify_number("5")
    False
    >>> value = verify_number(np.nan)
    False
    """
    if isinstance(value, str) or isinstance(value, bytes):
        return False
    try:
        foo = int(value)
        return True
    except:
        return False

def clean_num_list(val_list):
    """Clean the list of values that cannot be converted to a number.

    For each value in the list, if it cannot be converted to a number, 
    all instances of that value are removed from the list.

    Parameters
    ----------
    val_list : list
        The list of values to clean.

    Returns
    -------
    return_list : list
        The cleaned list of values.

    Examples
    --------
    >>> val_list = clean_list([1, 2, 3, "4", 5])
    [1, 2, 3, 5]
    >>> val_list = clean_list([1, 2, 3, np.nan, None, np.inf, -np.inf])
    [1, 2, 3]
    """
    # Create an empty list to store cleaned values
    return_list = []
    for val in val_list:
        if verify_number(val):
            # Add this value to the return list
            return_list.append(val)
    # If the list is empty after removing invalid numbers, raise an error
    if len(return_list) == 0:
        raise ValueError("No valid numbers in the input list.")
    return return_list

def verify_lat(lat_val):
    """Verify that the given latitude value is valid.

    If the given latitude value is within the range [-90, 90],
    return that value. Otherwise, raise a ValueError.

    Parameters
    ----------
    lat_val : float
        The latitude value to verify.

    Returns
    -------
    lat_val : float
        The verified latitude value.

    Examples
    --------
    >>> lat_val = verify_lat(45.0)
    45.0
    >>> lat_val = verify_lat(-100.0)
    ValueError: Latitude value must be in the range [-90, 90].
    """
    if not verify_number(lat_val):
        raise ValueError("Latitude value must be a number.")
    if np.isnan(lat_val):
        raise ValueError("Latitude value must not be NaN.")
    if lat_val < -90 or lat_val > 90:
        raise ValueError(f"Latitude value must be in the range [-90, 90], lat_val = {lat_val}.")
    return lat_val

def verify_lon(lon_val):
    """Verify that the given longitude value is valid.

    If the given longitude value is within the range [-180, 180],
    return that value. Otherwise, raise a ValueError.

    Parameters
    ----------
    lon_val : float
        The longitude value to verify.

    Returns
    -------
    lon_val : float
        The verified longitude value.

    Examples
    --------
    >>> lon_val = verify_lon(45.0)
    45.0
    >>> lon_val = verify_lon(-200.0)
    ValueError: Longitude value must be in the range [-180, 180].
    """
    if not verify_number(lon_val):
        raise ValueError("Longitude value must be a number.")
    if np.isnan(lon_val):
        raise ValueError("Longitude value must not be NaN.")
    if lon_val < -180 or lon_val > 180:
        raise ValueError(f"Longitude value must be in the range [-180, 180], lon_val = {lon_val}.")
    return lon_val

def shift_lon(lon_value):
    """Shift the given longitude value from the range [0, 360] to [-180, 180].

    If the given longitude value is within the range [0, 360],
    return that value shifted to the range [-180, 180].
    Otherwise, raise a ValueError.

    Parameters
    ----------
    lon_value : float
        The longitude value to shift.

    Returns
    -------
    lon_value : float
        The shifted longitude value.

    Examples
    --------
    >>> lon_value = shift_lon(45.0)
    -315.0
    >>> lon_value = shift_lon(-200.0)
    ValueError: Longitude value must be in the range [0, 360].
    """
    if not verify_number(lon_value):
        raise ValueError("Longitude value must be a number.")
    if np.isnan(lon_value):
        raise ValueError("Longitude value must not be NaN.")
    if lon_value < 0 or lon_value > 360:
        raise ValueError(f"Longitude value must be in the range [0, 360], lon_value = {lon_value}.")
    return lon_value - 180

def get_vminmax(arrays):
    """Get the minimum and maximum values across the given arrays.

    Flattens and concatenates the given arrays and returns the minimum
    and maximum values, ignoring NaN values.

    Parameters
    ----------
    arrays : list of numpy.ndarray
        The arrays to get the minimum and maximum values from.

    Returns
    -------
    vmin : float
        The minimum value across the arrays.
    vmax : float
        The maximum value across the arrays.

    Examples
    --------
    >>> arrays = [np.array([1, 2, 3]), np.array([4, 5, 6])]
    >>> vmin, vmax = get_vminmax(arrays)
    (1, 6)
    """
    # Flatten and concatenate the arrays
    flat_arrays = np.concatenate([arr.flatten() for arr in arrays])
    # Get the minimum and maximum values
    #   Catch warning for all-NaN arrays
    with warnings.catch_warnings():
        warnings.filterwarnings('error', category=RuntimeWarning)
        try:
            vmin = np.nanmin(flat_arrays)
            vmax = np.nanmax(flat_arrays)
        except RuntimeWarning as e:
            raise ValueError(f"{e}. Does input array contain any non-NaN values?")
    return vmin, vmax

def get_max_abs_val(val_list):
    """Get the maximum absolute value from the given list.

    Removes invalid numbers from the given list of values, then takes the 
    absolute value of the remaining values, and returns the largest.

    Parameters
    ----------
    val_list : list of numbers or numpy.ndarray
        The list of values to get the maximum absolute value from.

    Returns
    -------
    max_abs : float
        The maximum absolute value of the given values.

    Examples
    --------
    >>> max_abs = get_max_abs_val(-11, 6)
    6
    >>> vmin, vmax = get_vminmax([np.array([1, 2, -3]), np.array([4, 5, -6])])
    >>> max_abs = get_max_abs_val(vmin, vmax)
    5
    """
    # Clean the list of values
    val_list = clean_num_list(val_list)
    # Convert the input values to a numpy array, if it is not already
    val_list = np.array(val_list)
    return np.max(np.abs(val_list))

def restrict_domain(arrs_to_restrict, lats, lons, restricting_data):
    """Restrict the domain of the given arrays

    Restricts the domain of the given arrays to the same extent as that 
    in the restricting data. The values of lats, lons are the latitude and
    longitude values of the arrays to restrict.

    Parameters
    ----------
    arrs_to_restrict : list of numpy.ndarray
        The arrays to restrict in latitude and longitude.
    lats : numpy.ndarray
        The latitude values of the arrays to restrict.
    lons : numpy.ndarray
        The longitude values of the arrays to restrict.
    restricting_data : xarray.Dataset or xarray.DataArray
        The dataset to restrict the arrays to.
    
    Returns
    -------
    arrs_to_return : list of numpy.ndarray
        The restricted arrays.
    lat_r : numpy.ndarray
        The latitude values of the restricting data.
    lon_r : numpy.ndarray
        The longitude values of the restricting data.
    
    Examples
    --------
    >>> stage1 = np.load(get_pred_data(stage=1, 'HPC_run'='test_unet_601760', 'year'=2019))
    >>> lats, lons = load_lats_lons()
    >>> nox = xr.open_dataset('datafiles/nox_2019_t106_US.nc')
    >>> stage1_restricted = restrict_domain([nox], lats, lons, nox)
    """
    # Get the latitude and longitude values from the restricting data
    lat_r, lon_r = get_lats_lons(restricting_data)

    # I feel like this should work, but I can't figure it out right now
    this_extent = get_extent(restricting_data)

    # Find indices of lats and lons that are in the restricting data
    latmin = np.where(np.abs(lats-np.min(lat_r))<0.1)[0][0]
    latmax = np.where(np.abs(lats-np.max(lat_r))<0.1)[0][0] + 1
    lonmin = np.where(np.abs(lons-np.min(lon_r))<0.1)[0][0]
    lonmax = np.where(np.abs(lons-np.max(lon_r))<0.1)[0][0] + 1

    # Narrow the data to just this region
    arrs_to_return = []
    for arr in arrs_to_restrict:
        arrs_to_return.append(arr[:,latmin:latmax,lonmin:lonmax,:])
    return arrs_to_return, lat_r, lon_r

def verify_npy(array):
    """Determine if a variable or file holds a valid numpy array.

    If a numpy array or a path to a file containing a numpy array was passed,
    return True. Otherwise, raise a TypeError, ValueError or FileNotFoundError.

    Parameters
    ----------
    array : numpy.array or string
        A numpy array or a path to a file containing a numpy array.

    Returns
    -------
    nparray : np.ndarray
        The array being passed or pointed to as a
        np.ndarray.

    Examples
    --------
    >>> import numpy as np
    >>> from tempfile import NamedTemporaryFile
    >>> arr = np.array([1, 2, 3])
    >>> verify_npy(arr)
    array([1, 2, 3])

    >>> with NamedTemporaryFile(suffix=".npy", delete=False) as f:
    ...     np.save(f.name, arr)
    ...     verify_npy(f.name)
    array([1, 2, 3])

    >>> with NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
    ...     _ = f.write("1,2,3\\n4,5,6")
    >>> loaded = verify_npy(f.name)
    >>> isinstance(loaded, np.ndarray)
    True

    >>> verify_npy(42)
    Traceback (most recent call last):
        ...
    TypeError: Not a numpy array.

    >>> verify_npy("nonexistent/path.npy")
    Traceback (most recent call last):
        ...
    FileNotFoundError: File does not exist.

    >>> import os
    >>> os.makedirs("some/folder", exist_ok=True)
    >>> verify_npy("some/folder")
    Traceback (most recent call last):
        ...
    FileNotFoundError: Path leads to a folder.

    >>> with NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
    ...     pass  # Empty file
    >>> verify_npy(f.name)
    Traceback (most recent call last):
        ...
    ValueError: File does not contain a readable numpy array.
    """
    if isinstance(array, str):
        if os.path.isdir(array):
            raise FileNotFoundError("Path leads to a folder.")
        if not os.path.isfile(array):
            raise FileNotFoundError("File does not exist.")
        ext = os.path.splitext(array)[1].lower()
        try:
            if ext == ".npy":
                return np.load(array, allow_pickle=True)
            elif ext in [".txt", ".csv"]:
                try:
                    nparray =  np.loadtxt(array, delimiter=",")
                    if len(nparray) == 0:
                        raise ValueError("File does not contain a readable numpy array.")
                    return nparray
                except Exception:
                    try:
                        nparray = np.genfromtxt(array, delimiter=",", skip_header=1)
                        if len(nparray) == 0:
                            raise ValueError("File does not contain a readable numpy array.")
                        return nparray
                    except Exception as e:
                        raise ValueError("File does not contain a readable numpy array.")
            else:
                raise TypeError("File does not contain a readable numpy array.")
        except Exception:
            raise ValueError("File does not contain a readable numpy array.")
    elif isinstance(array, np.ndarray):
        return array
    else:
        raise TypeError("Not a numpy array.")

def get_num_from_string(str):
    """Extract numbers from a string.

    If the string contains numbers, return those numbers in a list.
    Otherwise, raise a ValueError.

    Parameters
    ----------
    str : str
        The string to extract the number from.

    Returns
    -------
    nums : list of int or float
        A list of numbers extracted from the string.

    Examples
    --------
    >>> num = get_num_from_string("There are 42.0 apples and 3 oranges.")
    [42, 3]
    >>> num = get_num_from_string("No number here")
    ValueError: No number found in the string.
    """
    # Verify that the input is a string
    if not isinstance(str, type('')):
        raise TypeError("Input must be a string.")
    # Find all numbers in the string using regular expressions
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", str)
    # Convert the numbers to integers or floats
    nums = [float(num) if '.' in num else int(num) for num in nums]
    return nums

def increment_month(month, increment):
    """Increment the month by a given number of months.

    Increments the month by the given number of months, wrapping around
    if the increment goes beyond December (12).

    Parameters
    ----------
    month : int or str
        The month to increment (1 for January, 2 for February, ..., 12 for December).
    increment : int or str
        The number of months to increment by.

    Returns
    -------
    new_month : int or str
        The new month after incrementing. The type will match the type of `month`.

    Examples
    --------
    >>> increment_month(1, 2)
    3
    >>> increment_month(11, 3)
    2
    >>> increment_month('5', '7')
    '12'
    """
    # Note return type
    return_type = type(month)
    # Ensure month is valid
    if isinstance(month, str):
        try:
            month = int(month)
        except:
            raise TypeError("Month must be an integer between 1 and 12.")
    if not isinstance(month, int) or month < 1 or month > 12:
        raise ValueError("Month must be an integer between 1 and 12.")
    
    # Ensure increment is an integer
    if isinstance(increment, str):
        try:
            increment = int(increment)
        except:
            raise TypeError("Increment must be an integer.")
    if not isinstance(increment, int):
        raise TypeError("Increment must be an integer.")
    
    # Calculate the new month
    new_month = (month - 1 + increment) % 12 + 1
    
    # Return the new month in the same type as the input
    if return_type == str:
        return str(new_month)
    else:
        return new_month
