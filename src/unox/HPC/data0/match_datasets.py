import xarray as xr
import numpy as np

from .verify_dataset import verify_dataset
from .verify_dtype import verify_number

def get_extent(
    xr_dataset=None,
    lats=None,
    lons=None,
    shift_lons=False,
    **kwargs,
):
    """ Get the latitude and longitude extent of the given xarray dataset.

        Find the maximum and minimum latitude and longitude values in the given dataset.

        Parameters
        ----------
        xr_dataset : `xarray.Dataset` or `xarray.DataArray`, optional
            The xarray data of which to find the extent.
        lats : `numpy.ndarray`, optional
            The latitude values to use instead of those in the dataset.
        lons : `numpy.ndarray`, optional
            The longitude values to use instead of those in the dataset.
        shift_lons : `bool`, optional
            If True, shift the longitude values based on the PM_centered kwarg.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `verify_dataset()` and `shift_lon_arr()`.

        Returns
        -------
        extent : `tuple`
            A tuple of np.float64 in the form (lat_min, lat_max, lon_min, lon_max).

        Examples
        --------
        >>> nox = xr.open_dataset('datafiles/nox_2019_t106_US.nc')
        >>> extent = get_extent(nox)
        (24.112, 58.878, -126.0, -59.625)

        >>> lats, lons = get_lats_lons(nox)
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
    """ Get the latitude and longitude values from the given dataset.

        Load the latitude and longitude values from the given dataset and return them as numpy arrays.

        Parameters
        ----------
        xr_dataset : `xarray.Dataset` or `xarray.DataArray`
            The xarray data to verify.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `verify_dataset()`.

        Returns
        -------
        lats : `numpy.ndarray`
            Array of latitude values.
        lons : `numpy.ndarray`
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


def match_domains(
    xr_a,
    xr_b,
    require_equal=True,
    require_len_gt_1=True,
):
    """ Restrict the domain of the given xarray Datasets to match each other.

        Find the maximum extent covered by both given datasets and restrict both to match.
        Requires that at least some of the actual latitude and longitude values are present in both datasets.

        Parameters
        ----------
        xr_a : `xarray.Dataset` or `xarray.DataArray`
            The first dataset.
        xr_b : `xarray.Dataset` or `xarray.DataArray`
            The second dataset.
        require_equal : `bool`, optional
            Whether to check that the latitude and longitude values in the two datasets are exactly the same after trimming.
            Default is `True`.
        require_len_gt_1 : `bool`, optional
            Whether to check to make sure that the trimmed datasets have more than 1 value in each of the lat and lon dimensions, to catch cases where the datasets only overlap at a single point, resulting in either the lat or lon dimension being dropped.
            Default is `True`.

        Returns
        -------
        xr_a : `xarray.Dataset` or `xarray.DataArray`
            The first dataset, with the latitude and longitude extents trimmed to match `xr_b`.
        xr_b : `xarray.Dataset` or `xarray.DataArray`
            The first dataset, with the latitude and longitude extents trimmed to match `xr_a`.
    """
    # Verify argument types
    xr_a = verify_dataset(xr_a, check_time=False)
    xr_b = verify_dataset(xr_b, check_time=False)

    # Get the extent of xr_a
    (a_lat_min, a_lat_max, a_lon_min, a_lon_max) = get_extent(xr_a, check_time=False)
    # Get the extent of xr_b
    (b_lat_min, b_lat_max, b_lon_min, b_lon_max) = get_extent(xr_b, check_time=False)
    
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
    # this_ds_chemra = this_ds_chemra.where(
        #     (this_ds_chemra.lat >= extent[0]) &
        #     (this_ds_chemra.lat <= extent[1]) &
        #     (this_ds_chemra.lon >= extent[2]) &
        #     (this_ds_chemra.lon <= extent[3]),
        #     drop=True,
        # )
    tr_xr_a = xr_a.where(
        (xr_a.lat >= lat_min) &
        (xr_a.lat <= lat_max) &
        (xr_a.lon >= lon_min) &
        (xr_a.lon <= lon_max),
        drop=True,
    )
    tr_xr_b = xr_b.where(
        (xr_b.lat >= lat_min) &
        (xr_b.lat <= lat_max) &
        (xr_b.lon >= lon_min) &
        (xr_b.lon <= lon_max),
        drop=True,
    )
    # tr_xr_a = xr_a.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    # tr_xr_b = xr_b.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

    # Verify these two datasets have the same latitude and longitude values
    if require_equal == True:
        lats_a, lons_a = get_lats_lons(tr_xr_a, check_time=False)
        lats_b, lons_b = get_lats_lons(tr_xr_b, check_time=False)
        if not np.array_equal(lats_a, lats_b):
            raise ValueError(f"(match domains) Latitude values do not match between the two datasets.")
        if not np.array_equal(lons_a, lons_b):
            raise ValueError(f"(match domains) Longitude values do not match between the two datasets.")
    # Verify that the xarray datasets have more than 1 value in each of the lat and lon dimensions
    if require_len_gt_1 == True:
        if len(tr_xr_a.lat) <= 1:
            raise ValueError(f"(match_domains) `xr_a` has 1 or fewer values in the lat dimension after trimming.")
        if len(tr_xr_a.lon) <= 1:
            raise ValueError(f"(match_domains) `xr_a` has 1 or fewer values in the lon dimension after trimming.")
        if len(tr_xr_b.lat) <= 1:
            raise ValueError(f"(match_domains) `xr_b` has 1 or fewer values in the lon dimension after trimming.")
        if len(tr_xr_b.lon) <= 1:
            raise ValueError(f"(match_domains) `xr_b` has 1 or fewer values in the lon dimension after trimming.")
    return tr_xr_a, tr_xr_b


def verify_lat(
    lat_val,
):
    """ Verify that the given latitude value is valid.

        If the given latitude value is within the range [-90, 90], return that value.
        Otherwise, raise a ValueError.

        Parameters
        ----------
        lat_val : `float`
            The latitude value to verify.

        Returns
        -------
        lat_val : `float`
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
    """ Verify that the given longitude value is valid.

        If the given longitude value is within the range [-180, 180], return that value.
        Otherwise, raise a ValueError.

        Parameters
        ----------
        lon_val : `float`
            The longitude value to verify.
        PM_centered : `bool`, optional
            If None, verify that the longitude value is in the range [-180, 360].
            If True, verify that the longitude value is in the range [-180, 180].
            If False, verify that the longitude value is in the range [0, 360].

        Returns
        -------
        lon_val : `float`
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
