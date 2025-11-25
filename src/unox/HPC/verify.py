import xarray as xr

def verify_dataset(
    xr_dataset,
    check_time=True,
    shift_lons=False,
    **kwargs,
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
    shift_lons : bool, optional
        If True, shift the longitude values based on the PM_centered kwarg.
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `shift_lon_arr()`.
    """
    # Verify argument types
    if not isinstance(xr_dataset, xr.Dataset) and not isinstance(xr_dataset, xr.DataArray):
        raise TypeError(f"(verify_dataset) `xr_dataset` must be an xarray Dataset or DataArray. Got type: {type(xr_dataset)}.")
    if not isinstance(check_time, bool):
        raise TypeError(f"(verify_dataset) `check_time` must be a bool. Got type: {type(check_time)}.")
    if not isinstance(shift_lons, bool):
        raise TypeError(f"(verify_dataset) `shift_lons` must be a bool. Got type: {type(shift_lons)}.")
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
    if shift_lons:
        xr_dataset['lon'] = shift_lon_arr(xr_dataset['lon'], **kwargs)
    return xr_dataset