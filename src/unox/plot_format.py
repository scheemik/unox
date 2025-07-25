from unox import data as udata

def pad_extent(extent, padding=0.1):
    """Pads the given extent.

    Pads the latitude and longitude extent of a dataset by enlarging
    the extent by the padding value.

    Parameters
    ----------
    extent : tuple
        A tuple of np.float64 in the form (lat_min, lat_max, lon_min, lon_max).
    padding : float
        The amount to pad the extent by in a fraction.

    Returns
    -------
    padded_extent : tuple
        A tuple of np.float64 in the form (p_lat_min, p_lat_max, p_lon_min, p_lon_max).

    Examples
    --------
    >>> nox = xr.open_dataset('datafiles/nox_2019_t106_US.nc')
    >>> extent = unox.data.get_extent(nox)
    >>> padded_extent = pad_extent(extent, padding=0.1)
    (20.635399999999997, 62.3546, -132.6375, -52.9875)
    """
    # Verify the tuple is the right shape
    if not isinstance(extent, tuple) or len(extent) != 4:
        raise ValueError("Extent must be a tuple of the form (lat_min, lat_max, lon_min, lon_max)")
    # Verify the padding is a number
    if not udata.verify_number(padding):
        raise TypeError("Padding must be a number, got: " + str(type(padding)) + ". Padding value: " + str(padding))
    # Unpack the extent tuple
    lat_min, lat_max, lon_min, lon_max = extent
    # Verify these values
    lat_min = udata.verify_lat(lat_min)
    lat_max = udata.verify_lat(lat_max)
    lon_min = udata.verify_lon(lon_min)
    lon_max = udata.verify_lon(lon_max)
    # Enlarge the extent of the map by the given padding value
    p_lat_min = lat_min - padding*abs(lat_max - lat_min)
    p_lat_max = lat_max + padding*abs(lat_max - lat_min)
    p_lon_min = lon_min - padding*abs(lon_max - lon_min)
    p_lon_max = lon_max + padding*abs(lon_max - lon_min)
    # Verify the latitude values are in the range [-90, 90]
    if p_lat_min < -90:
        p_lat_min = -90
    if p_lat_max > 90:
        p_lat_max = 90
    # Verify the longitude values are in the range [-180, 180]
    if p_lon_min < -180:
        p_lon_min = -180
    if p_lon_max > 180:
        p_lon_max = 180
    # Return the padded extent as a tuple
    return (p_lat_min, p_lat_max, p_lon_min, p_lon_max)

def get_var_label_and_units(var):
    """Get the label and units for a variable.

    Returns the label and units for a variable based on its name.

    Parameters
    ----------
    var : str
        The name of the variable.

    Returns
    -------
    label : str
        The label for the variable.
    units : str
        The units for the variable.

    Examples
    --------
    >>> label, units = get_var_label_and_units('temperature')
    ('Temperature', '°C')
    """
    var_labels_and_units = {
        'lat': ('Latitude', r'$^\circ$N'),
        'lon': ('Longitude', r'$^\circ$E'),
        # t106 variables
        'nox': (r'Surface NO$_x$ emissions', r'kg N m$^{-2}$ s$^{-1}$'),
        # TROPESS variables
        'no2': (r'NO$_2$', 'ppt'), 
        'no2_tm1': (r'NO$_2$ at $t-1$', 'ppt'),
        # ERA5 variables
        'u10': ('10 metre U wind component', r'm s$^{-1}$'),
        'v10': ('10 metre V wind component', r'm s$^{-1}$'),
        'blh': ('Boundary layer height', 'm'),
        'sp':  ('Surface pressure', 'Pa'),
        'skt': ('Skin temperature', 'K'),
        'ssrd': ('Surface short-wave (solar) radiation downwards', r'J m$^{-2}$'),
        't2m': ('2 metre temperature', 'K'),
    }

    if var not in var_labels_and_units.keys():
        raise ValueError(f"Variable '{var}' not recognized. Available variables: {list(var_labels_and_units.keys())}")
    else:
        label, units = var_labels_and_units[var]
    
    return label, units