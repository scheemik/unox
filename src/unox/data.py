import numpy as np
import xarray as xr

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

def get_lats_lons(dataset='../datafiles/TROPESS_reanalysis_mon_emi_nox_anth_2021.nc',
                  shift_lons=False):
    """Get the latitude and longitude values from the given dataset.

    Loads the latitude and longitude values from the given dataset
    and returns them as numpy arrays.

    Parameters
    ----------
    dataset : str
        The path to the dataset file.

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
    # Open the dataset using xarray
    xr_dataset = xr.open_dataset(dataset)
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