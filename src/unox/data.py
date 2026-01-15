import numpy as np
import xarray as xr
import pandas as pd
import warnings
import os
import re
from datetime import datetime

from unox.HPC.data0.paths import verify_path
from unox.HPC.data0.latlon import shift_lon_arr
from unox.HPC.data0.verify_dtype import verify_number
from unox.HPC.data0.verify_dataset import verify_dataset
from unox.HPC.data0.dataset import csv_to_xr

# Define the default latitude and longitude extents for this project
DEFAULT_LAT_MIN = 11
DEFAULT_LAT_MAX = 75
DEFAULT_LON_MIN = -175
DEFAULT_LON_MAX = -39
# Needs to be [north, west, south, east] for the cdsapi call in download_era5.py
DEFAULT_EXTENT = [DEFAULT_LAT_MAX, DEFAULT_LON_MIN, DEFAULT_LAT_MIN, DEFAULT_LON_MAX]

def generate_lats_lons(
    dataset='datafiles/sample_data/2019u10.nc',
    output_dir='datafiles/',
    ):
    """Generate latitude and longitude arrays from the given dataset.

    Creates the `lats.npy` and `lons.npy` files from the latitude and 
    longitude values in the given dataset. They were originally generated 
    from the ERA5 concatenated data files created by the `download_era5`
    and `concatenate` scripts in the `datafiles` directory.

    Parameters
    ----------
    dataset : str or xarray.Dataset, optional
        The filepath to the dataset or an xarray Dataset object from which to extract latitude and longitude values.

    Returns
    -------
    lats : numpy.ndarray
        The latitude values extracted from the dataset.
    lons : numpy.ndarray
        The longitude values extracted from the dataset.
    """
    # Load or verify the dataset
    if isinstance(dataset, str):
        xr_dataset = load_dataset(dataset)
    else:
        xr_dataset = verify_dataset(dataset)
    # Get the latitude and longitude values
    lats, lons = get_lats_lons(xr_dataset)
    # Save the latitude and longitude values as numpy arrays
    np.save(output_dir+'lats.npy', lats)
    np.save(output_dir+'lons.npy', lons)
    return lats, lons

def get_extent(
    xr_dataset=None,
    lats=None,
    lons=None,
    shift_lons=False,
    **kwargs,
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
    shift_lons : bool, optional
        If True, shift the longitude values based on the PM_centered kwarg.
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `verify_dataset()` and `shift_lon_arr()`.
    
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
            raise ValueError(f"(get_extent) Either `xr_dataset` or both `lats` and `lons` must be provided.")
        # Find the min and max lat and lon values
        lat_min = np.unique(np.min(lats))[0]
        lat_max = np.unique(np.max(lats))[0]
        # Shift the longitude values if specified
        if shift_lons:
            lons = shift_lon_arr(lons, **kwargs)
        lon_min = np.unique(np.min(lons))[0]
        lon_max = np.unique(np.max(lons))[0]
    else:
        # Verify the xr_dataset
        xr_dataset = verify_dataset(xr_dataset, **kwargs)
        # Find the min and max lat and lon values
        # Use np.unique to ensure that the values are unique and take only the first value
        lat_min = np.unique(xr_dataset.lat.min().values)[0]
        lat_max = np.unique(xr_dataset.lat.max().values)[0]
        # Shift the longitude values if specified
        if shift_lons:
            lons = shift_lon_arr(xr_dataset.lon.values, **kwargs)
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
    **kwargs,
    ):
    """Get the latitude and longitude values from the given dataset.

    Loads the latitude and longitude values from the given dataset
    and returns them as numpy arrays.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data to verify.
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `verify_dataset()`.

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
    xr_dataset = verify_dataset(xr_dataset, **kwargs)
    # Get the latitude and longitude values
    lats = xr_dataset.lat.values
    lons = xr_dataset.lon.values
    # Verify the latitude and longitude values
    map(verify_lat, lats)
    map(verify_lon, lons)
    return lats, lons

def get_latlon_resolution(
    xr_dataset=None,
    lats=None,
    lons=None,
    **kwargs,
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
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `verify_dataset()` and `get_lats_lons()`.
    
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
        xr_dataset = verify_dataset(xr_dataset, **kwargs)
        # Get the latitude and longitude values
        lats, lons = get_lats_lons(xr_dataset, **kwargs)
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
    **kwargs,
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
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `verify_dataset()`, 
        `get_extent()` and `get_latlon_resolution()`.
    """
    # Initialize a variable to hold the name of the output
    output_name = 'provided lat/lon arrays'
    # If a filepath is provided, verify the path and load the dataset
    if isinstance(xr_dataset, str):
        output_name = str(xr_dataset)
        xr_dataset = vfy.verify_path(xr_dataset)
        # If it is a csv, use custom function to load
        if xr_dataset.endswith('.csv'):
            xr_dataset = csv_to_xr(xr_dataset)
        else:
            xr_dataset = xr.open_dataset(xr_dataset)
    if not isinstance(xr_dataset, type(None)):
        # Verify the xarray dataset
        xr_dataset = verify_dataset(xr_dataset, **kwargs)
        # Change output name to the dataset name
        if output_name == 'provided lat/lon arrays':
            output_name = 'provided xarray dataset'
    # Print the extent and the resolution of the latitude and longitude values
    extent = get_extent(xr_dataset=xr_dataset, lats=lats, lons=lons, **kwargs)
    lat_res, lon_res = get_latlon_resolution(xr_dataset=xr_dataset, lats=lats, lons=lons, **kwargs)
    print(f"For {output_name}: ")
    print(f"\tLatitude extent: {extent[0]} to {extent[1]}")
    print(f"\tLongitude extent: {extent[2]} to {extent[3]}")
    print(f"\tLatitude resolution: {lat_res}")
    print(f"\tLongitude resolution: {lon_res}")

def verify_var(
    xr_dataset,
    var,
):
    """Verifies that the given variable is in the given xarray dataset.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data to verify.
    var : str
        The variable name to verify.

    Returns
    -------
    bool
        True if the variable is in the dataset, otherwise raises a ValueError.
    """
    # Verify argument types
    if True:
        if not isinstance(xr_dataset, xr.Dataset) and not isinstance(xr_dataset, xr.DataArray):
            raise TypeError(f"(verify_var) `xr_dataset` must be an xarray Dataset or DataArray. Got type: {type(xr_dataset)}")
        if not isinstance(var, str):
            raise TypeError(f"(verify_var) `var` must be a string. Got type: {type(var)}")
    # Check if the variable is in the dataset
    if var not in xr_dataset.data_vars:
        raise ValueError(f"(verify_var) Variable '{var}' not found in the xarray dataset. Available variables are: {list(xr_dataset.data_vars)}")
    else:
        return True

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
        raise ValueError("(clean_num_list) No valid numbers in the input list.")
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
        raise ValueError(f"(verify_lat) `lat_val` must be a number. Got type: {type(lat_val)}")
    if np.isnan(lat_val):
        raise ValueError(f"(verify_lat) `lat_val` must not be NaN.")
    if lat_val < -90 or lat_val > 90:
        raise ValueError(f"(verify_lat) `lat_val` must be in the range [-90, 90]. Got: {lat_val}")
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
        raise ValueError(f"(verify_lon) `lon_val` must be a number. Got type: {type(lon_val)}")
    if np.isnan(lon_val):
        raise ValueError(f"(verify_lon) `lon_val` must not be NaN.")
    if isinstance(PM_centered, type(None)):
        if lon_val < -180 or lon_val > 360:
            raise ValueError(f"(verify_lon) `lon_val` must be in the range [-180, 360]. Got: {lon_val}")
    elif PM_centered:
        if lon_val < -180 or lon_val > 180:
            raise ValueError(f"(verify_lon) `lon_val` must be in the range [-180, 180]. Got: {lon_val}")
    else:
        if lon_val < 0 or lon_val > 360:
            raise ValueError(f"(verify_lon) `lon_val` must be in the range [0, 360]. Got: {lon_val}")
    return lon_val

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
            raise ValueError(f"(get_vminmax) {e}. Does input array contain any non-NaN values?")
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
    >>> stage1 = np.load(get_pred_data(stage=1, 'HPC_run'='no2_example_run', 'year'=2019))
    >>> lats, lons = load_lats_lons()
    >>> nox = xr.open_dataset('datafiles/nox_2019_t106_US.nc')
    >>> stage1_restricted = restrict_domain([nox], lats, lons, nox)
    """
    # Get the latitude and longitude values from the restricting data
    lat_r, lon_r = get_lats_lons(restricting_data)

    # I feel like this should work, but I can't figure it out right now
    this_extent = get_extent(restricting_data)

    # Find indices of lats and lons that are in the restricting data
    ## within 0.1 degrees of the 
    latmin = np.where(np.abs(lats-np.min(lat_r))<0.1)[0][0]
    latmax = np.where(np.abs(lats-np.max(lat_r))<0.1)[0][0] + 1
    lonmin = np.where(np.abs(lons-np.min(lon_r))<0.1)[0][0]
    lonmax = np.where(np.abs(lons-np.max(lon_r))<0.1)[0][0] + 1

    # Narrow the data to just this region
    arrs_to_return = []
    for arr in arrs_to_restrict:
        arrs_to_return.append(arr[:,latmin:latmax,lonmin:lonmax,:])
    return arrs_to_return, lat_r, lon_r

def match_domains(
    xr_a,
    xr_b,
    ):
    """Restrict the domain of the given xarray Datasets to match each other.

    Finds the maximum extent covered by both given datasets and restricts both
    to match. Requires that at least some of the actual latitude and longitude
    values are present in both datasets.

    Parameters
    ----------
    xr_a : xarray.Dataset or xarray.DataArray
        The first dataset.
    xr_b : xarray.Dataset or xarray.DataArray
        The second dataset.
    
    Returns
    -------
    xr_a : xarray.Dataset or xarray.DataArray
        The first dataset, with the latitude and longitude extents trimmed to match `xr_b`.
    xr_b : xarray.Dataset or xarray.DataArray
        The first dataset, with the latitude and longitude extents trimmed to match `xr_a`.
    """
    # Verify argument types
    xr_a = verify_dataset(xr_a)
    xr_b = verify_dataset(xr_b)

    # Get the extent of xr_a
    (a_lat_min, a_lat_max, a_lon_min, a_lon_max) = get_extent(xr_a)
    # Get the extent of xr_b
    (b_lat_min, b_lat_max, b_lon_min, b_lon_max) = get_extent(xr_b)
    
    # Find the maximum extent covered by both datasets
    lat_min = max(a_lat_min, b_lat_min)
    lat_max = min(a_lat_max, b_lat_max)
    lon_min = max(a_lon_min, b_lon_min)
    lon_max = min(a_lon_max, b_lon_max)
    # Verify these numbers make sense
    if lat_min > lat_max:
        raise ValueError(f"(match_domains) `lat_min` ({lat_min}) larger than `lat_max` ({lat_max}).")
    if lon_min > lon_max:
        raise ValueError(f"(match_domains) `lon_min` ({lon_min}) larger than `lon_max` ({lon_max}).")

    # Trim both datasets
    tr_xr_a = xr_a.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    tr_xr_b = xr_b.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

    # Verify these two datasets have the same latitude and longitude values
    lats_a, lons_a = get_lats_lons(tr_xr_a)
    lats_b, lons_b = get_lats_lons(tr_xr_b)
    if not np.array_equal(lats_a, lats_b):
        raise ValueError(f"(match domains) Latitude values do not match between the two datasets.")
    if not np.array_equal(lons_a, lons_b):
        raise ValueError(f"(match domains) Longitude values do not match between the two datasets.")
    return tr_xr_a, tr_xr_b

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
            raise FileNotFoundError(f"(verify_npy) Path {array} leads to a folder.")
        if not os.path.isfile(array):
            raise FileNotFoundError(f"(verify_npy) File {array} does not exist.")
        ext = os.path.splitext(array)[1].lower()
        try:
            if ext == ".npy":
                return np.load(array, allow_pickle=True)
            elif ext in [".txt", ".csv"]:
                try:
                    nparray =  np.loadtxt(array, delimiter=",")
                    if len(nparray) == 0:
                        raise ValueError(f"(verify_npy) File {array} does not contain a readable numpy array.")
                    return nparray
                except Exception:
                    try:
                        nparray = np.genfromtxt(array, delimiter=",", skip_header=1)
                        if len(nparray) == 0:
                            raise ValueError(f"(verify_npy) File {array} does not contain a readable numpy array.")
                        return nparray
                    except Exception as e:
                        raise ValueError(f"(verify_npy) File {array} does not contain a readable numpy array.")
            else:
                raise ValueError(f"(verify_npy) File {array} does not contain a readable numpy array.")
        except Exception:
            raise ValueError(f"(verify_npy) File {array} does not contain a readable numpy array.")
    elif isinstance(array, np.ndarray):
        return array
    else:
        raise TypeError(f"(verify_npy) `array` is not a numpy array. Got type: {type(array)}")

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
        raise TypeError(f"(get_num_from_string) `str` must be a string. Got type: {type(str)}")
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
                raise ValueError(f"(get_doy) Invalid date format: {date}. Expected 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS'.")
    # If date is a numpy datetime64, convert it to a date and get the day of the year
    elif isinstance(date, np.datetime64):
        doy = date.astype('datetime64[D]').astype(object).timetuple().tm_yday
    else:
        raise TypeError(f"(get_doy) `date` must be a np.datetime64 or str. Got type: {type(date)}")
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
            raise TypeError(f"(increment_month) `month` must be an integer. Got type: {type(month)}")
    if not isinstance(month, int) or month < 1 or month > 12:
        raise ValueError(f"(increment_month) `month` must be an integer between 1 and 12. Got: {month}")
    
    # Ensure increment is an integer
    if isinstance(increment, str):
        try:
            increment = int(increment)
        except:
            raise TypeError(f"(increment_month) `increment` must be an integer. Got type: {type(increment)}")
    if not isinstance(increment, int):
        raise TypeError(f"(increment_month) `increment` must be an integer. Got type: {type(increment)}")
    
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
            raise ValueError(f"(get_YMD_from_date) `this_date` is an invalid date string: {this_date}. Must be in 'YYYY-MM-DD' format.")
    
    if not isinstance(this_date, np.datetime64):
        raise TypeError(f"(get_YMD_from_date) `this_date` must be a np.datetime64 or str. Got type: {type(this_date)}")
    
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
            raise ValueError(f"(get_increment_info) Unsupported timedelta64 type for `increment.dtype`. Use days, months, or years. Got type: {increment.dtype}")
    elif isinstance(increment, str):
        # Match the string format using regex
        match = re.match(r'(\d+)([DMY])', increment)
        if not match:
            raise ValueError(f"(get_increment_info) Invalid `increment` format: {increment}. Use 'XD', 'XM', or 'XY' where X is an integer and D, M, or Y are the units for days, months, or years respectively.")
        value, unit = match.groups()
        value = int(value)  # Convert to integer
    else:
        raise TypeError(f"(get_increment_info) `increment` must be a np.timedelta64 or str. Got type: {type(increment)}")
    
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
        raise TypeError(f"(add_amount_to_date) `this_date` must be a np.datetime64 or str. Got type: {type(this_date)}")
    if not isinstance(increment, (np.timedelta64, str)):
        raise TypeError(f"(add_amount_to_date) `increment` must be a np.timedelta64 or str. Got type: {type(increment)}")
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
            raise ValueError(f"(add_amount_to_date) Unsupported timedelta64 type for `increment.dtype`. Use days, months, or years. Got type: {increment.dtype}")
    elif isinstance(increment, str):
        # Match the string format using regex
        match = re.match(r'(\d+)([DMY])', increment)
        if not match:
            raise ValueError(f"(add_amount_to_date) Invalid `increment` format: {increment}. Use 'XD', 'XM', or 'XY' where X is an integer and D, M, or Y are the units for days, months, or years respectively.")
        value, unit = match.groups()
        # Find whether to add days, or months / years
        if unit == 'D':
            add_days = True
        else:
            add_days = False
    else:
        raise TypeError(f"(add_amount_to_date) `increment` must be a np.timedelta64 or str. Got type: {type(increment)}")
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
