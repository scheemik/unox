import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import xarray as xr
import proplot as pplt
from datetime import datetime
import warnings
from scipy.stats import linregress

from unox import unox
from unox import data as udata
from unox import plot_format as uplt_fmt
from unox.input import x_or_y_var, get_input_index

title_font_size = 12

def plot_extent(
    xr_dataset='/datafiles/nox_2019_t106_US.nc',
    ):
    """Plots the extent of the given xarray dataset.

    Creates a map with the Robin projection of the entire world
    with a box showing the maximum extent of the dataset.

    Parameters
    ----------
    xr_dataset : str or xarray.Dataset or xarray.DataArray
        The xarray data for which to plot the extent or the file path to the dataset.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.

    Examples
    --------
    >>> fig = plot_extent(xr_dataset)
    """
    # Check if xr_dataset is a file path or an xarray object
    if isinstance(xr_dataset, str):
        # If it's a file path, verify the file path
        xr_dataset = unox.verify_path(xr_dataset)
        # Now open the dataset
        xr_dataset = xr.open_dataset(xr_dataset)
    # Verify the xr_dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Find the min and max lat and lon values
    lat_min, lat_max, lon_min, lon_max = udata.get_extent(xr_dataset)
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
        suptitle='Extent of xarray dataset',
        latlines=30, lonlines=30, coast=True,
        labels=True, gridminor=True
    )
    # Return the figure
    return fig

def plot_lats_lons(
    xr_dataset='/datafiles/nox_2019_t106_US.nc',
    padding=0.1,
    ):
    """Plot the latitude and longitude values in the given dataset.

    Creates a map showing the longitude and latitude resolution of the 
    given dataset.

    Parameters
    ----------
    xr_dataset : str or xarray.Dataset or xarray.DataArray
        The xarray data for which to plot the extent or the file path to the dataset.
    padding : float
        The padding (in a fraction of total extent) to add to the extent of the map. 
        Default is 0.1 degrees.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    
    Examples
    --------
    >>> fig = plot_lats_lons(xr_dataset)
    """
    # Check if xr_dataset is a file path or an xarray object
    if isinstance(xr_dataset, str):
        # If it's a file path, verify the file path
        xr_dataset = unox.verify_path(xr_dataset)
        # Now open the dataset
        xr_dataset = xr.open_dataset(xr_dataset)
    # Verify the xr_dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Find the min and max lat and lon values
    this_extent = udata.get_extent(xr_dataset)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_fmt.pad_extent(this_extent, padding)
    # Make a meshgrid of the lat and lon values
    longrid, latgrid = np.meshgrid(xr_dataset.lon.values, xr_dataset.lat.values)
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
        suptitle='Coordinates of xarray dataset',
        latlines=10, lonlines=10, coast=True,
        labels=True, gridminor=True
    )
    # Return the figure
    return fig

def plot_nc_map(
    xr_dataset='../datafiles/nox_2019_t106_US.nc',
    var='nox',
    var_string='NOx emissions',
    var_units='kg/m2/s',
    datetime='2019-01-01T00:00:00',
    avg_over=None,
    cmap=pplt.Colormap('Fire'),
    cbar_max=1.2e-10,
    padding=0.1,
    ):
    """Plots a map of the 'var' data in a netCDF.

    Creates a map of the 'var' data on a map using the provided netCDF file.

    Parameters
    ----------
    xr_dataset : str or xarray.Dataset or xarray.DataArray
        Path to the netCDF data file.
    var : str
        The name of the variable to plot from the netCDF file.
    var_string : str
        The string to use for the variable in the plot title and colorbar label.
    var_units : str
        The units of the variable to use in the colorbar label.
    datetime : str
        Date and time to select from the data file.
    avg_over : str, numpy.timedelta64, or None
        If provided, averages the data over the specified time period.
        If None, takes just the time slice specified in `datetime`.
    cmap : matplotlib.colors.Colormap
        The colormap to use for the plot. Default is pplt.cm.Fire.
    cbar_max : float
        Maximum value for the colorbar.
    padding : float
        The padding (in a fraction of total extent) to add to the extent of the map. 
        Default is 0.1 degrees.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    
    Examples
    --------
    >>> import xarray as xr
    >>> this_dataset = xr.open_dataset('../datafiles/sample_data/nox_2019_t106_US.nc')
    >>> fig = plot_nc_map(xr_dataset=this_dataset)
    """
    # Check if xr_dataset is a file path or an xarray object
    if isinstance(xr_dataset, str):
        # If it's a file path, verify the file path
        xr_dataset = unox.verify_path(xr_dataset)
        # Now open the dataset
        xr_dataset = xr.open_dataset(xr_dataset)
    
    # Simplest way to plot the data
    # this_var.nox[0].plot()

    # Verify the xr_dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Find the min and max lat and lon values
    this_extent = udata.get_extent(xr_dataset)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_fmt.pad_extent(this_extent, padding)
    # Select the time to plot
    if isinstance(avg_over, type(None)):
        # Take just that time slice
        var_sel_time = xr_dataset[var].sel(time=datetime)
        # Format a string for the title
        overall_title = var_string + ' on ' + datetime.split('T')[0]
    else:
        # Add the increment over which to average to the datetime
        try:
            end_date = udata.add_amount_to_date(datetime, avg_over)
        except:
            raise ValueError(f'Invalid avg_over value: {avg_over}')
        # Average over the specified amount of time
        var_sel_time = xr_dataset[var].sel(time=slice(datetime, end_date)).mean(dim='time')
        # Get the value and unit of the averaging
        avg_over_num, avg_over_unit = udata.get_increment_info(avg_over)
        # Format a string for the title
        overall_title = var_string + ' averaged over ' + str(avg_over_num) + ' ' + avg_over_unit + ' from ' + datetime.split('T')[0]

    # Find the min and max lat and lon values
    lat_min, lat_max, lon_min, lon_max = udata.get_extent(var_sel_time, check_time=False)
    # Create the figure
    fig = pplt.figure(refwidth=10)
    axs = fig.subplots(nrows=1, proj='cyl')
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 
    # Plot the data
    this_var = axs.pcolorfast(var_sel_time, vmin=0, vmax=cbar_max)
    # Format the map
    axs.format(
        lonlim=(p_lon_min, p_lon_max), latlim=(p_lat_min, p_lat_max),
        suptitle=overall_title,
        latlines=10, lonlines=10, coast=True,
        labels=True, gridminor=True
    )
    # Add a colorbar
    fig.colorbar(this_var, loc='b', label=var_string + ' (' + var_units + ')')
    # Return the figure
    return fig

def plot_npy_map(
    this_fig,
    this_ax,
    npy_arr,
    lats,
    lons,
    cmap=pplt.Colormap('seismic'),
    add_colorbar=False,
    c_halfrange=None,
    cb_extend='neither',
    ax_title='',
    ):
    """Plots a map of the given numpy array.

    Creates a map of the given numpy array across the given coordinates.

    Parameters
    ----------
    this_fig : matplotlib.figure.Figure
        The figure on which to plot the data.
    this_ax : matplotlib.axes.Axes
        The axes on which to plot the data.
    npy_arr : numpy.ndarray
        The numpy array to plot. Expects the shape (len(lons), len(lats)).
    lats : numpy.ndarray
        The latitude coordinates of the data.
    lons : numpy.ndarray
        The longitude coordinates of the data.
    cmap : matplotlib.colors.Colormap
        The colormap to use for the plot. Default is pplt.cm.seismic.
    add_colorbar : bool, optional
        Whether to add a colorbar on the right-hand side of the axis.
        Default is False.
    c_halfrange : float
        The half range for the color normalization on diverging colormaps.
    cb_extend : str
        The extension of the colorbar. Can be 'neither', 'both', 'min', or 'max'.
        Default is 'neither'.
    ax_title : str
        The title of the plot.

    Returns
    -------
    this_ax : matplotlib.axes.Axes
        The axes with the plotted data.

    Examples
    --------
    >>> fig, ax = pplt.subplots()
    >>> plot_npy_map(ax, npy_arr, lats, lons, title='NOx emissions')
    """
    # Verify the dimensions of the numpy array
    if npy_arr.shape != (len(lats), len(lons)):
        raise ValueError(f"npy_arr must have shape (len(lats), len(lons)). Expected: ({len(lats)}, {len(lons)}), got: {npy_arr.shape}")
    # Verify c_halfrange is a number

    # Plot the data
    if isinstance(c_halfrange, type(None)):
        pcm = this_ax.pcolormesh(lons, lats, npy_arr, cmap=cmap, shading='auto', levels=100)
    elif udata.verify_number(c_halfrange):
        pcm = this_ax.pcolormesh(lons, lats, npy_arr, cmap=cmap, shading='auto', levels=100, vmin=-1*c_halfrange, vmax=c_halfrange, extend=cb_extend)  
    else:
        raise TypeError(f'c_halfrange must be a number, got: {type(c_halfrange)}. c_halfrange value: {c_halfrange}')
    # Get the minimum and maximum latitude and longitude values
    (p_lat_min, p_lat_max, p_lon_min, p_lon_max) = udata.get_extent(lats=lats, lons=lons)
    # Format the map
    this_ax.format(
        lonlim=(p_lon_min, p_lon_max), latlim=(p_lat_min, p_lat_max),
        title=ax_title,
        latlines=10, lonlines=10, coast=True,
        labels=True, gridminor=True
    )
    # Add a colorbar on the right-hand side
    if add_colorbar:
        cbar = make_colorbar(this_fig, this_ax.get_children()[0], 'Values', num_ticks=9, cb_loc='r', cb_extend='neither')
    return this_ax, pcm

def plot_input_map(
    input_set='no2_sample_input',
    this_date='2019-07-19T00:00:00',
    var='nox',
    stage=1,
    avg_over=None,
    restrict_lat_lon_to=None,
    cmap=pplt.Colormap('Fire'),
    **kwargs,
    ):
    """Plots a map of input data for the specified variable and time.

    Creates a map of the input data for the specified variable and time,
    averaging over a time period if specified.

    Parameters
    ----------
    input_set : str
        The input set set to use. Default is 'no2_sample_input'.
    this_date : np.datetime64 or str
        Date and time to select from the data file.
        Expected format is 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DD'.
    var : str
        The variable being plotted. Default is 'nox'.
        Y files contain ['nox']
        X files contain ['no2', 'no2_tm1', 'u10', 'v10', 'blh', 'sp', 'skt', 't2m', 'ssrd']
    stage : int
        The stage of the data to use (1 or 2). Default is 1.
    avg_over : str, numpy.timedelta64, or None
        If provided, averages the data over the specified time period.
        If None, takes just the time slice specified in `datetime`.
    restrict_lat_lon_to : str   
        Path to a netCDF file to restrict the latitude and longitude range.
        If None, the entire dataset is used.
    cmap : matplotlib.colors.Colormap
        The colormap to use for the plot. Default is pplt.cm.Fire.
    **kwargs : dict
        Additional keyword arguments to pass to the `plot_npy_map` function.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    """
    # Get the latitude and longitude values
    lats, lons = unox.load_lats_lons()
    # Get the variable's x or y designation and index
    x_or_y = x_or_y_var(var)
    var_idx = get_input_index(var)
    # Get the date's DOY
    doy = udata.get_DOY(this_date)

    # Get the input filepath
    input_filepath = unox.get_input_data(
        stage=stage,
        x_or_y=x_or_y,
        year=int(this_date.split('-')[0]),
        input_set=input_set,
        **kwargs,
    )
    # Get the array to plot
    array_to_plot = unox.get_one_t_input_var_array(
        var,
        this_date,
        stage=stage,
        input_set=input_set,
    )
    # Create the figure
    fig = pplt.figure(refwidth=4)
    ax = fig.subplots(nrows=1, ncols=1, proj='cyl')
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 
    # Restrict the latitude and longitude range
    if not isinstance(restrict_lat_lon_to, type(None)):
        array_to_plot, lats, lons = udata.restrict_domain(array_to_plot, lats, lons, xr.open_dataset(restrict_lat_lon_to))
    # Add the subplot
    plot_npy_map(fig, ax, array_to_plot, lats=lats, lons=lons, cmap=cmap, **kwargs)
    # Add a colorbar on the right-hand side
    cbar = make_colorbar(fig, ax.get_children()[0], var+' ('+x_or_y+'_vars['+str(var_idx)+'])', num_ticks=9, cb_loc='r', cb_extend='neither')
    # Set the figure title
    overall_title = input_filepath + ' on DOY ' + str(doy)
    fig.suptitle(overall_title, fontsize=title_font_size)
    return fig

def plot_stage_comp_maps(
    truth_params={'stage': 1, 'x_or_y': 'y', 'year': 2019, 'input_set':'no2_sample_input'},
    pred_params={'HPC_run': 'no2_example_run', 'year': 2019},
    this_date='2019-07-19T00:00:00',
    var='nox',
    avg_over=None,
    restrict_lat_lon_to=None,
    clr_bar_scale=0.5,
    stage1_only=False,
    ):
    """Plots a set of maps to compare the truth and the two stages of the model.

    Creates a set of 6 maps:
    1. Truth
    2. Stage 1
    3. Stage 2
    4. Difference: Truth - Stage 1
    5. Difference: Truth - Stage 2
    6. Difference: Stage 1 - Stage 2

    Parameters
    ----------
    truth_params : dict
        Dictionary containing the parameters for the truth data.
        Must contain 'stage', 'x_or_y', 'year', and 'input_set' as designated
        in unox.data.get_input_data().
    pred_params : dict
        Dictionary containing the parameters for the predicted data to be passed to
        the function unox.get_pred_data().
    this_date : np.datetime64 or str
        Date and time to select from the data file.
        Expected format is 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DD'.
    var : str
        The variable being plotted. Default is 'nox'.
    avg_over : str, numpy.timedelta64, or None
        If provided, averages the data over the specified time period.
        If None, takes just the time slice specified in `datetime`.
    restrict_lat_lon_to : str
        Path to a netCDF file to restrict the latitude and longitude range.
        If None, the entire dataset is used.
    clr_bar_scale : float between 0 and 1
        Scale factor for the color bar. If set to 1, the color bar will be scaled 
        to the maximum absolute value of the data. Default is 0.5.
    stage1_only : bool
        If True, produce graphs just corresponding to stage 1. If False, produce graphs
        for stage 1 and stage 2. Default is False.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plots.
    """
    # Get the latitude and longitude values
    lats, lons = unox.load_lats_lons()
    # Get the "truth" values
    truth = np.load(unox.get_input_data(**truth_params))
    # Get the stage 1 values
    stage1 = np.load(unox.get_pred_data(stage=1, **pred_params))
    # Remove `stage` from pred_params, if present
    pred_params.pop('stage', None)
    
    if stage1_only:
        # Make a list of the data
        data_list = [truth, stage1]
        # Set the number of rows in the figure
        num_rows = 1
    else:
        # Get the stage 2 values
        stage2 = np.load(unox.get_pred_data(stage=2, **pred_params))
        # Make a list of the data
        data_list = [truth, stage1, stage2]
        # Set the number of rows in the figure
        num_rows = 2
        
    # Restrict the latitude and longitude range
    if not isinstance(restrict_lat_lon_to, type(None)):
        data_list, lats, lons = udata.restrict_domain(data_list, lats, lons, xr.open_dataset(restrict_lat_lon_to))

    # Get the minimum and maximum values across the truth, stage1, and stage2 arrays
    vmin, vmax = udata.get_vminmax(data_list)
    
    # Get the halfrange for use with a diverging color map
    chr = udata.get_max_abs_val([vmin, vmax])

    # Get the day of year to plot
    day = udata.get_DOY(this_date)

    # Create the figure
    fig = pplt.figure(refwidth=4)
    ax = fig.subplots(nrows=num_rows, ncols=3, proj='cyl')
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 

    # Scale the color bar
    if clr_bar_scale < 0 or clr_bar_scale > 1:
        warnings.warn("clr_bar_scale should be between 0 and 1. Setting it to 0.5.")
        clr_bar_scale = 0.5
    if clr_bar_scale != 1:
        chr *= clr_bar_scale
        cbe = 'both'
    else:
        cbe = 'neither'

    if stage1_only:
        # Create the output arrays for the stage comparison
        out_arrs, overall_title = uplt_fmt.make_stage_comp_arrs(
            in_arrs = {'truth': data_list[0], 'stage1': data_list[1]},
            this_date = this_date,
            var = var,
            avg_over = avg_over,
            stage1_only = True,
        )

        # Add the subplots
        plot_npy_map(fig, ax[0,0], out_arrs['truth'], lats, lons, c_halfrange=chr, cb_extend=cbe, ax_title=f'{var} emissions (truth)')
        plot_npy_map(fig, ax[0,1], out_arrs['stage1'], lats, lons, c_halfrange=chr, cb_extend=cbe, ax_title='Stage 1 prediction')
        plot_npy_map(fig, ax[0,2], out_arrs['t_m_st1'], lats, lons, c_halfrange=chr, cb_extend=cbe, ax_title='Truth - stage 1 prediction')
    else:
        # Create the output arrays for the stage comparison
        out_arrs, overall_title = uplt_fmt.make_stage_comp_arrs(
            in_arrs = {'truth': data_list[0], 'stage1': data_list[1], 'stage2': data_list[2]},
            this_date = this_date,
            var = var,
            avg_over = avg_over,
            stage1_only = False,
        )

        # Add the subplots
        plot_npy_map(fig, ax[0,0], out_arrs['truth'], lats, lons, c_halfrange=chr, cb_extend=cbe, ax_title=f'{var} emissions (truth)')
        plot_npy_map(fig, ax[0,1], out_arrs['stage1'], lats, lons, c_halfrange=chr, cb_extend=cbe, ax_title='Stage 1 prediction')
        plot_npy_map(fig, ax[0,2], out_arrs['stage2'], lats, lons, c_halfrange=chr, cb_extend=cbe, ax_title='Stage 2 prediction')
        plot_npy_map(fig, ax[1,0], out_arrs['t_m_st1'], lats, lons, c_halfrange=chr, cb_extend=cbe, ax_title='Truth - stage 1 prediction')
        plot_npy_map(fig, ax[1,1], out_arrs['t_m_st2'], lats, lons, c_halfrange=chr, cb_extend=cbe, ax_title='Truth - stage 2 prediction')
        plot_npy_map(fig, ax[1,2], out_arrs['st1_m_st2'], lats, lons, c_halfrange=chr, cb_extend=cbe, ax_title='Stage 1 - stage 2 prediction')

    # Get the variable label and units
    var_label, var_units = uplt_fmt.get_var_label_and_units(var)
    # Add one overall colorbar for the entire figure on the right-hand side
    cbar = make_colorbar(fig, ax[0,0].get_children()[0], var_label+' '+var_units, num_ticks=9, cb_loc='r', cb_extend=cbe)
    # Set the figure title
    fig.suptitle(overall_title, fontsize=title_font_size)
    return fig

def make_colorbar(
    fig,
    cb_ax,
    cb_label,
    num_ticks=9,
    cb_loc='l',
    cb_extend='neither',
    ):
    """Creates a colorbar for the given figure and axes.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure on which to add the colorbar.
    cb_ax : matplotlib.axes.Axes
        The axes on which to add the colorbar.
    cb_label : str
        The label for the colorbar.
    num_ticks : int
        The number of ticks for the colorbar. Default is 9.
    cb_loc : str
        The location of the colorbar. Default is 'l' (left).
    cb_extend : str
        The extension of the colorbar. Can be 'neither', 'both', 'min', or 'max'.
        Default is 'neither'.

    Returns
    -------
    cbar : matplotlib.colorbar.Colorbar
        The created colorbar.

    Examples
    --------
    >>> fig, ax = pplt.subplots()
    >>> cbar = make_colorbar(fig, ax, cb_label='NOx emissions (kg/m2/s)')
    """
    # Add one overall colorbar for the entire figure on the right-hand side
    cbar = fig.colorbar(cb_ax, loc=cb_loc, label=cb_label, extend=cb_extend)
    # Set ticks for the colorbar (use an odd number of ticks to have a zero tick in the middle)
    cbar.locator = mpl.ticker.LinearLocator(numticks = num_ticks)
    cbar.update_ticks()
    return cbar

def plot_comparison(
    npy_a, 
    npy_b,
    label_a='Array A',
    label_b='Array B',
    ax=None,
    hist_params={'bins':100, 'vmax':1000, 'vmin':10},
    cmap=pplt.Colormap('viridis'),
    log_scale=True,
    set_under_val=1,
    ):
    """
    Plot a comparison of two numpy arrays.

    Creates a correlation plot between the values of the two given numpy arrays.

    Parameters
    ----------
    npy_a : numpy.ndarray
        The first numpy array to compare.
    npy_b : numpy.ndarray
        The second numpy array to compare.
    label_a : str
        The label for the first array in the plot.
    label_b : str
        The label for the second array in the plot.
    ax : matplotlib.axes.Axes or None
        The axes on which to plot the data. If None, a new figure and axes are created.
    hist_params : dict
        Dictionary containing the parameters for the histogram.
        Must contain 'bins', 'vmax', and 'vmin'.
    cmap : matplotlib.colors.Colormap
        The colormap to use for the histogram. Default is pplt.cm.viridis.
    log_scale : bool
        If True, use a logarithmic scale for the histogram. Default is True.
    set_under_val : float
        The value to set for the underflow in the colormap. Default is 1.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.

    Examples
    --------
    >>> fig = plot_comparison(npy_a, npy_b)
    """
    # Verify, flatten, and squeeze the numpy arrays
    npy_a = udata.verify_npy(np.squeeze(npy_a).flatten())
    npy_b = udata.verify_npy(np.squeeze(npy_b).flatten())
    # Create a new figure and axis if none is provided
    if isinstance(ax, type(None)):
        new_fig = True
    else:
        new_fig = False
    if new_fig:
        fig, ax = pplt.subplots()
    # Set the values under `set_under_val` to white
    cmap.set_under('w', set_under_val)
    # Plot the data, depending on the scale
    if log_scale:
        these_ticks = [0.1, 1] + list(range(10, 1100, 100))
        this_hist, xedges, yedges, q = ax.hist2d(npy_a, npy_b, bins=hist_params['bins'], norm='log', cmap=cmap, vmin=hist_params['vmin'], vmax=hist_params['vmax'], extend='both')
        # cbar_kwargs={'ticks': these_ticks}, 
    else:
        these_ticks = None
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
    ax.plot(xx, xx, 'k--', lw=2, label='y=x')
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
        ax.plot(xx, slope*xx+intercept, 'r--', lw=2, label='y=%.2f x + %.2f, R^2=%.2f'%(slope, intercept, r_value**2))
    # Format the plot
    ax.set_aspect(1)
    ax.legend()
    ax.grid()
    ax.set_xlabel(label_a)
    ax.set_ylabel(label_b)
    # If new plot, return the figure
    if new_fig:
        ax.colorbar(q, loc='r', label='Count per pixel', formatter='sci')
        return fig
    else:
        return q

def plot_true_pred_comp(
    truth_data={'stage':1, 'x_or_y':'y', 'year':2019, 'input_set':'sample_data'},
    pred_data={'stage':1, 'HPC_run':'no2_example_run', 'year':2019},
    hist_params={'bins':100, 'vmax':1000, 'vmin':10},
    restrict_lat_lon_to=None,
    var='nox',
    ):
    """Plot a comparison of the truth and predicted data.

    Creates a correlation plot of the stage 1 data (truth) and the
    output of the model (prediction).

    Parameters
    ----------
    truth_data : dict
        Dictionary containing the parameters for the truth data.
        Must contain 'stage', 'x_or_y', 'year', and 'input_set'.
    pred_data : dict
        Dictionary containing the parameters for the predicted data.
        Must contain 'stage', 'HPC_run', and 'year'.
    hist_params : dict
        Dictionary containing the parameters for the histogram.
        Must contain 'bins', 'vmax', and 'vmin'.
    restrict_lat_lon_to : str
        Path to a netCDF file to restrict the latitude and longitude range.
        If None, the entire dataset is used.
    var : str
        The name of the gas being modelled. Default is 'nox'.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    
    Examples
    --------
    >>> fig = plot_comparison(truth_arr, pred_arr)
    """
    # Get the variable label and units
    var_label, var_units = uplt_fmt.get_var_label_and_units(var)
    # Load the data
    truth = np.load(unox.get_input_data(**truth_data))  #truth (y input file)
    stage1 = np.load(unox.get_pred_data(**pred_data))  #stage 1 prediction
    if not isinstance(restrict_lat_lon_to, type(None)):
        # Restrict range
        lats, lons = unox.load_lats_lons()
        [truth, stage1], lats, lons = udata.restrict_domain([truth, stage1], lats, lons, xr.open_dataset(restrict_lat_lon_to))
    truths = truth.flatten()
    preds = stage1.flatten()
    fig = plot_comparison(truths, preds, 
                           label_a=f"'Truth' surface {var_label} ({var_units})",
                           label_b=f"Stage 1 surface {var_label} ({var_units})",      
                           hist_params=hist_params)
    return fig

def plot_npy_hist(
    npy_arr,
    ax=None,
    n_bins=100,
    xlabel='NOx emissions (kg/m2/s)',
    ylabel='Frequency',
    title=None,
    log_scale=False,
    clr='blue',
    ):
    """Plots a histogram of the given numpy array.

    Creates a histogram of the given numpy array on the given axis, or
    creates a new figure and axis if none is provided.

    Parameters
    ----------
    npy_arr : numpy.ndarray
        The numpy array to plot.
    ax : matplotlib.axes.Axes, optional
        The axes on which to plot the histogram. If None, a new figure and axes are created.
    n_bins : int
        The number of bins to use for the histogram. Default is 100.
    xlabel : str
        The label for the x-axis. Default is 'NOx emissions (kg/m2/s)'.
    ylabel : str
        The label for the y-axis. Default is 'Frequency'.
    title : str, optional
        The title of the plot. If None, no title is set.
    log_scale : bool
        If True, the y-axis will be set to a logarithmic scale. Default is False.
    clr : str
        The color of the histogram bars. Default is 'blue'.

    Returns
    -------
    fig / ax : matplotlib.figure.Figure or matplotlib.axes.Axes
        The figure or axes containing the histogram.

    Examples
    --------
    >>> fig = plot_npy_hist(npy_arr)
    >>> ax[0] = plot_npy_hist(npy_arr, ax=ax[0], n_bins=50, title='Histogram of NOx emissions')
    """
    # Verify the numpy array
    npy_arr = udata.verify_npy(npy_arr)
    # Flatten the numpy array
    npy_arr_flat = npy_arr.flatten()
    # Create a new figure and axis if none is provided
    if isinstance(ax, type(None)):
        new_fig = True
    else:
        new_fig = False
    if new_fig:
        fig, ax = pplt.subplots()
    # Plot the histogram
    ax.hist(npy_arr_flat, bins=n_bins, color=clr, alpha=0.5, label='n = '+str(len(npy_arr_flat)))
    # Format the plot
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title)
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

def plot_npy_diff(
    npy_a,
    npy_b,
    title=None,
    filename=None,
    ):
    """Plots the difference between two numpy arrays.

    Assuming the npy arrays have dimensions (time, lat, lon), creates a heatmap of number of differences for all time across lat vs. lon and the number of differences for all locations across time.

    Parameters
    ----------
    npy_a : numpy.ndarray
        The first numpy array.
    npy_b : numpy.ndarray
        The second numpy array.
    title : str, optional
        The title of the plot. If None, no title is set.
    filename : str
        The filename to save the plot. Default is None.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.

    Examples
    --------
    >>> fig = plot_npy_diff(npy_a, npy_b)
    """
    # Verify the numpy arrays
    npy_a = udata.verify_npy(np.squeeze(npy_a))
    npy_b = udata.verify_npy(np.squeeze(npy_b))
    # Check if the shapes of the numpy arrays match
    if npy_a.shape != npy_b.shape:
        raise ValueError("The shapes of the numpy arrays do not match.")
    # Create an boolean array to tell where the two arrays differ
    ab_diff = npy_a != npy_b
    # Find total number of entries
    total_entries = np.prod(ab_diff.shape)
    print("Number of differences:", np.sum(ab_diff),'/', total_entries, '(', np.sum(ab_diff)/total_entries*100, '% )')
    if np.sum(ab_diff) == 0:
        no_diff = True
        print("The two arrays are identical. Skiping plot.")
        return
    else:
        no_diff = False

    # Create the figure
    ## Make the axis so that they don't share x ranges by setting `share=False`
    ## Setting `refwidth`` makes the figure a reasonable size
    ## The value of `refaspect` is the height divided by the width of each subplot
    fig, ax = pplt.subplots(nrows=3, ncols=2, proj={2:'cyl'}, refwidth=4, share=False, refaspect=1.8)

    # Plot line plot showing number of differences for all locations across time
    ax[0].plot(np.sum(ab_diff, axis=(1, 2)), color='red')
    # Don't share x or y axes with first plot
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Number of differences')

    # Plot map showing number of differences for all time
    lats, lons = unox.load_lats_lons()
    temp, pcm = plot_npy_map(fig, ax[1], np.sum(ab_diff, axis=0),
                            lats, lons,
                            ax_title=None,
                            cb_extend='max',
                            cmap=pplt.Colormap('viridis'))
    ax[1].set_xlabel('Longitude')
    ax[1].set_ylabel('Latitude')
    # # Add colorbar above the plot
    cbar = ax[1].colorbar(pcm, loc='t', label='Number of differences')

    # Plot a histograms of the both numpy arrays
    plot_npy_hist(npy_a, ax=ax[2], title='npy_a and npy_b', log_scale=True, clr='blue')
    plot_npy_hist(npy_b, ax=ax[2], title='npy_a and npy_b', log_scale=True, clr='red')

    # Plot a histograms of both arrays, just where they differ
    if no_diff == False:
        plot_npy_hist(npy_a[ab_diff], ax=ax[3], title='npy_a and npy_b, where they differ', log_scale=True, clr='blue')
        plot_npy_hist(npy_b[ab_diff], ax=ax[3], title='npy_a and npy_b, where they differ', log_scale=True, clr='red')

    # Plot a histogram of the differences between the two arrays, just where they differ
    if no_diff == False:
        delta_ab_diff = npy_a[ab_diff] - npy_b[ab_diff]
        plot_npy_hist(delta_ab_diff, ax=ax[4], title='npy_a - npy_b, where they differ', log_scale=True, clr='red')
    
    # Make a comparison plot
    if no_diff == False:
        q = plot_comparison(npy_a[ab_diff], npy_b[ab_diff],
                        label_a='npy_a (where they differ)',
                        label_b='npy_b (where they differ)',
                        ax=ax[5],
                        hist_params={'bins':100, 'vmax':1000, 'vmin':10},
                        cmap=pplt.Colormap('viridis'),
                        log_scale=True,
                        set_under_val=1)
        ax[5].colorbar(q, loc='r', label='Count per pixel', formatter='sci')

    # Set the title of the figure if provided
    if title is not None:
        fig.suptitle(title)
    fig.format()

    # Save the figure to file
    if filename is not None:
        fig.savefig(filename)
    return fig

def compare_input_files(
    year=2019,
    stage=1,
    var='no2',
    old_dir='no2_sample_input',
    new_dir='no2_input_test0',
    abs_tolerance=2e-5,
    ):
    """
    Compares new and old input files for the given year and stage.

    Parameters
    ----------
    year : int
        The year for which to compare the input files.
    stage : int
        The stage of the input files to compare.
    var : str
        The variable to pull out of the input file. Default is 'no2'. 
        Choose from the input_vars_dict
    old_dir : str
        The directory containing the old input files.
    new_dir : str
        The directory containing the new input files.
    abs_tolerance : float
        The absolute tolerance for comparing the input files. Default is 2e-5.
    """
    from unox.input import x_or_y_var, get_input_index
    # Get the x_or_y and index of the variable
    x_or_y = x_or_y_var(var)
    input_idx = get_input_index(var)
    # Assemble the paths to the old and new input files
    old_filepath = f'inputfiles/{old_dir}/stage{stage}/{x_or_y}/'+str(x_or_y).capitalize()+f'_{year}.npy'
    new_filepath = f'inputfiles/{new_dir}/stage{stage}/{x_or_y}/'+str(x_or_y).capitalize()+f'_{year}.npy'
    # Verify the file paths
    old_filepath = unox.verify_path(old_filepath)
    new_filepath = unox.verify_path(new_filepath)
    # Load the old and new input files
    old_input = np.load(old_filepath)
    new_input = np.load(new_filepath)
    # Pull out just the chosen variable from both arrays
    old_input = old_input[..., input_idx]
    new_input = new_input[..., input_idx]
    # Output the shapes
    print(f"Shape of {var} in {old_filepath}: \n\t{old_input.shape}")
    print(f"Shape of {var} in {new_filepath}: \n\t{new_input.shape}")
    # Are the arrays different?
    if np.array_equal(old_input, new_input):
        print(f"The input files are the same for {var}.")
        return None
    else:
        if np.allclose(old_input, new_input, atol=abs_tolerance):
            print("The input files are similar within the absolute tolerance of", abs_tolerance)
        else:
            print("The input files differ more than the tolerance of",abs_tolerance)
        # Plot the differences
        caps_x_or_y = str(x_or_y).capitalize()
        overall_title = f'{old_filepath} (old) vs {new_filepath} (new) for {var}'
        return plot_npy_diff(old_input, new_input, title=overall_title)