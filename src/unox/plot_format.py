import numpy as np

from unox import data as udata
from unox.HPC.data0.verify_dtype import verify_number

def set_fig_row_col(
    n_subplots,
    n_rows=None,
    n_cols=None,
    **kwargs,
):
    """Determine the number of rows and columns in a figure based on the number of subplots.

        Parameters
        ----------
        n_subplots : int
            The total number of subplots in the figure.
        n_rows : in or None
            The number of rows to use in the figure. Default is `None`.
        n_cols : int or None
            The number of columns to use in the figure. Default is `None`.
        **kwargs : keyword arguments
            Additional keyword arguments accepted to facilitate wrapper functions.
        
        Returns
        -------
        n_rows : int
            The number of rows in the figure.
        n_cols : int
            The number of columns in the figure.
        
        Examples
        --------
        >>> n_rows, n_cols = set_fig_row_col(4)
        2, 2
        >>> n_rows, n_cols = set_fig_row_col(6)
        2, 3
        >>> n_rows, n_cols = set_fig_row_col(6, n_rows=3)
        3, 2
    """
    # Verify argument types
    if not isinstance(n_subplots, int):
        raise TypeError(f"(set_fig_row_col) `n_subplots` must be an integer. Got type: {type(n_subplots)}")
    if not isinstance(n_rows, type(None)) and not isinstance(n_rows, int):
        raise TypeError(f"(set_fig_row_col) `n_rows` must be an integer or `None`. Got type: {type(n_rows)}")
    if not isinstance(n_cols, type(None)) and not isinstance(n_cols, int):
        raise TypeError(f"(set_fig_row_col) `n_cols` must be an integer or `None`. Got type: {type(n_cols)}")
    # Make sure none of the inputs are equal to zero or negative
    if n_subplots <= 0:
        raise ValueError(f"(set_fig_row_col) `n_subplots` must be a positive integer. Got: {n_subplots}")
    if not isinstance(n_rows, type(None)) and n_rows <= 0:
        raise ValueError(f"(set_fig_row_col) `n_rows` must be a positive integer. Got: {n_rows}")
    if not isinstance(n_cols, type(None)) and n_cols <= 0:
        raise ValueError(f"(set_fig_row_col) `n_cols` must be a positive integer. Got: {n_cols}")
    # Determine the number of rows and columns
    if not isinstance(n_rows, type(None)) and not isinstance(n_cols, type(None)):
        # Both rows and columns are specified
        if n_rows * n_cols < n_subplots:
            raise ValueError(f"(set_fig_row_col) `n_rows` * `n_cols` must be greater than or equal to `n_subplots`. Got: {n_rows} * {n_cols} < {n_subplots}")
        return n_rows, n_cols
    elif not isinstance(n_rows, type(None)):
        # Only rows are specified
        n_cols = int(np.ceil(n_subplots / n_rows))
        return n_rows, n_cols
    elif not isinstance(n_cols, type(None)):
        # Only columns are specified
        n_rows = int(np.ceil(n_subplots / n_cols))
        return n_rows, n_cols
    else:
        # Neither rows nor columns are specified
        if n_subplots == 3:
            n_rows = 1
            n_cols = 3
        elif n_subplots == 7:
            n_rows = 2
            n_cols = 4
        elif n_subplots == 8:
            n_rows = 2
            n_cols = 4
        else: # Use as close to a square layout as possible
            n_cols = int(np.ceil(np.sqrt(n_subplots)))
            n_rows = int(np.ceil(n_subplots / n_cols))
        return n_rows, n_cols

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
        raise ValueError(f"(pad_extent) `extent` must be a tuple of the form (lat_min, lat_max, lon_min, lon_max). Got type: {type(extent)}")
    # Verify the padding is a number
    if not verify_number(padding):
        raise TypeError(f"(pad_extent) `padding` must be a number. Got type: {type(padding)}.")
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
        raise ValueError(f"(get_var_label_and_units) Variable '{var}' not recognized. Available variables: {list(var_labels_and_units.keys())}")
    else:
        label, units = var_labels_and_units[var]
    return label, units

def make_stage_comp_arrs(
    in_arrs,
    this_date,
    var,
    avg_over=None,
    stage1_only=False,
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
        stage1_only : bool
            If True, produce arrays just corresponding to stage 1. If False, produce arrays
            for stage 1 and stage 2. Default is False.

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
        # Get the differences
        t_m_st1 = truth - stage1
        # Format a string for the title
        overall_title = var_label + ' on ' + this_date
        # If including stage 2
        if not stage1_only:
            # Get just that day from the numpy arrays
            stage2 = in_arrs['stage2'][DOY, :, :, :]
            # Get the differences
            t_m_st2 = truth - stage2
            st1_m_st2 = stage1 - stage2
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
        # Get the differences
        t_m_st1 = truth - stage1
        # Take the average over the time period for all
        truth = truth.mean(axis=0)
        stage1 = stage1.mean(axis=0)
        t_m_st1 = t_m_st1.mean(axis=0)
        # If including stage 2
        if not stage1_only:
            # Get just the data between those two days
            stage2 = in_arrs['stage2'][DOY:DOY_end, :, :, :]
            # Get the differences
            t_m_st2 = truth - stage2
            st1_m_st2 = stage1 - stage2
            # Take the average over the time period for all
            stage2 = stage2.mean(axis=0)
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
    out_arrs['t_m_st1'] = t_m_st1[:,:,0]
    # If including stage 2
    if not stage1_only:
        out_arrs['stage2'] = stage2[:,:,0]
        out_arrs['t_m_st2'] = t_m_st2[:,:,0]
        out_arrs['st1_m_st2'] = st1_m_st2[:,:,0]
    return out_arrs, overall_title

def format_sci_notation(
    x, 
    ndp=2, 
    sci_lims_f=(-3, 3), 
    pm_val=None, 
    condense=False
):
    """ Formats a number into scientific notation.

        Returns a formatted string of a number in scientific notation if the exponent is outside the specified limits. Uses LaTeX formatting for the string to be used in plot labels.

        Parameters
        ----------
        x : `float`, `int`
            The number to format.
        ndp : `int`, optional
            The number of decimal places to include in the formatted string.
            Default is 2.
        sci_lims_f : `tuple` of `int`, optional
            The limits on the powers of 10 between which scientific notation will not be used.
            Default is (-3, 3).
        pm_val : `float`, `int`, `None`, optional
            The plus-minus uncertainty value to include in the formatted string after a `\pm` symbol.
            If `None`, no uncertainty will be included.
            Default is `None`. 
        condense : `bool`, optional
            Whether to remove spaces around `\pm` and `\times` operators in the formatted string.
            Default is `False`.
            
        Returns
        -------
        formatted_str : `str`
            The formatted string of the number in scientific notation if the exponent is outside the specified limits, or in normal decimal notation otherwise. If `pm_val` is provided, the uncertainty will be included in the formatted string.
        
        Examples
        --------
        >>> format_sci_notation(0.00012345)
        '1.23\\times10^{-4}'
        >>> format_sci_notation(12345, ndp=3)
        '1.234\\times10^{4}'
        >>> format_sci_notation(0.00012345, sci_lims_f=(-5, 5))
        '0.00'
        >>> format_sci_notation(12345, sci_lims_f=(-5, 5))
        '12345.00'
    """
    # Verify argument types
    if not verify_number(x):
        raise TypeError(f"(format_sci_notation) `x` must be a number. Got type: {type(x)}.")
    if not isinstance(ndp, int):
        raise TypeError(f"(format_sci_notation) `ndp` must be an integer. Got type: {type(ndp)}.")
    if not isinstance(sci_lims_f, tuple) or len(sci_lims_f) != 2 or not all(isinstance(i, int) for i in sci_lims_f):
        raise TypeError(f"(format_sci_notation) `sci_lims_f` must be a tuple of two integers. Got type: {type(sci_lims_f)} with values: {sci_lims_f}.")
    if not (isinstance(pm_val, type(None)) or verify_number(pm_val)):
        raise TypeError(f"(format_sci_notation) `pm_val` must be a number or `None`. Got type: {type(pm_val)}.")
    if not isinstance(condense, bool):
        raise TypeError(f"(format_sci_notation) `condense` must be a boolean. Got type: {type(condense)}.")

    if isinstance(pm_val, type(None)):
        try:
            s = '{x:0.{ndp:d}e}'.format(x=x, ndp=ndp)
            m, e = s.split('e')
        except:
            print('Warning: could not format',x,'with',ndp,'decimal places')
            return r'{x:0.{ndp:d}f}'.format(x=x, ndp=ndp)
        # Check to see whether it's outside the scientific notation exponent limits
        if int(e) < min(sci_lims_f) or int(e) > max(sci_lims_f):
            if condense:
                return r'{m:s}{{\times}}10^{{{e:d}}}'.format(m=m, e=int(e))
            else:
                return r'{m:s}\times10^{{{e:d}}}'.format(m=m, e=int(e))
        else:
            return r'{x:0.{ndp:d}f}'.format(x=x, ndp=ndp)
    else:
        try:
            # Find magnitude and base 10 exponent for x
            s = '{x:0.{ndp:d}e}'.format(x=x, ndp=ndp)
            m, e = s.split('e')
        except:
            print('Warning: could not format',x,'with',ndp,'decimal places and pm_val:',pm_val)
            if condense:
                return r'{x:0.{ndp:d}f}{{\pm}}{pm_val:0.{ndp:d}f}'.format(x=x, ndp=ndp, pm_val=pm_val)
            else:
                return r'{x:0.{ndp:d}f}{{\pm}}{pm_val:0.{ndp:d}f}'.format(x=x, ndp=ndp, pm_val=pm_val)
        # Find magnitude and base 10 exponent for pm_val
        pm_s = '{pm_val:0.{ndp:d}e}'.format(pm_val=pm_val, ndp=ndp)
        pm_m, pm_e = pm_s.split('e')
        # Find difference between exponents to use as new number of decimal places
        new_ndp = max(2, int(e)-int(pm_e))
        # Reformat x
        s = '{x:0.{ndp:d}e}'.format(x=x, ndp=new_ndp)
        m, e = s.split('e')
        # Shift value of pm_val to correct exponent
        pm_m = '{pm_val:0.{ndp:d}f}'.format(pm_val=pm_val/(10**int(e)), ndp=new_ndp)
        # Check to see whether it's outside the scientific notation exponent limits
        if int(e) < min(sci_lims_f) or int(e) > max(sci_lims_f):
            if condense:
                return r'({m:s}{{\pm}}{pm_m:s}){{\times}} 10^{{{e:d}}}'.format(m=m, pm_m=pm_m, e=int(e))
            else:
                return r'({m:s}\pm{pm_m:s})\times 10^{{{e:d}}}'.format(m=m, pm_m=pm_m, e=int(e))
        else:
            if condense:
                return r'{x:0.{ndp:d}f}{{\pm}}{pm_val:0.{ndp:d}f}'.format(x=x, ndp=new_ndp, pm_val=pm_val)
            else:
                return r'{x:0.{ndp:d}f}\pm{pm_val:0.{ndp:d}f}'.format(x=x, ndp=new_ndp, pm_val=pm_val)