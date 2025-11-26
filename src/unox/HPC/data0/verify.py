import xarray as xr

# Necessary to use relative imports (starting with a dot) to avoid
# errors when running on HPC as the `unox` package is not available
from .latlon import shift_lon_arr

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