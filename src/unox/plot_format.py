from unox import data as udata

def pad_extent(
    extent, 
    padding=0.1,
    ):
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

def get_var_label_and_units(
    var,
    ):
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
        ## NOx
        # t106 variables
        'nox': (r'Surface NO$_x$ emissions', r'kg N m$^{-2}$ s$^{-1}$'),
        # TROPESS variables
        'no2': (r'NO$_2$', 'ppt'), 
        'no2_tm1': (r'NO$_2$ at $t-1$', 'ppt'),
        ## CO
        # HEMCO variables
        'EmisCO_Total': (r'CO emission flux (all sectors)', r'kg/m$^2$/s'),
        # GEOS-Chem variables
        'SpeciesConcVV_CO': (r'CO concentration', r'mol / mol dry'),
        ## Meteorology
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

def make_stage_comp_arrs(
    in_arrs,
    this_date,
    var,
    avg_over=None,
    ):
    """Create arrays for stage comparison plots.

    Creates a dictionary of arrays for stage comparison, where each key is a stage
    and the value is an array of the variable for that stage. For use with the 
    `unox.plotting.plot_stage_comp_maps()` function.

    Parameters
    ----------
    in_arrs : dict
        A dictionary of input arrays, where the keys are stage names and the values are arrays.
        Expects format like: {'truth': truth_arr, 'stage1': stage1_arr, 'stage2': stage2_arr}
    this_date : np.datetime64 or str
        Date and time to select from the data file.
        Expected format is 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DD'.
    var : str
        The variable which will be plotted.
    avg_over : str, numpy.timedelta64, or None
        If provided, averages the data over the specified time period.
        If None, takes just the time slice specified in `datetime`.

    Returns
    -------
    out_arrs : dict
        A dictionary of output arrays for each stage.
    overall_title : str
        A title for the overall plot, based on the variable and date(s).
    
    Examples
    --------
    >>> 
    """
    out_arrs = {}
    
    # Get the variable label and units
    var_label, var_units = get_var_label_and_units(var)

    # Get the day of year to plot
    DOY = udata.get_DOY(this_date)
    if isinstance(avg_over, type(None)):
        # Get just that day from the numpy arrays
        truth = in_arrs['truth'][DOY, :, :, :]
        stage1 = in_arrs['stage1'][DOY, :, :, :]
        stage2 = in_arrs['stage2'][DOY, :, :, :]
        # Get the differences
        t_m_st1 = truth - stage1
        t_m_st2 = truth - stage2
        st1_m_st2 = stage1 - stage2
        # Format a string for the title
        overall_title = var_label + ' on ' + this_date
    # If averaging over a time period, get the end date
    else:
        # Add the increment to the date
        end_date = udata.add_amount_to_date(this_date, avg_over, keep_within_year=True)
        # Get the day of year for the end date
        DOY_end = udata.get_DOY(end_date)
        # Account for the fact that they only have 364 days
        if DOY_end > 364:
            DOY_end = 364
        print('start DOY:', DOY, 'end DOY:', DOY_end)
        # Get just the data between those two days
        truth = in_arrs['truth'][DOY:DOY_end, :, :, :]
        stage1 = in_arrs['stage1'][DOY:DOY_end, :, :, :]
        stage2 = in_arrs['stage2'][DOY:DOY_end, :, :, :]
        # Get the differences
        t_m_st1 = truth - stage1
        t_m_st2 = truth - stage2
        st1_m_st2 = stage1 - stage2
        # Take the average over the time period for all
        truth = truth.mean(axis=0)
        stage1 = stage1.mean(axis=0)
        stage2 = stage2.mean(axis=0)
        t_m_st1 = t_m_st1.mean(axis=0)
        t_m_st2 = t_m_st2.mean(axis=0)
        st1_m_st2 = st1_m_st2.mean(axis=0)
        # Get the value and unit of the averaging
        avg_over_num, avg_over_unit = udata.get_increment_info(avg_over)
        # Format a string for the title
        overall_title = var_label + ' averaged over ' + str(avg_over_num) + ' ' + avg_over_unit + ' from ' + this_date
    # Set the arrays to plot
    ## They only have one channel, so just select index 0
    out_arrs['truth']  = truth[:,:,0]
    out_arrs['stage1'] = stage1[:,:,0]
    out_arrs['stage2'] = stage2[:,:,0]
    out_arrs['t_m_st1'] = t_m_st1[:,:,0]
    out_arrs['t_m_st2'] = t_m_st2[:,:,0]
    out_arrs['st1_m_st2'] = st1_m_st2[:,:,0]
    return out_arrs, overall_title
