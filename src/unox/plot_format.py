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
    >>> extent = unox.data.get_extent(24.112, 58.878, -126.0, -59.625)
    >>> padded_extent = pad_extent(extent, padding=0.1)
    (20.635399999999997, 62.3546, -132.6375, -52.9875)
    """
    # Unpack the extent tuple
    lat_min, lat_max, lon_min, lon_max = extent
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
        p_lon_min += 360
    if p_lon_max > 180:
        p_lon_max -= 360
    # Return the padded extent as a tuple
    return (p_lat_min, p_lat_max, p_lon_min, p_lon_max)