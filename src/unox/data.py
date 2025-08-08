import numpy as np
import xarray as xr
import pandas as pd
import warnings
import os
import re
from datetime import datetime

from unox import unox

# Define the default latitude and longitude extents for this project
DEFAULT_LAT_MIN = 11
DEFAULT_LAT_MAX = 75
DEFAULT_LON_MIN = -175
DEFAULT_LON_MAX = -39
DEFAULT_EXTENT = [DEFAULT_LAT_MIN, DEFAULT_LAT_MAX, DEFAULT_LON_MIN, DEFAULT_LON_MAX]

def get_extent(
    xr_dataset=None,
    lats=None,
    lons=None,
    shift_lons=False,
    check_time=True,
    ):
    """Get the latitude and longitude extent of the given xarray dataset.

    Finds the maximum and minimum latitude and longitude values in the given dataset.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray, optional
        The xarray data of which to find the extent.
    lats : numpy.ndarray, optional
        The latitude values to use instead of those in the dataset.
    lons : numpy.ndarray, optional
        The longitude values to use instead of those in the dataset.
    shift_lons : bool or string, optional
        If True, shift the longitude values from the range [0, 360] to [-180, 180].
        If 'ID_centered', shift from [-180, 180] to [0, 360].
    check_time : bool, optional
        If True, verify that the dataset has a 'time' coordinate.
    
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
        # Shift the longitude values if specified
        if shift_lons == 'ID_centered':
            lons = shift_lon_arr(lons, PM_centered=False)
        elif shift_lons:
            lons = shift_lon_arr(lons, PM_centered=True)
        lon_min = np.unique(np.min(lons))[0]
        lon_max = np.unique(np.max(lons))[0]
    else:
        # Verify the xr_dataset
        xr_dataset = verify_dataset(xr_dataset, check_time=check_time, shift_lons=shift_lons)
        # Find the min and max lat and lon values
        # Use np.unique to ensure that the values are unique and take only the first value
        lat_min = np.unique(xr_dataset.lat.min().values)[0]
        lat_max = np.unique(xr_dataset.lat.max().values)[0]
        # Shift the longitude values if specified
        if shift_lons == 'ID_centered':
            lons = shift_lon_arr(xr_dataset.lon.values, PM_centered=False)
        elif shift_lons:
            lons = shift_lon_arr(xr_dataset.lon.values, PM_centered=True)
        else:
            lons = xr_dataset.lon.values
        lon_min = np.unique(lons.min())[0]
        lon_max = np.unique(lons.max())[0]
    # Verify that latitude values are in the range [-90, 90]
    lat_max = verify_lat(lat_max)
    lat_min = verify_lat(lat_min)
    lon_max = verify_lon(lon_max)
    lon_min = verify_lon(lon_min)
    # Return the extent as a tuple
    return (lat_min, lat_max, lon_min, lon_max)

def get_lats_lons(
    xr_dataset,
    shift_lons=False,
    ):
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
    xr_dataset = verify_dataset(xr_dataset, shift_lons=shift_lons)
    # Get the latitude and longitude values
    lats = xr_dataset.lat.values
    lons = xr_dataset.lon.values
    # Verify the latitude and longitude values
    map(verify_lat, lats)
    if shift_lons:
        lons = np.array(shift_lon_arr(lons))
    map(verify_lon, lons)
    return lats, lons

def get_latlon_resolution(
    xr_dataset=None,
    lats=None,
    lons=None,
    shift_lons=False,
    ):
    """Get the latitude and longitude resolution of the given dataset.

    Calculates the resolution of coordinate values in the dataset
    to find the resolution in latitude and longitude separately.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray, optional
        The xarray data of which to find the extent.
    lats : numpy.ndarray, optional
        The latitude values to use instead of those in the dataset.
    lons : numpy.ndarray, optional
        The longitude values to use instead of those in the dataset.
    shift_lons : bool or string, optional
        If True, shift the longitude values from the range [0, 360] to [-180, 180].
        If 'ID_centered', shift from [-180, 180] to [0, 360].
    
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
    # If given an xarray dataset
    if not isinstance(xr_dataset, type(None)):
        # Verify the xr_dataset
        xr_dataset = verify_dataset(xr_dataset, shift_lons=shift_lons)
        # Get the latitude and longitude values
        lats, lons = get_lats_lons(xr_dataset, shift_lons=shift_lons)
    # Calculate the resolution in latitude and longitude
    ## Make sure to sort the values first 
    lat_res = np.unique(np.diff(np.sort(lats)))
    if len(lat_res) != 1:
        # Find the average and standard deviation of the latitude resolution
        ## Make sure to sort the values first 
        lat_res = np.diff(np.sort(lats))
        lat_res_mean = np.mean(lat_res)
        lat_res_std = np.std(lat_res)
        lat_res = f"{lat_res_mean} ± {lat_res_std}"
    else:
        lat_res = str(lat_res[0])
    ## Make sure to sort the values first 
    lon_res = np.unique(np.diff(np.sort(lons)))
    if len(lon_res) != 1:
        # Find the average and standard deviation of the longitude resolution
        ## Make sure to sort the values first 
        lon_res = np.diff(np.sort(lons))
        lon_res_mean = np.mean(lon_res)
        lon_res_std = np.std(lon_res)
        lon_res = f"{lon_res_mean} ± {lon_res_std}"
    else:
        lon_res = str(lon_res[0])
    # Return the resolution in latitude and longitude
    return lat_res, lon_res

def print_latlon_info(
    xr_dataset=None,
    lats=None,
    lons=None,
    shift_lons=False,
    ):
    """Print information about the latitude and longitude values.

    Prints the extent and resolution of the latitude and longitude
    values in the given dataset or arrays.

    Parameters
    ----------
    xr_dataset : str or xarray.Dataset or xarray.DataArray, optional
        The filepath to, or the xarray data for which to print the 
        latitude and longitude information.
    lats : numpy.ndarray, optional
        The latitude values to use instead of those in the dataset.
    lons : numpy.ndarray, optional
        The longitude values to use instead of those in the dataset.
    shift_lons : bool, optional
        If True, shift the longitude values from the range [0, 360] to [-180, 180].
    """
    # Initialize a variable to hold the name of the output
    output_name = 'provided lat/lon arrays'
    # If a filepath is provided, verify the path and load the dataset
    if isinstance(xr_dataset, str):
        output_name = str(xr_dataset)
        xr_dataset = unox.verify_path(xr_dataset)
        # If it is a csv, use custom function to load
        if xr_dataset.endswith('.csv'):
            xr_dataset = csv_to_xr(xr_dataset)
        else:
            xr_dataset = xr.open_dataset(xr_dataset)
    if not isinstance(xr_dataset, type(None)):
        # Verify the xarray dataset
        xr_dataset = verify_dataset(xr_dataset, shift_lons=shift_lons)
        # Change output name to the dataset name
        if output_name == 'provided lat/lon arrays':
            output_name = 'provided xarray dataset'
    # Print the extent and the resolution of the latitude and longitude values
    extent = get_extent(xr_dataset=xr_dataset, lats=lats, lons=lons, shift_lons=shift_lons)
    lat_res, lon_res = get_latlon_resolution(xr_dataset=xr_dataset, lats=lats, lons=lons, shift_lons=shift_lons)
    print(f"For {output_name}: ")
    print(f"\tLatitude extent: {extent[0]} to {extent[1]}")
    print(f"\tLongitude extent: {extent[2]} to {extent[3]}")
    print(f"\tLatitude resolution: {lat_res}")
    print(f"\tLongitude resolution: {lon_res}")

def verify_dataset(
    xr_dataset,
    check_time=True,
    shift_lons=False,
    ):
    """Verify that the given xarray dataset is valid.

    Checks to make sure the given dataset is of the expected type
    and contains the expected coordinates.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data to verify.
    check_time : bool, optional
        If True, verify that the dataset has a 'time' coordinate.
    shift_lons : bool or string, optional
        If True, shift the longitude values from the range [0, 360] to [-180, 180].
        If 'ID_centered', shift from [-180, 180] to [0, 360].
    """
    # Verify that xr_dataset is an xarray Dataset or DataArray
    if not isinstance(xr_dataset, xr.Dataset) and not isinstance(xr_dataset, xr.DataArray):
        raise TypeError("xr_dataset must be an xarray Dataset or DataArray.")
    # Standardize the coordinate names
    xr_coords = list(xr_dataset.coords)
    for coord in xr_coords:
        std_coord = fuzzy_coord_match(coord)
        if std_coord == 'lat':
            xr_dataset = xr_dataset.rename({coord: 'lat'})
        elif std_coord == 'lon':
            xr_dataset = xr_dataset.rename({coord: 'lon'})
        elif std_coord == 'time':
            xr_dataset = xr_dataset.rename({coord: 'time'})
    coordinate_list = list(xr_dataset.coords)
    # Verify that the dataset has lat and lon coordinates
    if 'lat' not in coordinate_list:# and 'latitude' not in coordinate_list and 'Latitude' not in coordinate_list:
        raise ValueError(f"xr_dataset must have 'lat' or 'latitude' as a coordinate. Available coordinates are: {coordinate_list}")
    if 'lon' not in coordinate_list:# and 'longitude' not in coordinate_list and 'Longitude' not in coordinate_list:
        raise ValueError(f"xr_dataset must have 'lon' or 'longitude' as a coordinate.. Available coordinates are: {coordinate_list}")
    # Verify that the dataset has the time coordinate
    if check_time:
        if 'time' not in coordinate_list:# and 'Date' not in coordinate_list:
            raise ValueError("xr_dataset must have 'time' coordinate.")
    # Shift longitude values if specified
    if shift_lons == 'ID_centered':
        xr_dataset['lon'] = shift_lon_arr(xr_dataset['lon'], PM_centered=False)
    elif shift_lons:
        xr_dataset['lon'] = shift_lon_arr(xr_dataset['lon'], PM_centered=True)
    return xr_dataset

def verify_number(
    value,
    ):
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

def clean_num_list(
    val_list,
    ):
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

def verify_lat(
    lat_val,
    ):
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

def verify_lon(
    lon_val,
    PM_centered=None,
    ):
    """Verify that the given longitude value is valid.

    If the given longitude value is within the range [-180, 180],
    return that value. Otherwise, raise a ValueError.

    Parameters
    ----------
    lon_val : float
        The longitude value to verify.
    PM_centered : bool, optional
        If None, verify that the longitude value is in the range [-180, 360].
        If True, verify that the longitude value is in the range [-180, 180].
        If False, verify that the longitude value is in the range [0, 360].

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
    if isinstance(PM_centered, type(None)):
        if lon_val < -180 or lon_val > 360:
            raise ValueError(f"Longitude value must be in the range [-180, 360], lon_val = {lon_val}.")
    elif PM_centered:
        if lon_val < -180 or lon_val > 180:
            raise ValueError(f"Longitude value must be in the range [-180, 180], lon_val = {lon_val}.")
    else:
        if lon_val < 0 or lon_val > 360:
            raise ValueError(f"Longitude value must be in the range [0, 360], lon_val = {lon_val}.")
    return lon_val

def shift_lon(
    lon_value,
    PM_centered=True,
    ):
    """Shift the given longitude value between ranges [0, 360] and [-180, 180].

    If the Prime Meridian is centered and the longitude value is in the range [0, 360],
    shift it to the range [-180, 180]. If the Prime Meridian is not centered (i.e. the
    International Date Line is centered) and the longitude value is in the range 
    [-180, 180], shift it to the range [0, 360]. Otherwise, return the same value.
    If the longitude value is not a number or is NaN, or is outside the relevant range
    for the specified PM_centered, raise a ValueError.

    Parameters
    ----------
    lon_value : float
        The longitude value to shift.
    PM_centered : bool, optional
        If True, shift the longitude value from the range [0, 360] to [-180, 180].
        If False, shift from [-180, 180] to [0, 360]. Defaults to True.

    Returns
    -------
    lon_value : float
        The shifted longitude value.

    Examples
    --------
    >>> lon_value = shift_lon(45.0, PM_centered=True)
    45.0
    >>> lon_value = shift_lon(270.0, PM_centered=True)
    -90.0
    >>> lon_value = shift_lon(-70.0, PM_centered=False)
    290.0
    >>> lon_value = shift_lon(200.0, PM_centered=False)
    200.0
    """
    if not verify_number(lon_value):
        raise ValueError("Longitude value must be a number.")
    if np.isnan(lon_value):
        raise ValueError("Longitude value must not be NaN.")
    # Check overall range
    if lon_value < -180 or lon_value > 360:
        raise ValueError(f"Longitude value must be in the range [-180, 360], lon_value = {lon_value}.")
    # If using PM-centered convention
    if PM_centered==True:
        # Check if the value is in the range [180, 360]
        if lon_value > 180 and lon_value <= 360:
            # Shift to [-180, 180]
            return (lon_value + 180) % 360 - 180
    # If using IDL-centered convention
    elif PM_centered==False:
        # Check if the value is in the range [-180, 0]
        if lon_value >= -180 and lon_value <= 0:
            # Shift to [0, 360]
            return (lon_value + 360) % 360
    else:
        raise ValueError(f"PM_centered must be True or False. Got {PM_centered}.")
    return lon_value

def shift_lon_arr(
    lon_array,
    PM_centered=True,
    ):
    """
    Shift the given array of longitude values between ranges [0, 360] and [-180, 180].

    Map the `shift_lon` function to shift each value in the array.

    Parameters
    ----------
    lon_array : numpy.ndarray or xarray.DataArray
        The array of longitude values to shift.
    PM_centered : bool, optional
        If True, shift the longitude value from the range [0, 360] to [-180, 180].
        If False, shift from [-180, 180] to [0, 360]. Defaults to True.

    Returns
    -------
    numpy.ndarray or xarray.DataArray
        The shifted longitude values in the range [-180, 180].

    Examples
    --------
    >>> lon_array = np.array([0, 90, 180, 270, 360])
    >>> shifted_lon = shift_lon_arr(lon_array)
    array([0, 90, 180, -90, 0])
    """
    # Ensure the input is a numpy array or xarray DataArray
    if not isinstance(lon_array, (np.ndarray, xr.DataArray)):
        raise TypeError("Input must be a numpy.ndarray or xarray.DataArray.")
    
    # Map the shift_lon function to each element in the array
    shifted_lon = np.vectorize(shift_lon, excluded={1})(lon_array, PM_centered)
    
    return shifted_lon

def get_vminmax(
    arrays,
    ):
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

def get_max_abs_val(
    val_list,
    ):
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

def restrict_domain(
    arrs_to_restrict, 
    lats, 
    lons, 
    restricting_data,
    ):
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

def verify_npy(
    array,
    ):
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

def get_num_from_string(
    str,
    ):
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

def get_DOY(
    date,
    ):
    """Get the day of the year from a date.

    Extracts the day of the year from a given date
    and returns it as an integer.

    Parameters
    ----------
    date : np.datetime64 or str
        The date to extract the day of the year from.

    Returns
    -------
    doy : int
        The day of the year of the date.

    Examples
    --------
    >>> get_DOY('2019-12-20')
    354
    >>> get_DOY(np.datetime64('2020-01-01'))
    1
    """
    # If date is a string, try to parse it as a date using a couple different formats
    if isinstance(date, str):
        try:
            doy = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').timetuple().tm_yday
        except:
            try:
                doy = datetime.strptime(date, '%Y-%m-%d').timetuple().tm_yday
            except:
                raise ValueError(f"Invalid date format: {date}. Expected 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS'.")
    # If date is a numpy datetime64, convert it to a date and get the day of the year
    elif isinstance(date, np.datetime64):
        doy = date.astype('datetime64[D]').astype(object).timetuple().tm_yday
    else:
        raise TypeError("date must be a np.datetime64 or str.")
    return int(doy)

def increment_month(
    month, 
    increment,
    ):
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
    increment_year : bool
        Whether the increment caused a year change.
        True if the month is December and increment > 0.

    Examples
    --------
    >>> increment_month(1, 2)
    3, False
    >>> increment_month(11, 3)
    2, True
    >>> increment_month('5', '7')
    '12', False
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
    # Determine if the increment caused a year change
    if month + increment > 12:
        increment_year = True
    else:
        increment_year = False
    
    # Return the new month in the same type as the input
    if return_type == str:
        return str(new_month), increment_year
    else:
        return new_month, increment_year

def get_YMD_from_date(
    this_date,
    ):
    """Get the year, month, and day from a date.

    Extracts the year, month, and day from a given date
    and returns them as integers.

    Parameters
    ----------
    this_date : np.datetime64 or str
        The date to extract the year, month, and day from.

    Returns
    -------
    year : int
        The year of the date.
    month : int
        The month of the date.
    day : int
        The day of the date.

    Examples
    --------
    >>> get_YMD_from_date('2019-12-20')
    (2019, 12, 20)
    >>> get_YMD_from_date(np.datetime64('2020-01-01'))
    (2020, 1, 1)
    """
    # Ensure that the input is a valid date type
    if isinstance(this_date, str):
        try:
            this_date = np.datetime64(this_date)
        except ValueError:
            raise ValueError(f"Invalid date string: {this_date}. Must be in 'YYYY-MM-DD' format.")
    
    if not isinstance(this_date, np.datetime64):
        raise TypeError("this_date must be a np.datetime64 or str.")
    
    # Extract the year, month, and day from the date
    year = this_date.astype(object).year
    month = this_date.astype(object).month
    day = this_date.astype(object).day
    
    return year, month, day

def get_increment_info(
    increment,
    ):
    """Get the increment value and unit from a string.

    Parses a string that represents an increment in the format 'XD', 'XM', or 'XY',
    where X is an integer and D, M, or Y are the units for days, months, or years respectively.
    
    Parameters
    ----------
    increment : np.timedelta64 or str
        The amount of time to add to the date.
        If a string, it should be in the format 'XD', 'XM', or 'XY'
        where X is an integer and D, M, or Y are the units for days, 
        months, or years respectively.

    Returns
    -------
    value : int
        The numeric value of the increment.
    unit : str
        The unit of the increment ('D', 'M', or 'Y').

    Raises
    ------
    ValueError
        If the increment string is not in the expected format.
    TypeError
        If the increment is not a np.timedelta64 or str.
    
    Examples
    --------
    >>> value, unit = get_increment_info('20D')
    (20, 'D')
    >>> value, unit = get_increment_info(np.timedelta64(20, 'D'))
    (20, 'D')
    >>> value, unit = get_increment_info('3M')
    (3, 'M')
    >>> value, unit = get_increment_info(np.timedelta64(2, 'Y'))
    (2, 'Y')
    """
    # Check if the increment is a np.timedelta64
    if isinstance(increment, np.timedelta64):
        # Determine the unit and value based on the dtype
        if increment.dtype == 'timedelta64[D]':
            value = increment.astype('timedelta64[D]').astype(int)
            unit = 'D'
        elif increment.dtype == 'timedelta64[M]':
            value = increment.astype('timedelta64[M]').astype(int)
            unit = 'M'
        elif increment.dtype == 'timedelta64[Y]':
            value = increment.astype('timedelta64[Y]').astype(int)
            unit = 'Y'
        else:
            raise ValueError("Unsupported timedelta64 type. Use days, months, or years.")
    elif isinstance(increment, str):
        # Match the string format using regex
        match = re.match(r'(\d+)([DMY])', increment)
        if not match:
            raise ValueError(f"Invalid increment format: {increment}. Use 'XD', 'XM', or 'XY' where X is an integer and D, M, or Y are the units for days, months, or years respectively.")
        value, unit = match.groups()
        value = int(value)  # Convert to integer
    else:
        raise TypeError("increment must be a np.timedelta64 or str.")
    
    return value, unit

def add_amount_to_date(
    this_date,
    increment,
    keep_within_year=False,
    ):
    """Add an amount of time to a date.

    Adds the given amount of time to the given date and 
    returns the new date.

    Parameters
    ----------
    this_date : np.datetime64 or str
        The date to add the time to.
    increment : np.timedelta64 or str
        The amount of time to add to the date.
        If a string, it should be in the format 'XD', 'XM', or 'XY'
        where X is an integer and D, M, or Y are the units for days, 
        months, or years respectively.
    keep_within_year : bool, optional
        If True, the new date will be kept within the same year as `this_date`.

    Returns
    -------
    new_date : np.datetime64 or str
        The new date after adding the time.
    
    Examples
    --------
    >>> add_time_to_date('2019-12-20', '20D')
    '2020-01-09'
    >>> add_time_to_date(np.datetime64('2019-12-25'), np.timedelta64(20, 'D'))
    np.datetime64('2020-01-14')
    """
    # Make sure the inputs are of the correct type
    if not isinstance(this_date, (np.datetime64, str)):
        raise TypeError("this_date must be a np.datetime64 or str.")
    if not isinstance(increment, (np.timedelta64, str)):
        raise TypeError("increment must be a np.timedelta64 or str.")
    # If the date is a string, convert it to a np.datetime64
    if isinstance(this_date, str):
        this_date = np.datetime64(this_date)
        return_type = str
    else:
        return_type = np.datetime64
    # Determine whether to add days, months, or years
    if isinstance(increment, np.timedelta64):
        # Find whether to add days, or months / years
        if increment.dtype == 'timedelta64[D]':
            add_days = True
        elif increment.dtype == 'timedelta64[M]':
            add_days = False
            value = increment.astype('timedelta64[M]').astype(int)
            unit = 'M'
        elif increment.dtype == 'timedelta64[Y]':
            add_days = False
            value = increment.astype('timedelta64[Y]').astype(int)
            unit = 'Y'
        else:
            raise ValueError("Unsupported timedelta64 type. Use days, months, or years.")
    elif isinstance(increment, str):
        # If the amount is a string, convert it to np.timedelta64
        match = re.match(r'(\d+)([DMY])', increment)
        if not match:
            raise ValueError(f"Invalid increment format: {increment}. Use 'XD', 'XM', or 'XY' where X is an integer and D, M, or Y are the units for days, months, or years respectively.")
        value, unit = match.groups()
        # Find whether to add days, or months / years
        if unit == 'D':
            add_days = True
        else:
            add_days = False
    else:
        raise TypeError("increment must be a np.timedelta64 or str.")
    # If adding days
    if add_days:
        if isinstance(increment, str):
            increment = np.timedelta64(int(value), unit)
        # Add the time to the date
        new_date = this_date + increment
    else:
        # Get the Y, M, D from the date
        this_year, this_month, this_day = get_YMD_from_date(this_date)
        if isinstance(increment, str):
            if unit == 'M':
                # If adding months, increment the month
                new_month, increment_year = increment_month(this_month, int(value))
                if increment_year:
                    # If the increment caused a year change, increment the year
                    this_year += 1
                # Create the new date with the incremented month and year
                new_date = np.datetime64(f"{this_year}-{new_month:02d}-{this_day:02d}")
            elif unit == 'Y':
                # If adding years, increment the year
                this_year += int(value)
                # Create the new date with the incremented year
                new_date = np.datetime64(f"{this_year}-{this_month:02d}-{this_day:02d}")
        else:
            if unit == 'M':
                # If adding months, increment the month
                new_month, increment_year = increment_month(this_month, int(value))
                if increment_year:
                    # If the increment caused a year change, increment the year
                    this_year += 1
                # Create the new date with the incremented month and year
                new_date = np.datetime64(f"{this_year}-{new_month:02d}-{this_day:02d}")
            elif unit == 'Y':
                # If adding years, increment the year
                this_year += value
                # Create the new date with the incremented year
                new_date = np.datetime64(f"{this_year}-{this_month:02d}-{this_day:02d}")
    # If keep_within_year is True, ensure the new date is within the same year
    if keep_within_year:
        # Get the year from the original date
        original_year = this_date.astype(object).year
        # Set the new date to the last day of the same year if it exceeds it
        if new_date.astype(object).year > original_year:
            new_date = np.datetime64(f"{original_year}-12-31")
        # Or, to the first day of the same year if it is before it
        elif new_date.astype(object).year < original_year:
            new_date = np.datetime64(f"{original_year}-01-01")

    # If the return type is a string, convert the date back to a string
    if return_type == str:
        new_date = str(new_date)
    # Return the new date
    return new_date

def fuzzy_coord_match(
    coord
    ):
    """Returns standard coordinate name for given fuzzy match.

    Takes in a coordinate name which may be a variation of standard
    coordinate names (e.g., 'lat', 'latitude', 'Latitude') and returns the
    standard coordinate name ('lat', 'lon', 'time') for latitude, longitude,
    and time. Also returns the dummy 'number' coordinate from ERA5 data.

    Parameters
    ----------
    coord : str
        The coordinate name to match.

    Returns
    -------
    matched_coord : str
        The standard coordinate name that matches the input coordinate.

    Examples
    --------
    >>> fuzzy_coord_match('lat')
    'lat' 
    >>> fuzzy_coord_match('latitude')
    'lat'
    >>> fuzzy_coord_match('Latitude')
    'lat'
    """
    # Convert the coordinate to lowercase for matching
    coord = coord.lower()
    # Define a mapping of fuzzy matches to standard coordinates
    coord_mapping = {
        'lat': 'lat',
        'latitude': 'lat',
        'lon': 'lon',
        'longitude': 'lon',
        'time': 'time',
        'valid_time': 'time',
        'datetime': 'time',
        'date': 'time',
        'number': 'number',  # Dummy coordinate for ERA5 data
    }
    # Check if the coordinate is in the mapping
    if coord in coord_mapping:
        return coord_mapping[coord]
    else:
        # If not found, raise an error
        raise ValueError(f"Coordinate '{coord}' does not match any standard coordinate names. Expected 'lat', 'lon', or 'time'.")

def csv_to_pd(
    csv_filepath,
    is_US_EPA=True,
    ):
    """Load a CSV file into a pandas DataFrame.

    Loads a CSV file into a pandas DataFrame, ensuring that the
    required columns are present if the file is from the US EPA.

    Parameters
    ----------
    csv_filepath : str
        The path to the CSV file to load.
    is_US_EPA : bool, optional
        If True, verify that the CSV file has the required columns
        for US EPA data. Defaults to True.

    Returns
    -------
    df : pandas.DataFrame
        The loaded DataFrame.

    Examples
    --------
    >>> df = csv_to_pd('datafiles/US_EPA/daily_42602_2019.csv')
    >>> df.head()   
                Latitude	Longitude	Arithmetic Mean
    Date			
    2019-01-01	33.553056	-86.815	    4.314286
    2019-01-08	33.553056	-86.815	    6.263636
    2019-01-09	33.553056	-86.815	    4.957143
    2019-01-10	33.553056	-86.815	    5.891667
    2019-01-11	33.553056	-86.815	    14.500000
    """
    # Verify the filepath
    csv_filepath = unox.verify_path(csv_filepath)
    # Verify the file is a CSV
    if not csv_filepath.lower().endswith('.csv'):
        raise ValueError("File must be a CSV.")
    # If it is from the US EPA
    if is_US_EPA:
        try:
            df = pd.read_csv(csv_filepath, parse_dates={'Date':['Date Local']}, index_col=['Date'], usecols=['Date Local', 'Latitude', 'Longitude', 'Arithmetic Mean'])
            # Rename 'Arithmetic Mean' to match the US EPA species ID name
            ## Get the ID from the file path
            species_id = os.path.basename(csv_filepath).split('_')[1]
            ## Get the species name
            species_name = get_US_EPA_species_name(species_id)
            ## Rename the 'Arithmetic Mean' column
            df.rename(columns={'Arithmetic Mean': species_name}, inplace=True)
        except Exception as e:
            raise ValueError(f"Error loading US EPA CSV file: {e}. Ensure the file has the required columns: 'Date Local', 'Latitude', 'Longitude', 'Arithmetic Mean'.")
    else:
        try:
            df = pd.read_csv(csv_filepath)
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {e}.")
    return df

def csv_to_xr(
    csv_filepath,
    is_US_EPA=True,
    ):
    """Load a CSV file into an xarray Dataset.

    Loads a CSV file into an xarray Dataset, ensuring that the
    required columns are present if the file is from the US EPA.

    Parameters
    ----------
    csv_filepath : str
        The path to the CSV file to load.
    is_US_EPA : bool, optional
        If True, verify that the CSV file has the required columns
        for US EPA data. Defaults to True.

    Returns
    -------
    xr_dataset : xarray.Dataset
        The loaded Dataset.

    Examples
    --------
    >>> xr_dataset = csv_to_xr('datafiles/US_EPA/daily_42602_2019.csv')
    >>> xr_dataset
    """
    # Load the CSV into a pandas DataFrame
    df = csv_to_pd(csv_filepath, is_US_EPA)
    # Convert the DataFrame to an xarray Dataset
    xr_dataset = df.to_xarray()
    # If it is from the US EPA, set the coordinates
    if is_US_EPA:
        xr_dataset = xr_dataset.set_coords(['Latitude', 'Longitude'])
        xr_dataset = verify_dataset(xr_dataset, shift_lons=False)
    return xr_dataset

def get_US_EPA_species_name(
    ID
    ):
    """Get the US EPA species name from the ID.

    Maps the US EPA species ID to the corresponding species name.

    Parameters
    ----------
    ID : str
        The US EPA species ID to map.

    Returns
    -------
    species_name : str
        The corresponding US EPA species name.

    Examples
    --------
    >>> species_name = get_US_EPA_species_name('42602')
    'no2'
    >>> species_name = get_US_EPA_species_name('42101')
    'co'
    """
    # Define a mapping of US EPA species IDs to species names
    species_mapping = {
        # Criteria gases
        '44201': 'o3',
        '42401': 'so2',
        '42101': 'co',
        '42602': 'no2',
        # Particulate matter
        '88101': 'pm25',
        '88502': 'pm25n',
        '81102': 'pm10',
        '86101': 'pmc',
        'SPEC': 'pm25spec',
        'PM10SPEC': 'pm10spec',
        # Meteorological
        'WIND': 'wind',
        'TEMP': 'temp',
        'PRESS': 'press',
        'RH_DP': 'rh_and_dp',
        # Toxics, Precursors, and Lead
        'HAPS': 'haps',
        'VOCS': 'vocs',
        'NONOxNOy': 'nonoxnoy',
        'LEAD': 'lead',
    }
    # Check if the ID is in the mapping
    if ID in species_mapping:
        return species_mapping[ID]
    else:
        raise ValueError(f"Invalid US EPA species ID: {ID}.")
