import numpy as np
import xarray as xr
import warnings

def get_extent(xr_dataset,
               shift_lons=False):
    """Get the latitude and longitude extent of the given xarray dataset.

    Finds the maximum and minimum latitude and longitude values in the given dataset.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data of which to find the extent.
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
    """
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

# def compare_lats_lons((lats1, lons1), (lats2, lons2)):

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