import numpy as np
import xarray as xr

def get_extent(xr_dataset):
    """Get the latitude and longitude extent of the given xarray dataset.

    Finds the maximum and minimum latitude and longitude values in the given dataset.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data of which to find the extent.
    
    Returns
    -------
    extent : tuple
        A tuple of np.float64 in the form (lat_min, lat_max, lon_min, lon_max).
    
    Examples
    --------
    >>> extent = get_extent(nox)
    (24.112, 58.878, -126.0, -59.625)
    """
    # Verify that xr_dataset is an xarray Dataset or DataArray
    if not isinstance(xr_dataset, xr.Dataset) and not isinstance(xr_dataset, xr.DataArray):
        raise TypeError("xr_dataset must be an xarray Dataset.")
    # Verify that the dataset has lat and lon coordinates
    if 'lat' not in xr_dataset.coords or 'lon' not in xr_dataset.coords:
        raise ValueError("xr_dataset must have 'lat' and 'lon' coordinates.")
    # Find the min and max lat and lon values
    # Use np.unique to ensure that the values are unique and take only the first value
    lat_min = np.unique(xr_dataset.lat.min().values)[0]
    lat_max = np.unique(xr_dataset.lat.max().values)[0]
    lon_min = np.unique(xr_dataset.lon.min().values)[0]
    lon_max = np.unique(xr_dataset.lon.max().values)[0]
    # Verify that the min and max values are not NaN
    if np.isnan(lat_min):
        raise ValueError("lat_min is NaN.")
    if np.isnan(lat_max):
        raise ValueError("lat_max is NaN.")
    if np.isnan(lon_min):
        raise ValueError("lon_min is NaN.")
    if np.isnan(lon_max):
        raise ValueError("lon_max is NaN.")
    # Verify that latitude values are in the range [-90, 90]
    if lat_min < -90 or lat_min > 90:
        raise ValueError("Latitude values must be in the range [-90, 90], lat_min = {lat_min}.")
    if lat_max < -90 or lat_max > 90:
        raise ValueError("Latitude values must be in the range [-90, 90], lat_max = {lat_max}.")
    # Verify that longitude values are in the range [-180, 180]
    if lon_min < -180 or lon_min > 180:
        raise ValueError("Longitude values must be in the range [-180, 180], lon_min = {lon_min}.")
    if lon_max < -180 or lon_max > 180:
        raise ValueError("Longitude values must be in the range [-180, 180], lon_max = {lon_max}.")
    # Return the extent as a tuple
    return (lat_min, lat_max, lon_min, lon_max)
