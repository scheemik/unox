import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import xarray as xr
import proplot as pplt
from datetime import datetime
import warnings
from scipy.stats import linregress
import json
import os

from unox import data as udata
from unox.HPC.data0.dataset import uarray
from unox.HPC.data0.verify_dataset import verify_dataset, verify_var
from unox.HPC.data0.verify_dtype import verify_number
from unox import plot_format as uplt_fmt

# Set font sizes
mpl.rcParams['font.size'] = 16
mpl.rcParams['axes.labelsize'] = 16
mpl.rcParams['xtick.labelsize'] = 12
mpl.rcParams['ytick.labelsize'] = 12
mpl.rcParams['legend.fontsize'] = 12
title_font_size = 20

def plot_extent(
    dataset,
    **kwargs,
):
    """Plots the extent of the given dataset.

        Creates a map with the Robin projection of the entire world
        with a box showing the maximum N,S,E,W extent of the dataset.

        Parameters
        ----------
        dataset : `str`, `xarray.Dataset`, `xarray.DataArray`
            The dataset for which to plot the latitude / longitude extent.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `uarray()`.
        
        Returns
        -------
        fig : `matplotlib.figure.Figure`
            The figure object containing the plot.

        Examples
        --------
        >>> fig = plot_extent('inputfiles/no2_2019_JFM/no2_2019_JFM.nc')
        >>> fig = plot_extent('no2_2019_JFM', is_input_set=True)
    """
    # Verify argument types
    # Making `uarray` object verifies `dataset`
    u_arr = uarray(dataset, **kwargs)

    # Find the min and max lat and lon values
    lat_min, lat_max, lon_min, lon_max = udata.get_extent(u_arr.xr)
    # Find the midpoint of the longitude values to center the map
    lon_mid = (lon_min + lon_max) / 2
    # Create the figure
    fig = pplt.figure(refwidth=10)
    axs = fig.subplots(nrows=1, proj='robin', proj_kw={'lon_0': lon_mid})
    # Plot the extent as a bounding box
    axs.plot([lon_min, lon_min, lon_max, lon_max, lon_min],
             [lat_min, lat_max, lat_max, lat_min, lat_min],
             color='red', lw=2)
    # Format the map
    axs.format(
        suptitle=f'Extent of {u_arr.name}',
        latlines=30, lonlines=30, coast=True,
        labels=True, gridminor=True
    )
    # Return the figure
    return fig

def plot_lats_lons(
    dataset,
    padding=0.1,
    **kwargs,
):
    """Plot the latitude and longitude values of the given dataset.

        Creates a map showing the longitude and latitude resolution of the 
        given dataset in a checkerboard pattern.

        Parameters
        ----------
        dataset : `str`, `xarray.Dataset`, `xarray.DataArray`
            The dataset for which to plot the latitude and longitude grid.
        padding : `float`, optional
            The padding (in a fraction of total extent) to add to the extent of the map. 
            Default is `0.1`.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `uarray()`.
        
        Returns
        -------
        fig : `matplotlib.figure.Figure`
            The figure object containing the plot.
        
        Examples
        --------
        >>> fig = plot_lats_lons('inputfiles/no2_2019_JFM/no2_2019_JFM.nc')
        >>> fig = plot_lats_lons('no2_2019_JFM', is_input_set=True)
    """
    # Verify argument types 
    # Making `uarray` object verifies `dataset`
    u_arr = uarray(dataset, **kwargs)
    # `padding` is verified in `pad_extent()`
    
    # Find the min and max lat and lon values
    this_extent = udata.get_extent(u_arr.xr)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_fmt.pad_extent(this_extent, padding)
    # Make a meshgrid of the lat and lon values
    longrid, latgrid = np.meshgrid(u_arr.xr.lon.values, u_arr.xr.lat.values)
    # Create the figure
    fig = pplt.figure(refwidth=10)
    axs = fig.subplots(nrows=1, proj='cyl')
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 
    # Make a checkerboard pattern the size of the lat/longrid
    chk_brd = np.indices(longrid.shape).sum(axis=0) % 2
    # Plot a checker pattern of the lat and lon values
    axs.pcolorfast(longrid, latgrid, chk_brd, cmap="gray", alpha=0.5)
    # Format the map
    axs.format(
        lonlim=(p_lon_min, p_lon_max), latlim=(p_lat_min, p_lat_max),
        suptitle=f'Coordinates of {u_arr.name}',
        latlines=10, lonlines=10, coast=True,
        labels=True, gridminor=True
    )
    # Return the figure
    return fig

def map_ax(
    xr_arr,
    ax,
    plt_title=None,
    cmap=pplt.Colormap('Fire'),
    cbar_max=None,
    cbar_min=None,
    cb_ext='neither',
    padding=0.1,
    **kwargs,
):
    """Plots a map of the given data array.

        Creates a map of the given xarray DataArray on the axes provided. 
        The latitude and longitude values from `xr_arr` are used to set the extent of the map.

        Parameters
        ----------
        xr_arr : `xarray.DataArray`
            The xarray data to plot. Must not have a time dimension.
        ax : `matplotlib.axes.Axes`
            The axes on which to plot the data.
        plt_title : `str`, optional
            The title for the plot. 
            Default is `None`.
        cmap : `matplotlib.colors.Colormap`, optional
            The colormap to use for the plot. 
            Default is `pplt.cm.Fire`.
        cbar_max : `float`, optional
            Maximum value for the colorbar. When `None`, the colorbar max is set to the max value to plot.
            Default is `None`.
        cbar_min : `float`, optional
            Minimum value for the colorbar. When `None`, the colorbar max is set to the min value to plot.
            Default is `None`.
        cb_ext : `str`, optional
            How to extend the ends of the colorbar. Can be `'neither'`, `'both'`, `'min'`, or `'max'`.
            Default is `'neither'`.
        padding : `float`, optional
            The padding (in a fraction of total extent) to add to the extent of the map. 
            Default is `0.1`.
        **kwargs : keyword arguments
            Additional keyword arguments accepted to facilitate wrapper functions.
        
        Returns
        -------
        this_map_ax : `matplotlib.axes.Axes`
            The axes object containing the plot.
        clrbar_label : `str`
            The label for the colorbar containing the variable name and units.
        
        Examples
        --------
        >>> import proplot as pplt
        >>> fig, axs = pplt.subplots(nrows=1, ncols=2, proj='cyl')
        >>> this_xr = uarray('no2_2019_JFM', is_input_set=True).xr['no2']
        >>> this_xr = this_xr.sel(time='2019-01-02').squeeze(drop=True)
        >>> this_ax, cb_label = map_ax(this_xr, axs[0])
    """
    # Verify argument types
    if not isinstance(xr_arr, xr.DataArray):
        raise TypeError(f"(map_ax) `xr_arr` must be an xarray DataArray. Got type: {type(xr_arr)}")
    if not isinstance(ax, pplt.axes.Axes):
        raise TypeError(f"(map_ax) `ax` must be a proplot Axes object. Got type: {type(ax)}")
    if not isinstance(plt_title, (type(None), str)):
        raise TypeError(f"(map_ax) `plt_title` must be a string or None. Got type: {type(plt_title)}")
    if not isinstance(cmap, mpl.colors.Colormap):
        raise TypeError(f"(map_ax) `cmap` must be a matplotlib Colormap. Got type: {type(cmap)}")
    if not isinstance(cbar_max, type(None)):
        verify_number(cbar_max)
    if not isinstance(cbar_min, type(None)):
        verify_number(cbar_min)
    if cb_ext not in ['neither', 'both', 'min', 'max']:
        raise ValueError(f"(map_ax) `cb_ext` must be 'neither', 'both', 'min', or 'max'. Got: {cb_ext}")
    # `padding` is verified in `pad_extent()`

    # Verify the xr_arr. Assume there is no time dimension
    xr_arr = verify_dataset(xr_arr, check_time=False)
    # If there are any dimensions of size 1 (var, for example), squeeze them out
    xr_arr = xr_arr.squeeze(drop=True)
    # Check to ensure that `lat` and `lon` are the only remaining dimensions
    if not set(xr_arr.dims).issubset({'lat', 'lon'}):
        raise ValueError(f"(map_ax) `xr_arr` must have only 'lat' and 'lon' dimensions after squeezing. Got dimensions: {xr_arr.dims}")
    # Get the variable name from xr_arr
    var = xr_arr.name

    # Get the long name and units of the specified variable for plot labels
    try:
        var_name = xr_arr.long_name
        var_unit = xr_arr.units
    except:
        var_name = 'var'
        var_unit = 'units'

    # Find the min and max lat and lon values
    this_extent = udata.get_extent(xr_arr, check_time=False)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_fmt.pad_extent(this_extent, padding)

    # Get the maximum value for the colorbar
    if isinstance(cbar_max, type(None)):
        cbar_max = xr_arr.max()
        cbar_max = cbar_max.values
        cbar_max = np.unique(cbar_max)[0]
    # Get the minimum value for the colorbar
    if isinstance(cbar_min, type(None)):
        cbar_min = xr_arr.min()
        cbar_min = cbar_min.values
        cbar_min = np.unique(cbar_min)[0]
    # Plot the data, use `discrete=False` to set a continuous colorbar
    this_map_ax = ax.pcolormesh(xr_arr, vmin=cbar_min, vmax=cbar_max, discrete=False, extend=cb_ext, cmap=cmap)
    # Format the map
    ax.format(
        lonlim=(p_lon_min, p_lon_max), latlim=(p_lat_min, p_lat_max),
        title=plt_title,
        latlines=10, lonlines=10, coast=True,
        labels=True, gridminor=True
    )
    # Assemble colorbar label
    clrbar_label = f"{var_name} ({var_unit})"
    # Return the axis plot and colorbar label
    return this_map_ax, clrbar_label

def plot_var_maps(
    dataset,
    vars=['nox'],
    restrict_lat_lon_to=None,
    ens_mem=None,
    **kwargs,
):
    """Plots a maps of the given data.

        A wrapper for the `map_ax()` function.
        Creates maps for each specified 'var' using the provided dataset.

        Parameters
        ----------
        dataset : `str`, `xarray.Dataset`, `xarray.DataArray`
            The dataset for which to plot the specified variables.
        vars : `str`, `list`, optional
            The name(s) of the variable(s) to plot from the dataset.
            Default is `nox`.
        restrict_lat_lon_to : `str`, `None`, optional
            Path to a netCDF file to restrict the latitude and longitude range.
            If `None`, the entire dataset is used.
            Default is `None`.
        ens_mem : `int`, `None`, optional
            The ID of the ensemble member to plot. 
            If `None`, the dataset is assumed to not have multiple ensemble members.
            Default is `None`.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `uarray`, `select_time()`, `set_fig_row_col()` and `map_ax()`.
        
        Returns
        -------
        fig : `matplotlib.figure.Figure`
            The figure object containing the plot.
        
        Examples
        --------
        >>> fig = plot_var_maps('no2_example_run', is_predict=True, vars=['no2_pred'], datetime='2019-06-01', avg_over='30D')
    """
    # Verify argument types 
    # Making `uarray` object verifies `dataset`
    u_arr = uarray(dataset, **kwargs)
    if not isinstance(vars, list):
        if isinstance(vars, str):
            vars = [vars]
        else:
            raise TypeError(f"(plot_var_maps) `vars` must be a list of variable names or a single variable name string. Got type: {type(vars)}")
    else:
        for var in vars:
            if not isinstance(var, str):
                raise TypeError(f"(plot_var_maps) Each entry in `vars` must be a string. Got type: {type(var)}")
    if len(vars) == 0:
        raise ValueError("(plot_var_maps) `vars` list cannot be empty.")
    if not isinstance(restrict_lat_lon_to, (type(None), str)):
        raise TypeError(f"(plot_var_maps) `restrict_lat_lon_to` must be a string or None. Got type: {type(restrict_lat_lon_to)}")
    if isinstance(ens_mem, int):
        title_ens_ID = f"({ens_mem:02d})"
        ens_ID = f"_{ens_mem:02d}"
    elif isinstance(ens_mem, type(None)):
        title_ens_ID = ""
        ens_ID = ""
    else:
        raise TypeError(f"(plot_var_maps) `ens_mem` must be an integer or None. Got type: {type(ens_mem)}")
    
    # Select the time slice to plot
    u_arr.xr, title_segment = select_time(u_arr.xr, **kwargs)

    # Restrict the latitude and longitude range
    if not isinstance(restrict_lat_lon_to, type(None)):
        # Load the specified data set to restrict to
        restrict_xr = uarray(restrict_lat_lon_to).xr
        # Restrict the domain of the data to plot
        u_arr.xr, _ = udata.match_domains(u_arr.xr, restrict_xr, require_equal=False)

    # Create the figure
    fig = pplt.figure(refwidth=10)
    n_rows, n_cols = uplt_fmt.set_fig_row_col(len(vars), **kwargs)
    axs = fig.subplots(nrows=n_rows, ncols=n_cols, proj='cyl')
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 

    # Plot each of the variables
    for i in range(len(vars)):
        var = vars[i]+ens_ID
        # Verify that the variable is in the dataset
        verify_var(u_arr.xr, var)
        # Reduce the dataset to just the specified variable
        var_xr = u_arr.xr[var]
    
        # Add the plot to the axis
        this_var, clrbar_label = map_ax(
            var_xr,
            axs[i], 
            **kwargs,
        )
        # Add a colorbar
        axs[i].colorbar(this_var, loc='b', label=clrbar_label)
    # Add an overall title
    fig.suptitle(f"{u_arr.name}{title_ens_ID} {title_segment}", fontsize=title_font_size)
    # Return the figure
    return fig

def select_time(
    xr_data,
    datetime=None,
    avg_over=None,
    sum_vars=False,
    **kwargs,
):
    """Selects the time from an xarray to plot.

        Either selects a single time slice, averages over a time period, or sums over the entire available time dimension to result in an xarray without a time dimension, only lat-lon dimensions.

        Parameters
        ----------
        xr_data : `xarray.Dataset`, `xarray.DataArray`
            The xarray data to plot. Must have a time dimension.
        datetime : `str`, `None`, optional
            Date and time to select from the data file.
            Default is `None`.
        avg_over : `str`, `numpy.timedelta64`, `None`, optional
            If provided, averages the data over the specified time period.
            If None, takes just the time slice specified in `datetime`.
            Default is `None`.
        sum_vars : `bool`, optional
            Whether to sum across all time steps. Is ignored if `avg_over` is not None.
            Default is `False`.
        **kwargs : keyword arguments
            Additional keyword arguments accepted to facilitate wrapper functions.

        Returns
        -------
        xr_sel_time : `xarray.Dataset`, `xarray.DataArray`
            An xarray DataArray of the selected variable without a time dimension.
        title_segment : `str`
            A segment of the title string for the plot with time information.

        Examples
        --------
        >>> xr_data = uarray('no2_2019_JFM', is_input_set=True).xr
        >>> xr_sel_time, title_segment = select_time(xr_data, datetime='2019-01-15')
    """
    # Verify argument types
    xr_data = verify_dataset(xr_data, check_time=True)
    if not isinstance(datetime, (type(None), str, np.timedelta64)):
        raise TypeError(f"(select_time) `datetime` must be None, a string, or a numpy.timedelta64. Got type: {type(datetime)}")
    if not isinstance(avg_over, (type(None), str, np.timedelta64)):
        raise TypeError(f"(select_time) `avg_over` must be None, a string, or a numpy.timedelta64. Got type: {type(avg_over)}")
    if not isinstance(sum_vars, bool):
        raise TypeError(f"(select_time) `sum_vars` must be a bool. Got type: {type(sum_vars)}")

    # Select the time to plot
    if not isinstance(avg_over, type(None)):
        # Add the increment over which to average to the datetime
        try:
            end_date = udata.add_amount_to_date(datetime, avg_over)
        except:
            raise ValueError(f"(select_time) Invalid `avg_over` value: {avg_over}")
        # Average over the specified amount of time
        # Maintain attributes by using `drop=False` in sel() and `keep_attrs=True` in mean()
        xr_sel_time = xr_data.sel(time=slice(datetime, end_date), drop=False)
        xr_sel_time = xr_sel_time.mean(dim='time', keep_attrs=True)
        # Get the value and unit of the averaging
        avg_over_num, avg_over_unit = udata.get_increment_info(avg_over)
        # Format a string for the title
        title_segment = f"Averaged from {str(xr_data.time.values[0]).split('T')[0].split(' ')[0]} to {str(xr_data.time.values[-1]).split('T')[0].split(' ')[0]} ({avg_over_num} {avg_over_unit})"
    elif sum_vars == True:
        # Sum all the variables over time
        xr_sel_time = xr_data.sum(dim='time', keep_attrs=True).squeeze(drop=True)
        # Format a string for the title
        title_segment = f"Summed from {str(xr_data.time.values[0]).split('T')[0].split(' ')[0]} to {str(xr_data.time.values[-1]).split('T')[0].split(' ')[0]}"
    else:
        # Take just that time slice
        # Use squeeze to drop `time` dimension as sel() only automatically drops scalar
        # dimensions, which `time` is not
        xr_sel_time = xr_data.sel(time=datetime, drop=False).squeeze(drop=True)
        # Format a string for the title
        title_segment = datetime.split('T')[0]
    return xr_sel_time, title_segment

def plot_run_analysis(
    dataset,
    year,
    datetime=None,
    restrict_lat_lon_to=None,
    ens_mem=None,
    add_corr_plots=True,
    stage1_only=False,
    clr_bar_scale=0.5,
    clr_map=pplt.Colormap('Balance'),
    **kwargs,
):
    """Plots a set of maps to compare the 'truth' and the two stages of the model.

        Creates a set of 6 maps:
        1. 'Truth'
        2. Stage 1
        3. Stage 2
        4. Difference: 'Truth' - Stage 1
        5. Difference: 'Truth' - Stage 2
        6. Difference: Stage 1 - Stage 2

        Additionally adds correlation plots between:
        7. 'Truth' and Stage 1
        8. 'Truth' and Stage 2
        9. Stage 1 and Stage 2

        Parameters
        ----------
        dataset : `str`, `xarray.Dataset`, `xarray.DataArray`, `uarray`
            The dataset for which to make comparison maps. Must be a predictions dataset.
        year : `int`
            The year for which to make comparisons.
        datetime : `str`, `None`, optional
            Date and time to select from the data file.
            Default is `None`.
        restrict_lat_lon_to : `str`, `None`, optional
            Path to a netCDF file to restrict the latitude and longitude range.
            If `None`, the entire dataset is used.
            Default is `None`.
        ens_mem : `int`, `None`, optional
            The ID of the ensemble member to plot. 
            If `None`, the dataset is assumed to not have multiple ensemble members.
            Default is `None`.
        add_corr_plots : `bool`, optional
            Whether or not to add a row of correlation plots to the figure.
            Default is `True`.
        stage1_only : `bool`, optional
            If `True`, produce graphs just corresponding to stage 1. If `False`, produce graphs
            for stage 1 and stage 2. 
            Default is `False`.
        clr_bar_scale : `float`, optional
            Scale factor for the color bar, must be between `0` and `1`. If set to `1`, the color bar will be scaled to the maximum absolute value of the data. 
            Default is `0.5`.
        clr_map : `matplotlib.colors.Colormap`, optional
            The colormap to use for the map plots. 
            Default is `pplt.cm.Balance`.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `select_time()`, `map_ax()`, and `corr_plot()`.
        
        Returns
        -------
        fig : `matplotlib.figure.Figure`
            The figure object containing the plots.

        Examples
        --------
        >>> fig = plot_run_analysis('no2_example_run', year = 2019, datetime='2019-01-02',
        avg_over='364D', restrict_lat_lon_to='../datafiles/sample_data/nox_2019_t106_US.nc',  add_corr_plots=True)
    """
    # Verify argument types
    # Making `uarray` object verifies `dataset`
    pred_uarr = uarray(dataset, is_predict=True)
    if not isinstance(year, int):
        raise TypeError(f"(plot_run_analysis) `year` must be an integer. Got type: {type(year)}")
    if not isinstance(datetime, (type(None), str, np.timedelta64)):
        raise TypeError(f"(select_time) `datetime` must be None, a string, or a numpy.timedelta64. Got type: {type(datetime)}")
    elif isinstance(datetime, type(None)):
        datetime = f"{year}-01-02"
    if not isinstance(restrict_lat_lon_to, (type(None), str)):
        raise TypeError(f"(plot_run_analysis) `restrict_lat_lon_to` must be a string or None. Got type: {type(restrict_lat_lon_to)}")
    if isinstance(ens_mem, int):
        title_ens_ID = f"({ens_mem:02d})"
        ens_ID = f"_{ens_mem:02d}"
    elif isinstance(ens_mem, type(None)):
        title_ens_ID = ""
        ens_ID = ""
    else:
        raise TypeError(f"(plot_var_maps) `ens_mem` must be an integer or None. Got type: {type(ens_mem)}")
    if not isinstance(add_corr_plots, bool):
        raise TypeError(f"(plot_run_analysis) `add_corr_plots` must be a bool. Got type: {type(add_corr_plots)}")
    if not isinstance(stage1_only, bool):
        raise TypeError(f"(plot_run_analysis) `stage1_only` must be a bool. Got type: {type(stage1_only)}")
    verify_number(clr_bar_scale)
    if clr_bar_scale < 0 or clr_bar_scale > 1:
        raise ValueError(f"(plot_run_analysis) `clr_bar_scale` must be between 0 and 1. Got: {clr_bar_scale}")
    if not isinstance(clr_map, mpl.colors.Colormap):
        raise TypeError(f"(plot_run_analysis) `clr_map` must be a matplotlib Colormap. Got type: {type(clr_map)}")

    # Get the metadata from the predictions uarray
    meta_dict = pred_uarr._get_metadata()
    # Get the input set from the metadata
    input_set = meta_dict['config_dict']['input_set']
    # Get the input set used in the HPC run
    input_uarr = uarray(input_set, is_input_set=True)
    # Get and verify input set
    input_xarray = input_uarr.xr

    # Get the `y_var` name from the input dataset
    y_var = input_uarr.xr.attrs['y_var']
    # Make a list for the variables to plot
    vars_to_plot = [y_var]
    # Verify that the prediction array has the correct variable
    pred_var = f"{y_var}_pred{ens_ID}"
    verify_var(pred_uarr.xr, pred_var)
    vars_to_plot.append(pred_var)
    # Decide on the number of rows and columns in the figure
    if stage1_only == False:
        pred_var_s2 = f"{y_var}_pred_s2{ens_ID}"
        verify_var(pred_uarr.xr, pred_var_s2)
        vars_to_plot.append(pred_var_s2)
        # Set the number of rows and columns in the figure
        if add_corr_plots:
            n_rows = 3
            n_rows_maps = 2
        else:
            n_rows = 2
            n_rows_maps = 2
        n_cols = 3
        n_maps = 6
    else:
        # Set the number of rows and columns in the figure
        if add_corr_plots:
            n_rows = 2
            n_rows_maps = 1
            n_cols = 2
        else:
            n_rows = 1
            n_rows_maps = 1
            n_cols = 3
        n_maps = 3
    
    # Trim the latitude and longitude extents to match
    pred_uarr.xr, input_uarr.xr = udata.match_domains(pred_uarr.xr, input_uarr.xr)
    # Add the "truth" data to the prediction array
    pred_uarr.xr[y_var] = input_uarr.xr[y_var]
    # Select the time slice to plot
    ## Note: This will not affect the data used in the correlation plots
    pred_uarr.xr, time_title = select_time(pred_uarr.xr, datetime, **kwargs)

    # Restrict the latitude and longitude range
    ## Note: This will not affect the data used in the correlation plots
    if not isinstance(restrict_lat_lon_to, type(None)):
        # Load the specified data set to restrict to
        restrict_xr = uarray(restrict_lat_lon_to).xr
        # Restrict the domain of the data to plot
        pred_uarr.xr, _ = udata.match_domains(pred_uarr.xr, restrict_xr, require_equal=False)
        input_uarr.xr, _ = udata.match_domains(input_uarr.xr, restrict_xr, require_equal=False)

    # Get the units of the y_var
    y_var_unit = input_uarr.xr[y_var].units
    # Calculate the difference between the "truth" and the predictions
    pred_uarr.xr['y_m_st1'] = pred_uarr.xr[y_var] - pred_uarr.xr[pred_var]
    pred_uarr.xr['y_m_st1'].attrs = {'long_name': f"'Truth' - Stage 1 prediction", 'units': y_var_unit}
    vars_to_plot.append('y_m_st1')
    if stage1_only == False:
        pred_uarr.xr['y_m_st2'] = pred_uarr.xr[y_var] - pred_uarr.xr[pred_var_s2]
        pred_uarr.xr['y_m_st2'].attrs = {'long_name': f"'Truth' - Stage 2 prediction", 'units': y_var_unit}
        vars_to_plot.append('y_m_st2')
        pred_uarr.xr['st1_m_st2'] = pred_uarr.xr[pred_var] - pred_uarr.xr[pred_var_s2]
        pred_uarr.xr['st1_m_st2'].attrs = {'long_name': f"Stage 1 - Stage 2", 'units': y_var_unit}
        vars_to_plot.append('st1_m_st2')

    # Create tuple of the projections for each subplot
    if add_corr_plots == False:
        # Only one projection required
        these_projs = 'cyl'
    else:
        # Create a list of projections for each subplot
        these_projs = []
        for i in range(n_maps):
            these_projs.append('cyl')
        for i in range((n_rows * n_cols) - n_maps):
            these_projs.append(None)
    # Create the figure
    ## Setting `share=False` to allow separate axis labels for each subplot
    fig, axs = pplt.subplots(refwidth=4, nrows=n_rows, ncols=n_cols, proj=these_projs, share=False)
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 

    # Get the maximum and minimum values for each variable
    vmin_arr = pred_uarr.xr.min(skipna=True)
    vmax_arr = pred_uarr.xr.max(skipna=True)
    # Gather the maximum and mimum values across all variables
    val_list = []
    for var in vmin_arr.data_vars:
        val_list.append(vmin_arr[var].values)
        val_list.append(vmax_arr[var].values)
    # Get the halfrange for use with a diverging color map
    chr = udata.get_max_abs_val(val_list)
    # Scale the color bar
    if clr_bar_scale < 0 or clr_bar_scale > 1:
        warnings.warn("clr_bar_scale should be between 0 and 1. Setting it to 0.5.")
        clr_bar_scale = 0.5
    if clr_bar_scale != 1:
        chr *= clr_bar_scale
        cbe = 'both'
    else:
        cbe = 'neither'

    # Make blank lists to collect vars and colorbar labels
    these_vars = [None]*(n_maps)
    these_cblbls = [None]*(n_maps)
    # Add the plots to the axes
    for i in range(len(vars_to_plot)):
        data_arr = pred_uarr.xr[vars_to_plot[i]]
        # Add the plot to the axis
        these_vars[i], these_cblbls[i] = map_ax(
            data_arr,
            axs[i], 
            plt_title=data_arr.attrs['long_name'],
            cmap=clr_map,
            cbar_max=chr,
            cbar_min=-chr,
            cb_ext=cbe,
            **kwargs,
        )

    # Determine the colorbar label
    if len(set(these_cblbls)) == 1:
        cb_label = these_cblbls[0]
    else:
        cb_label = 'Labels vary'
        cb_label = these_cblbls[0]
    # Add one overall colorbar for the entire figure on the right-hand side
    cbar = make_colorbar(fig, these_vars[-1], cb_label, num_ticks=9, cb_loc='r', cb_extend=cbe, rows=(1, n_rows_maps))

    # Add correlation plots, if specified
    if add_corr_plots:
        # Create arrays to hold the plots
        fig_q_list = [None]*3
        # Add the three correlation plots to the figure
        fig_q_list[0] = corr_plot(
            dataset,
            is_predict=True,
            x_var='pred',
            y_var='truth',
            datetime=year,
            ax=axs[n_maps],
            restrict_lat_lon_to=restrict_lat_lon_to,
            ens_mem=ens_mem,
            **kwargs,
        )
        if stage1_only == False:
            fig_q_list[1] = corr_plot(
                dataset,
                is_predict=True,
                x_var='pred_s2',
                y_var='truth',
                datetime=year,
                ax=axs[-2],
                restrict_lat_lon_to=restrict_lat_lon_to,
                ens_mem=ens_mem,
                **kwargs,
            )
            fig_q_list[2] = corr_plot(
                dataset,
                is_predict=True,
                x_var='pred',
                y_var='pred_s2',
                datetime=year,
                ax=axs[-1],
                restrict_lat_lon_to=restrict_lat_lon_to,
                ens_mem=ens_mem,
                **kwargs,
            )
        # Add the colorbar
        fig.colorbar(fig_q_list[0], loc='r', label='Count per pixel', extend='both', formatter='sci', rows=(n_rows_maps+1, n_rows))

    # Set the figure title
    fig.suptitle(f"HPC run: {pred_uarr.name}{title_ens_ID}, input set: {input_set}, {time_title}", fontsize=title_font_size)
    return fig

def plot_comparison(
    a_xr_arr,
    b_xr_arr,
    ax=None,
    plt_title=None,
    a_label=None,
    b_label=None,
    cmap=pplt.Colormap('viridis'),
    set_under_val=1,
    hist_params={'bins':100, 'vmax':1000, 'vmin':10},
    log_scale=True,
    **kwargs,
):
    """Plot a comparison of two arrays.

        Creates a correlation plot between the values of the two given arrays.

        Parameters
        ----------
        a_xr_arr : `xarray.DataArray`, `numpy.ndarray`
            The first xarray DataArray or numpy array to compare.
        b_xr_arr : `xarray.DataArray`, `numpy.ndarray`
            The second xarray DataArray or numpy array to compare.
        ax : `matplotlib.axes.Axes`, optional
            The axes on which to plot the data.
            Default is `None`.
        plt_title : `str`, optional
            The title for the plot. 
            Default is `None`.
        a_label : `str`, optional
            The label to use for the first array.
        b_label : `str`, optional
            The label to use for the second array.
        cmap : `matplotlib.colors.Colormap`, optional
            The colormap to use for the plot. 
            Default is `pplt.cm.viridis`.
        set_under_val : `float`, optional
            The value below which to set the colormap to white.
            Default is `1`.
        hist_params : `dict`, optional
            The dictionary of values to set the 2D histogram parameters.
            Default is `{'bins':100, 'vmax':1000, 'vmin':10}`.
        log_scale : `bool`, optional
            Whether to use a logarithmic scale for the histogram.
            Default is `True`.
        **kwargs : keyword arguments
            Additional keyword arguments accepted to facilitate wrapper functions.
        
        Returns
        -------
        fig : `matplotlib.figure.Figure`
            The figure object containing the plot. Returned if `ax` is `None`.
        q : `QuadMesh`
            The QuadMesh object created by the 2D histogram. Returned if `ax` is given.
    """
    # Verify argument types
    if isinstance(a_xr_arr, xr.DataArray):
        a_xr_label = f"{a_xr_arr.attrs['long_name']} ({a_xr_arr.attrs['units']})"
        a_xr_arr = a_xr_arr.values
    elif not isinstance(a_xr_arr, (xr.DataArray, np.ndarray)):
        raise TypeError(f"(plot_comparison) `a_xr_arr` must be an xarray DataArray or numpy array. Got type: {type(a_xr_arr)}")
    else:
        a_xr_label = 'Array A'
    if isinstance(b_xr_arr, xr.DataArray):
        b_xr_label = f"{b_xr_arr.attrs['long_name']} ({b_xr_arr.attrs['units']})"
        b_xr_arr = b_xr_arr.values
    elif not isinstance(b_xr_arr, (xr.DataArray, np.ndarray)):
        raise TypeError(f"(plot_comparison) `b_xr_arr` must be an xarray DataArray or numpy array. Got type: {type(b_xr_arr)}")
    else:
        b_xr_label = 'Array B'
    if not isinstance(ax, (pplt.axes.Axes, type(None))):
        raise TypeError(f"(plot_comparison) `ax` must be a proplot Axes object or None. Got type: {type(ax)}")
    if not isinstance(plt_title, (type(None), str)):
        raise TypeError(f"(plot_comparison) `plt_title` must be a string or None. Got type: {type(plt_title)}")
    if isinstance(a_label, type(None)):
        a_label = a_xr_label
    elif not isinstance(a_label, str):
        raise TypeError(f"(plot_comparison) `a_label` must be a string or None. Got type: {type(a_label)}")
    if isinstance(b_label, type(None)):
        b_label = b_xr_label
    elif not isinstance(b_label, str):
        raise TypeError(f"(plot_comparison) `b_label` must be a string or None. Got type: {type(b_label)}")
    if not isinstance(cmap, mpl.colors.Colormap):
        raise TypeError(f"(plot_comparison) `cmap` must be a matplotlib Colormap. Got type: {type(cmap)}")
    verify_number(set_under_val)
    if not isinstance(hist_params, dict):
        raise TypeError(f"(plot_comparison) `hist_params` must be a dictionary. Got type: {type(hist_params)}")
    if not isinstance(log_scale, bool):
        raise TypeError(f"(plot_comparison) `log_scale` must be a bool. Got type: {type(log_scale)}")
    
    # Convert the xarray DataArrays to numpy arrays, 
    # then squeeze and flatten to get one dimensional arrays
    npy_a = np.squeeze(a_xr_arr).flatten()
    npy_b = np.squeeze(b_xr_arr).flatten()
    # Verify these arrays are the same length
    if len(npy_a) != len(npy_b):
        raise ValueError(f"(plot_comparison) `a_xr_arr` and `b_xr_arr` must have the same number of elements. Got lengths {len(npy_a)} and {len(npy_b)} respectively.")
    # Create a new figure and axis if none is provided
    if isinstance(ax, type(None)):
        new_fig = True
    else:
        new_fig = False
    if new_fig:
        # Create the figure
        fig = pplt.figure(refwidth=4)
        ax = fig.subplots(nrows=1, ncols=1)
    # Set the values under `set_under_val` to white
    cmap.set_under('w', set_under_val)
    # Plot the data, depending on the scale
    if log_scale:
        this_hist, xedges, yedges, q = ax.hist2d(npy_a, npy_b, bins=hist_params['bins'], norm='log', cmap=cmap, vmin=hist_params['vmin'], vmax=hist_params['vmax'], extend='both')
    else:
        this_hist, xedges, yedges, q = ax.hist2d(npy_a, npy_b, bins=hist_params['bins'], norm='linear', cmap=cmap)
    # Count the maximum extent of the histogram where values are larger than vmin
    counts_0 = np.sum(this_hist > hist_params['vmin'], axis=0)
    counts_1 = np.sum(this_hist > hist_params['vmin'], axis=1)
    max_0 = max(np.where(counts_0 > 0, yedges[:-1], 0))
    max_1 = max(np.where(counts_1 > 0, xedges[:-1], 0))
    padding = 1.1
    axis_lim = max(max_0, max_1) * padding
    # Add line of y=x
    xx = np.arange(0, axis_lim, 1)
    ax.plot(xx, xx, 'k--', lw=2)#, label='y=x')
    # Limit the x and y axes
    ax.set_xlim((0, axis_lim))
    ax.set_ylim((0, axis_lim))
    # Plot the linear regression between the truth and predicted values
    ## Only if neither array has all the same values
    if np.all(npy_a == npy_a[0]) or np.all(npy_b == npy_b[0]):
        warnings.warn("One of the arrays has all the same values. Skipping linear regression.")
    else:
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = linregress(npy_a, npy_b)
        if intercept < 0:
            pm_str = '-'
        else:
            pm_str = '+'
        ax.plot(xx, slope*xx+intercept, 'r--', lw=2, label=rf'$y=%.2fx{pm_str}%.2f$, $R^2$=%.2f'%(slope, abs(intercept), r_value**2))
    # Format the plot
    ax.set_aspect(1)
    ax.legend()
    ax.grid()
    ax.format(
        xlabel=a_label,
        ylabel=b_label,
    )
    # If new plot, return the figure
    if new_fig:
        # Add the colorbar
        ax.colorbar(q, loc='r', label='Count per pixel', formatter='sci')
        # Set the figure title
        fig.suptitle(plt_title, fontsize=title_font_size) 
        return fig
    else:
        return q

def corr_plot(
    dataset,
    x_var = 'pred',
    y_var = 'truth',
    datetime = 2019,
    restrict_lat_lon_to = None,
    ens_mem=None,
    **kwargs,
):
    """Makes a correlation plot of the two given variables.

        Creates a heatmap correlation plot with the specified variables on each axis
        using the data from the specified dataset, filtering based on the given datetime,
        period over which to average, and latitude/longitude restrictions.

        Parameters
        ----------
        dataset : `str`, `uarray`, `xarray.Dataset`, `xarray.DataArray`
            The dataset from which to get the data for the correlation plot.
        x_var : `str`, optional
            The variable to plot on the x-axis.
            Can be `truth`, `pred`, `pred_s2`, or any variable in the dataset.
            Default is `pred`.
        y_var : `str`, optional
            The variable to plot on the y-axis.
            Can be `truth`, `pred`, `pred_s2`, or any variable in the dataset.
            Default is `truth`.
        datetime : `int`, `str`, or `numpy.timedelta64`, optional
            If an integer year is provided, all the data from that year will be used.
            If a datetime is given, the data will be filtered by `select_time()`, using
            that datetime and the value of `avg_over`, if included in `**kwargs`. 
        restrict_lat_lon_to : `str`, `None`, optional
            Path to a netCDF file to restrict the latitude and longitude range.
            If `None`, the entire dataset is used.
            Default is `None`.
        ens_mem : `int`, `None`, optional
            The ID of the ensemble member to plot. 
            If `None`, the dataset is assumed to not have multiple ensemble members.
            Default is `None`.
        **kwargs : dict
            Additional keyword arguments to pass to `select_time()` and `plot_comparison()`.

        Returns
        -------
        fig_q : `matplotlib.figure.Figure`
            The figure object containing the plot.

        Examples
        --------
        >>> fig = corr_plot('no2_example_run', is_predict=True, x_ax='pred', y_ax='truth')
    """
    # Verify argument types
    # Making a `uarray` object verifies `dataset`
    u_arr = uarray(dataset, **kwargs)
    if not isinstance(x_var, str):
        raise ValueError(f"(corr_plot) `x_var` must be a string. Got type: {type(x_var)}")
    if not isinstance(y_var, str):
        raise ValueError(f"(corr_plot) `y_var` must be a string. Got type: {type(y_var)}")
    if isinstance(datetime, int):
        year = datetime
    elif not isinstance(datetime, (str, np.timedelta64)):
        raise TypeError(f"(corr_plot) `datetime` must be a string, or a numpy.timedelta64. Got type: {type(datetime)}")
    else:
        year = None
    if not isinstance(restrict_lat_lon_to, (type(None), str)):
        raise TypeError(f"(corr_plot) `restrict_lat_lon_to` must be a string or None. Got type: {type(restrict_lat_lon_to)}")
    if isinstance(ens_mem, int):
        title_ens_ID = f"({ens_mem:02d})"
        ens_ID = f"_{ens_mem:02d}"
    elif isinstance(ens_mem, type(None)):
        title_ens_ID = ""
        ens_ID = ""
    else:
        raise TypeError(f"(plot_var_maps) `ens_mem` must be an integer or None. Got type: {type(ens_mem)}")

    # Set the x and y data arrays to `None`
    x_xarr = None
    y_xarr = None
    # Verify the specified x and y axes are in the dataset
    if x_var in ['pred', 'pred_s2'] or y_var in ['pred', 'pred_s2']:
        # Make sure the dataset is a prediction uarray
        if not u_arr.is_predict:
            raise ValueError(f"(corr_plot) To plot 'pred' or 'pred_s2', `dataset` {u_arr.name} must be a prediction HPC run. Got {u_arr.name}.is_predict: {u_arr.is_predict}")
        # Get the name of the `y_var` used in the HPC run
        HPC_y_var = u_arr.xr.attrs['y_var']
        # Add that `y_var` to the predcition axes
        if 'pred' in x_var:
            x_var = f"{HPC_y_var}_{x_var}{ens_ID}"
            x_xarr = u_arr.xr[x_var]
        if 'pred' in y_var:
            y_var = f"{HPC_y_var}_{y_var}{ens_ID}"
            y_xarr = u_arr.xr[y_var]
    # Check whether to plot the 'truth'
    if x_var == 'truth' or y_var == 'truth':
        # Get the name of the `y_var` used in the input set
        HPC_y_var = u_arr.xr.attrs['y_var']
        # If the dataset is a prediction uarray
        if u_arr.is_predict:
            # Get the metadata from the predictions uarray
            meta_dict = u_arr._get_metadata()
            # Get the input set from the metadata
            input_set = meta_dict['config_dict']['input_set']
            # Get the input set used in the HPC run
            input_uarr = uarray(input_set, is_input_set=True)
        elif u_arr.is_input_set:
            input_uarr = u_arr
        else:
            raise ValueError(f"(corr_plot) To plot 'truth', `dataset` {u_arr.name} must be either a prediction HPC run or an input set. Got is_predict: {u_arr.is_predict}, is_input_set: {u_arr.is_input_set}")
        if x_var == 'truth':
            x_xarr = input_uarr.xr[HPC_y_var]
        if y_var == 'truth':
            y_xarr = input_uarr.xr[HPC_y_var]
    # Check whether both x and y data arrays have been set
    if isinstance(x_xarr, type(None)):
        # Verify the specified variable is in the dataset
        verify_var(u_arr.xr, x_var)
        # Set the x data array
        x_xarr = u_arr.xr[x_var]
    if isinstance(y_xarr, type(None)):
        # Verify the specified variable is in the dataset
        verify_var(u_arr.xr, y_var)
        # Set the x data array
        y_xarr = u_arr.xr[y_var]
    
    # Narrow the time range of the data
    if not isinstance(year, type(None)):
        # If `year` is set, select that year from the x and y data arrays
        x_xarr = x_xarr.sel(time=str(year))
        y_xarr = y_xarr.sel(time=str(year))
    else:
        # Otherwise, select the time over which to plot the correlation
        x_xarr, x_time_title = select_time(x_xarr, datetime=datetime, **kwargs)
        y_xarr, y_time_title = select_time(y_xarr, datetime=datetime, **kwargs)
    
    # Restrict the latitude and longitude range
    if not isinstance(restrict_lat_lon_to, type(None)):
        # Load the specified data set to restrict to
        restrict_xr = uarray(restrict_lat_lon_to).xr
        # Restrict the domain of the data to plot
        x_xarr, _ = udata.match_domains(x_xarr, restrict_xr, require_equal=False)
        y_xarr, _ = udata.match_domains(y_xarr, restrict_xr, require_equal=False)

    # Plot the comparison
    fig_q = plot_comparison(
        x_xarr,
        y_xarr,
        **kwargs,
    )
    return fig_q

def make_colorbar(
    fig,
    cb_ax,
    cb_label,
    num_ticks=9,
    cb_loc='r',
    cb_extend='neither',
    **kwargs,
):
    """Creates a colorbar for the given figure and axes.

        Parameters
        ----------
        fig : `matplotlib.figure.Figure`
            The figure on which to add the colorbar.
        cb_ax : `cartopy.mpl.geocollection.GeoQuadMesh`
            The geo quad mesh on which to add the colorbar.
        cb_label : `str`
            The label for the colorbar.
        num_ticks : `int`, optional
            The number of ticks for the colorbar. 
            Default is `9`.
        cb_loc : `str`, optional
            The location of the colorbar. Default is 'r' (right).
        cb_ext : `str`, optional
            How to extend the ends of the colorbar. Can be `'neither'`, `'both'`, `'min'`, or `'max'`.
            Default is `'neither'`.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to `colorbar()`, such as the `rows` tuple.

        Returns
        -------
        cbar : `matplotlib.colorbar.Colorbar`
            The generated colorbar.

        Examples
        --------
        >>> fig, axs = pplt.subplots(nrows=3, ncols=3)
        >>> n_rows_maps = 2
        >>> cbar = make_colorbar(fig, axs, cb_label='NOx emissions (kg/m2/s)', rows=(1, n_rows_maps))
    """
    from cartopy.mpl.geocollection import GeoQuadMesh
    # Verify argument types
    if not isinstance(fig, mpl.figure.Figure):
        raise TypeError(f"(make_colorbar) `fig` must be a matplotlib Figure. Got type: {type(fig)}")
    if not isinstance(cb_ax, GeoQuadMesh):
        raise TypeError(f"(make_colorbar) `cb_ax` must be a GeoQuadMesh. Got type: {type(cb_ax)}")
    if not isinstance(cb_label, str):
        raise TypeError(f"(make_colorbar) `cb_label` must be a string. Got type: {type(cb_label)}")
    if not isinstance(num_ticks, int):
        raise TypeError(f"(make_colorbar) `num_ticks` must be an integer. Got type: {type(num_ticks)}")
    if not isinstance(cb_loc, str):
        raise TypeError(f"(make_colorbar) `cb_loc` must be a string. Got type: {type(cb_loc)}")
    if not isinstance(cb_extend, str):
        raise TypeError(f"(make_colorbar) `cb_extend` must be a string. Got type: {type(cb_extend)}")

    # Add one overall colorbar for the entire figure on the right-hand side
    cbar = fig.colorbar(cb_ax, loc=cb_loc, label=cb_label, extend=cb_extend, **kwargs)
    # Set ticks for the colorbar (use an odd number of ticks to have a zero tick in the middle)
    cbar.locator = mpl.ticker.LinearLocator(numticks = num_ticks)
    cbar.update_ticks()
    return cbar

def plot_hist(
    data_arrs,
    ax=None,
    n_bins=100,
    ax_label='NOx emissions (kg/m2/s)',
    ylabel='Frequency',
    plt_title=None,
    log_scale=False,
):
    """Plots a histogram of the given array(s).

        Creates a histogram of the given data on the given axis, or creates a new figure and axis if none is provided.
        Each array in `data_arrs` is plotted as a separate histogram on the same axes.

        Parameters
        ----------
        data_arrs : `list`, `numpy.ndarray`, `xr.DataArray`
            The array(s) to plot.
        ax : `matplotlib.axes.Axes`, `None`, optional
            The axes on which to plot the histogram. If `None`, a new figure and axes are created.
            Default is `None`.
        n_bins : `int`, optional
            The number of bins to use for the histogram. 
            Default is `100`.
        ax_label : `str`, optional
            The label for the x-axis. 
            Default is `'NOx emissions (kg/m2/s)'`.
        ylabel : `str`, optional
            The label for the y-axis. 
            Default is `'Frequency'`.
        plt_title : `str`, optional
            The title of the plot. If `None`, no title is set.
            Default is `None`.
        log_scale : `bool`, optional
            If `True`, the y-axis will be set to a logarithmic scale. 
            Default is `False`.

        Returns
        -------
        fig / ax : `matplotlib.figure.Figure` or `matplotlib.axes.Axes`
            The figure or axes containing the histogram.

        Examples
        --------
        >>> data_arr1 = uarray('nox_2019_JFM', is_input_set=True).xr['no2'].values
        >>> data_arr2 = uarray('nox_2019_JFM', is_input_set=True).xr['no2_s2'].values
        >>> fig = plot_npy_hist(data_arr1)
        
        >>> fig, axs = pplt.subplots(nrows=2, ncols=1)
        >>> axs[0] = plot_npy_hist([data_arr1, data_arr2], ax=axs[0], n_bins=50, title='Histogram of NO2 emissions, both stages')
    """
    # Verify argument types
    if not isinstance(data_arrs, list):
        if isinstance(data_arrs, (np.ndarray, xr.DataArray)):
            data_arrs = [data_arrs]
        else:
            raise TypeError(f"(plot_hist) `data_arrs` must be a list, numpy array, or xarray DataArray. Got type: {type(data_arrs)}")
    else:
        for data_arr in data_arrs:
            if not isinstance(data_arr, (np.ndarray, xr.DataArray)):
                raise TypeError(f"(plot_hist) Each element of `data_arrs` must be a numpy array or xarray DataArray. Got type: {type(data_arr)}")
    if not isinstance(ax, (pplt.axes.Axes, type(None))):
        raise TypeError(f"(plot_hist) `ax` must be a proplot Axes object or None. Got type: {type(ax)}")
    if not isinstance(n_bins, int):
        raise TypeError(f"(plot_hist) `n_bins` must be an integer. Got type: {type(n_bins)}")
    if not isinstance(ax_label, str):
        raise TypeError(f"(plot_hist) `ax_label` must be a string. Got type: {type(ax_label)}")
    if not isinstance(ylabel, str):
        raise TypeError(f"(plot_hist) `ylabel` must be a string. Got type: {type(ylabel)}")
    if not isinstance(plt_title, (type(None), str)):
        raise TypeError(f"(plot_hist) `plt_title` must be a string or None. Got type: {type(plt_title)}")
    if not isinstance(log_scale, bool):
        raise TypeError(f"(plot_hist) `log_scale` must be a bool. Got type: {type(log_scale)}")

    # Create a new figure and axis if none is provided
    if isinstance(ax, type(None)):
        new_fig = True
    else:
        new_fig = False
    if new_fig:
        fig, ax = pplt.subplots()
    # Loop across the data arrays
    for data_arr in data_arrs:
        if isinstance(data_arr, xr.DataArray):
            data_arr = data_arr.values
        # Flatten the array
        flat_arr = data_arr.flatten()
        # Plot the histogram
        ax.hist(flat_arr, bins=n_bins, alpha=0.5, label='n = '+str(len(flat_arr)))
    # Format the plot
    ax.set_xlabel(ax_label)
    ax.set_ylabel(ylabel)
    if not isinstance(plt_title, type(None)):
        ax.set_title(plt_title)
    if log_scale:
        ax.set_yscale('log')
        # Set the ticks to scientific notation
        ax.format(yformatter='sci')
    # Add legend to show the number of values in the histogram
    ax.legend()
    # If new plot, return the figure
    if new_fig:
        return fig
    else:
        return ax

def compare_input_vars(
    input_a_dict = {
        'input_set':'no2_2019_JFM',
        'year':2019,
        'var':'no2',
    },
    input_b_dict = {
        'input_set':'no2_2019_JFM',
        'year':2019,
        'var':'no2_s2',
    },
    abs_tolerance=2e-5,
    restrict_lat_lon_to=None,
):
    """Compares the data for two input variables.

        Parameters
        ----------
        input_dict_a : `dict`, optional
            Dictionary containing the parameters for the first input variable.
            Must contain `'input_set'`, `'year'`, and `'var'`. 
        input_dict_b : `dict`, optional
            Dictionary containing the parameters for the second input variable.
            Must contain `'input_set'`, `'year'`, and `'var'`. 
        abs_tolerance : `float`, optional
            The absolute tolerance for comparing the input files. 
            Default is `2e-5`.
        restrict_lat_lon_to : `str`, `None`, optional
            Path to a netCDF file to restrict the latitude and longitude range.
            If `None`, the entire dataset is used.
            Default is `None`.
        
        Returns
        -------
        None
            If the input files match within the given tolerance.
        fig : `matplotlib.figure.Figure`
            If the input files differ more than the given tolerance, a figure is returned.
        
        Examples
        --------
        >>> fig = compare_input_vars(
        ...     {
        ...         'input_set': 'no2_2019_JFM',
        ...         'year': 2019,
        ...         'var': 'no2',
        ...     },
        ...     {
        ...         'input_set': 'no2_2019_JFM',
        ...         'year': 2019,
        ...         'var': 'no2_s2',
        ...     },
        ...     restrict_lat_lon_to='../datafiles/sample_data/nox_2019_t106_US.nc',
        ... )
    """
    # Verify argument types
    for input_dict in [input_a_dict, input_b_dict]:
        if not isinstance(input_dict, dict):
            raise TypeError(f"(compare_input_vars) `input_dict` must be a dictionary. Got: {type(input_dict)}")
        required_keys = ['input_set', 'year', 'var']
        for key in required_keys:
            if key not in input_dict:
                raise KeyError(f"(compare_input_vars) `input_dict` must contain the key '{key}'.")
        if not isinstance(input_dict['input_set'], str):
            raise TypeError(f"(compare_input_vars) `input_set` must be a string. Got type: {type(input_dict['input_set'])}")
        if not udata.verify_number(input_dict['year']):
            raise TypeError(f"(compare_input_vars) `year` must be an integer. Got type: {type(input_dict['year'])}")
        if not isinstance(input_dict['var'], str):
            raise TypeError(f"(compare_input_vars) `var` must be a string. Got type: {type(input_dict['var'])}")
    if not isinstance(abs_tolerance, float):
        raise TypeError(f"(compare_input_vars) `abs_tolerance` must be a float. Got type: {type(abs_tolerance)}")
    if not isinstance(restrict_lat_lon_to, (type(None), str)):
        raise TypeError(f"(compare_input_vars) `restrict_lat_lon_to` must be a string or None. Got type: {type(restrict_lat_lon_to)}")

    # Loop over the two input dictionaries and load the data
    for input_dict in [input_a_dict, input_b_dict]:
        # Load the input data as a uarray
        input_dict['u_arr'] = uarray(input_dict['input_set'], is_input_set=True)
        # Narrow the time range of the data
        input_dict['u_arr'].xr = input_dict['u_arr'].xr.sel(time=str(input_dict['year']))
        # Restrict the latitude and longitude range
        if not isinstance(restrict_lat_lon_to, type(None)):
            # Load the specified data set to restrict to
            restrict_xr = uarray(restrict_lat_lon_to).xr
            # Restrict the domain of the data to plot
            input_dict['u_arr'].xr, _ = udata.match_domains(input_dict['u_arr'].xr, restrict_xr, require_equal=False)
        # Get the xarray dataset for just the given variable
        this_input = input_dict['u_arr'].xr[input_dict['var']]
        # If y_var, remove extra dimension
        if input_dict['var'] == input_dict['u_arr'].xr.attrs['y_var']:
            this_input = this_input.squeeze()
        input_dict['data_array'] = this_input
        print(f"Shape of {input_dict['var']} from {input_dict['input_set']}: {this_input.shape}")
    # Check whether the data arrays are the same size
    if input_a_dict['data_array'].shape != input_b_dict['data_array'].shape:
        raise ValueError(f"(compare_input_vars) The shapes of the input data arrays do not match. Got: {input_a_dict['data_array'].shape} and {input_b_dict['data_array'].shape}")
    # Are the arrays different?
    if np.array_equal(input_a_dict['data_array'], input_b_dict['data_array']):
        print(f"Match found for {input_a_dict['input_set']}-{input_a_dict['year']}-{input_a_dict['var']} vs {input_b_dict['input_set']}-{input_b_dict['year']}-{input_b_dict['var']}.")
        return None
    else:
        if np.allclose(input_a_dict['data_array'], input_b_dict['data_array'], atol=abs_tolerance):
            print("The input files are similar within the absolute tolerance of", abs_tolerance)
        else:
            print("The input files differ more than the tolerance of",abs_tolerance)
        # Plot the differences

        # Create an boolean variable to tell where the two arrays differ
        input_a_dict['u_arr'].xr['ab_diff'] = input_a_dict['u_arr'].xr[input_a_dict['var']] != input_b_dict['u_arr'].xr[input_b_dict['var']]
        # Put that variable into an array
        ab_diff = np.array(input_a_dict['u_arr'].xr['ab_diff'].values).squeeze()
        total_diffs = np.sum(ab_diff)
        # Find total number of entries
        total_entries = np.prod(ab_diff.shape)
        print("Number of differences:", total_diffs,'/', total_entries, '(', total_diffs/total_entries*100, '% )')

        # Create the figure
        ## Make the axis so that they don't share x ranges by setting `share=False`
        ## Setting `refwidth`` makes the figure a reasonable size
        ## The value of `refaspect` is the height divided by the width of each subplot
        fig, ax = pplt.subplots(nrows=3, ncols=2, proj={2:'cyl'}, refwidth=4, share=False, refaspect=1.8)

        ## Plot 0: Line plot showing number of differences across time
        diff_arr = np.sum(ab_diff, axis=(1, 2))
        # time_arr = input_a_dict['u_arr'].xr['time'].values
        # time_arr = [date.to_datetimeindex() for date in time_arr]
        # # Make the date locator
        # loc = mpl.dates.AutoDateLocator()
        # ax[0].xaxis.set_major_locator(loc)
        # ax[0].xaxis.set_major_formatter(mpl.dates.ConciseDateFormatter(loc))

        # Plot line plot showing number of differences for all locations across time
        ax[0].plot(diff_arr, color='red')
        # Don't share x or y axes with first plot
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Number of differences')

        ## Plot 1: A map showing where the differences are
        # Create an xarray DataArray of the sum of the differences over time
        this_x_arr1, title_segment = select_time(
            input_a_dict['u_arr'].xr,
            sum_vars=True,
        )
        # Define metadata for that DataArray
        this_x_arr1['ab_diff'].attrs['long_name'] = 'Differences'
        this_x_arr1['ab_diff'].attrs['units'] = 'count'
        ax1_var, ax1_clrbar_label = map_ax(
            this_x_arr1['ab_diff'],
            ax[1],
            plt_title=title_segment,
            cmap=pplt.Colormap('Viridis'),
        )
        # Add a colorbar
        ax[1].colorbar(ax1_var, loc='r', label=ax1_clrbar_label)

        # Format a label for the histograms
        hist_units = f"{input_a_dict['u_arr'].xr[input_a_dict['var']].attrs['units']}"
        hist_label = f"{input_a_dict['u_arr'].xr[input_a_dict['var']].attrs['long_name']} ({hist_units})"

        ## Plot 2: Histograms of both inputs
        plot_hist(
            [input_a_dict['data_array'], input_b_dict['data_array']],
            ax=ax[2],
            plt_title='Input data arrays',
            ax_label=hist_label,
            log_scale=True,
        )

        # Get arrays of the inputs where they differ
        a_where_differ = input_a_dict['u_arr'].xr[input_a_dict['var']].where(input_a_dict['u_arr'].xr['ab_diff']).values
        b_where_differ = input_b_dict['u_arr'].xr[input_b_dict['var']].where(input_a_dict['u_arr'].xr['ab_diff']).values
        # Flatten all three arrays and remove NaN values
        a_differ_flat = a_where_differ[~np.isnan(a_where_differ)].flatten()
        b_differ_flat = b_where_differ[~np.isnan(b_where_differ)].flatten()
        # Get the difference between these two arrays
        delta_ab_flat = a_differ_flat - b_differ_flat

        ## Plot 3: Histograms of both inputs, where they differ
        plot_hist(
            [a_differ_flat, b_differ_flat],
            ax=ax[3],
            plt_title='Input data arrays where they differ',
            ax_label=hist_label,
            log_scale=True,
        )

        ## Plot 4: Histogram of the differences between both inputs, where they differ
        plot_hist(
            [delta_ab_flat],
            ax=ax[4],
            plt_title='Difference between inputs where they differ',
            ax_label=hist_label,
            log_scale=True,
        )

        ## Plot 5: Correlation plot between both inputs, where they differ
        q = plot_comparison(
            a_differ_flat,
            b_differ_flat,
            ax=ax[5],
            a_label=f"Array A ({hist_units})",
            b_label=f"Array B ({hist_units})",
        )
        # Add the colorbar
        ax[5].colorbar(q, loc='r', label='Count per pixel', formatter='sci')

        # Set the figure title
        overall_title = f"{input_a_dict['input_set']}-{input_a_dict['year']}-{input_a_dict['var']} vs {input_b_dict['input_set']}-{input_b_dict['year']}-{input_b_dict['var']}"
        fig.suptitle(overall_title)
        return fig
