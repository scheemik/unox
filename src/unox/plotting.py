import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import xarray as xr
import proplot as pplt
from datetime import datetime
import warnings

from unox import unox
from unox import data as udata
from unox import plot_format as uplt_frmt

def plot_extent(xr_dataset='/datafiles/nox_2019_t106_US.nc'):
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
    udata.verify_dataset(xr_dataset)
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

def plot_lats_lons(xr_dataset='/datafiles/nox_2019_t106_US.nc',
                   padding=0.1):
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
    udata.verify_dataset(xr_dataset)
    # Find the min and max lat and lon values
    this_extent = udata.get_extent(xr_dataset)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_frmt.pad_extent(this_extent, padding)
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

def plot_nc_map(xr_dataset='../datafiles/nox_2019_t106_US.nc',
                var='nox',
                var_string='NOx emissions',
                var_units='kg/m2/s',
                datetime='2019-01-01T00:00:00',
                cbar_max=1.2e-10,
                padding=0.1):
    """Plots a map of the 'var' data in a netCDF.

    Creates a map of the 'var' data on a map using the provided netCDF file.

    Parameters
    ----------
    xr_dataset : str
        Path to the netCDF data file.
    var : str
        The name of the variable to plot from the netCDF file.
    var_string : str
        The string to use for the variable in the plot title and colorbar label.
    var_units : str
        The units of the variable to use in the colorbar label.
    datetime : str
        Date and time to select from the data file.
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
    >>> fig = plot_nc_map(xr_dataset='../datafiles/nox_2019_t106_US.nc')
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
    udata.verify_dataset(xr_dataset)
    # Find the min and max lat and lon values
    this_extent = udata.get_extent(xr_dataset)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_frmt.pad_extent(this_extent, padding)
    # Select the time to plot
    # var_sel_time = xr_dataset.nox.sel(time=datetime)
    var_sel_time = xr_dataset[var].sel(time=datetime)
    # Find the min and max lat and lon values
    lat_min, lat_max, lon_min, lon_max = udata.get_extent(var_sel_time)
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
        suptitle=var_string + ' on ' + datetime,
        latlines=10, lonlines=10, coast=True,
        labels=True, gridminor=True
    )
    # Add a colorbar
    fig.colorbar(this_var, loc='b', label=var_string + ' (' + var_units + ')')
    # Return the figure
    return fig

def plot_npy_map(this_fig,
                 this_ax,
                 npy_arr,
                 lats,
                 lons,
                 c_halfrange,
                 cb_extend='neither',
                 ax_title=''):
    """Plots a map of the given numpy array.

    Creates a map of the given numpy array across the given coordinates.

    Parameters
    ----------
    this_fig : matplotlib.figure.Figure
        The figure on which to plot the data.
    this_ax : matplotlib.axes.Axes
        The axes on which to plot the data.
    npy_arr : numpy.ndarray
        The numpy array to plot. Expects the shape (len(lons), len(lats), 1).
    lats : numpy.ndarray
        The latitude coordinates of the data.
    lons : numpy.ndarray
        The longitude coordinates of the data.
    c_halfrange : float
        The half range for the color normalization.
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
    >>> fig, ax = plt.subplots()
    >>> plot_npy_map(ax, npy_arr, lats, lons, title='NOx emissions')
    """
    # Plot the data
    pcm = this_ax.pcolormesh(lons, lats, npy_arr, cmap=plt.cm.seismic, shading='auto', levels=100, vmin=-c_halfrange, vmax=c_halfrange, extend=cb_extend)  
    # Get the minimum and maximum latitude and longitude values
    (p_lat_min, p_lat_max, p_lon_min, p_lon_max) = udata.get_extent(lats=lats, lons=lons)
    # Format the map
    this_ax.format(
        lonlim=(p_lon_min, p_lon_max), latlim=(p_lat_min, p_lat_max),
        title=ax_title,
        latlines=10, lonlines=10, coast=True,
        labels=True, gridminor=True
    )
    return this_ax

def plot_stage_comp_maps(truth_params={'stage': 1, 'x_or_y': 'y', 'year': 2019},
                pred_params={'stage': -1, 'HPC_run': 'test_unet_601760', 'year': 2019},
                this_date='2019-07-19T00:00:00',
                restrict_lat_lon_to=None,
                clr_bar_scale=0.5):
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
        Must contain 'stage', 'x_or_y', and 'year', as designated in unox.data.get_sample_data().
    pred_params : dict
        Dictionary containing the parameters for the predicted data.
        Must contain 'stage', 'HPC_run', and 'year', as designated in unox.data.get_pred_data().
    this_date : str
        Date and time to select from the data file.
    restrict_lat_lon_to : str
        Path to a netCDF file to restrict the latitude and longitude range.
        If None, the entire dataset is used.
    clr_bar_scale : float between 0 and 1
        Scale factor for the color bar. If set to 1, the color bar will be scaled 
        to the maximum absolute value of the data. Default is 0.5. 
    
    Returns
    -------
    """
    truth = np.load(unox.get_sample_data(**truth_params))
    # Remove `stage` from pred_params, if present
    pred_params.pop('stage', None)
    stage1 = np.load(unox.get_pred_data(stage=1, **pred_params))
    stage2 = np.load(unox.get_pred_data(stage=2, **pred_params))
    # Get the latitude and longitude values
    lats, lons = unox.load_lats_lons()

    if not isinstance(restrict_lat_lon_to, type(None)):
        # Restrict range
        [truth, stage1, stage2], lats, lons = udata.restrict_domain([truth, stage1, stage2], lats, lons, xr.open_dataset(restrict_lat_lon_to))
    
    # Get the minimum and maximum values across the truth, stage1, and stage2 arrays
    vmin, vmax = udata.get_vminmax([truth, stage1, stage2])
    # Get the halfrange for use with a diverging color map
    halfrange = udata.get_max_abs_val([vmin, vmax])

    # Get the day of year to plot
    day = datetime.strptime(this_date, '%Y-%m-%dT%H:%M:%S').timetuple().tm_yday

    # Create the figure
    fig = pplt.figure(refwidth=4)
    ax = fig.subplots(nrows=2, ncols=3, proj='cyl')
    # ax = fig.subplots(nrows=1, proj='cyl')
    # Set the figure title
    fig.suptitle('NOx emissions on ' + this_date, fontsize=16)
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 

    # Scale the color bar
    if clr_bar_scale < 0 or clr_bar_scale > 1:
        warnings.warn("clr_bar_scale should be between 0 and 1. Setting it to 0.5.")
        clr_bar_scale = 0.5
    if clr_bar_scale != 1:
        halfrange *= clr_bar_scale
        cb_extend = 'both'
    else:
        cb_extend = 'neither'
    print('cb_extend:', cb_extend)

    # Add the subplots
    # plot_npy_map(fig, ax, truth[day,:,:,0], lats, lons, halfrange, ax_title='NOx emissions (truth)')
    plot_npy_map(fig, ax[0,0], truth[day,:,:,0], lats, lons, halfrange, cb_extend, ax_title='NOx emissions (truth)')
    plot_npy_map(fig, ax[0,1], stage1[day,:,:,0], lats, lons, halfrange, cb_extend, ax_title='Stage 1 prediction')
    plot_npy_map(fig, ax[0,2], stage2[day,:,:,0], lats, lons, halfrange, cb_extend, ax_title='Stage 2 prediction')
    plot_npy_map(fig, ax[1,0], truth[day,:,:,0]-stage1[day,:,:,0], lats, lons, halfrange, cb_extend, ax_title='Truth - stage 1 prediction')
    plot_npy_map(fig, ax[1,1], truth[day,:,:,0]-stage2[day,:,:,0], lats, lons, halfrange, cb_extend, ax_title='Truth - stage 2 prediction')
    plot_npy_map(fig, ax[1,2], stage1[day,:,:,0]-stage2[day,:,:,0], lats, lons, halfrange, cb_extend, ax_title='Stage 1 - stage 2 prediction')

    # Add one overall colorbar for the entire figure on the right-hand side
    cbar = make_colorbar(fig, ax[0,0].get_children()[0], 'NOx emissions (kg/m2/s)', num_ticks=9, cb_loc='l', cb_extend=cb_extend)
    return fig

def make_colorbar(fig,
                  cb_ax,
                  cb_label,
                  num_ticks=9,
                  cb_loc='l',
                  cb_extend='neither'):
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
    >>> fig, ax = plt.subplots()
    >>> cbar = make_colorbar(fig, ax, cb_label='NOx emissions (kg/m2/s)')
    """
    # Add one overall colorbar for the entire figure on the right-hand side
    cbar = fig.colorbar(cb_ax, loc=cb_loc, label=cb_label, extend=cb_extend)
    # Set ticks for the colorbar (use an odd number of ticks to have a zero tick in the middle)
    cbar.locator = mpl.ticker.LinearLocator(numticks = num_ticks)
    cbar.update_ticks()
    return cbar

def plot_comparison(truth_data={'stage':1, 'x_or_y':'y', 'year':2019},
                    pred_data={'stage':1, 'HPC_run':'test_unet_601760', 'year':2019},
                    hist_params={'bins':100, 'vmax':1000, 'vmin':10},
                    restrict_lat_lon_to=None
                    ):
    """Plot a comparison of the truth and predicted data.

    Creates a correlation plot of the stage 1 data (truth) and the
    output of the model (prediction).

    Parameters
    ----------
    truth_data : dict
        Dictionary containing the parameters for the truth data.
        Must contain 'stage', 'x_or_y', and 'year'.
    pred_data : dict
        Dictionary containing the parameters for the predicted data.
        Must contain 'stage', 'HPC_run', and 'year'.
    hist_params : dict
        Dictionary containing the parameters for the histogram.
        Must contain 'bins', 'vmax', and 'vmin'.
    restrict_lat_lon_to : str
        Path to a netCDF file to restrict the latitude and longitude range.
        If None, the entire dataset is used.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    
    Examples
    --------
    >>> fig = plot_comparison(truth_arr, pred_arr)
    """
    from scipy.stats import linregress
    # Load the data
    truth = np.load(unox.get_sample_data(**truth_data))  #truth (y input file)
    stage1 = np.load(unox.get_pred_data(**pred_data))  #stage 1 prediction
    if not isinstance(restrict_lat_lon_to, type(None)):
        # Restrict range
        lats, lons = unox.load_lats_lons()
        [truth, stage1], lats, lons = udata.restrict_domain([truth, stage1], lats, lons, xr.open_dataset(restrict_lat_lon_to))
    truths = truth.flatten()
    preds = stage1.flatten()
    # Create the figure
    fig = plt.figure()
    # Select the color map
    my_cmap = plt.cm.jet
    my_cmap.set_under('w', 1)
    # Plot the data
    this_hist, xedges, yedges, q = plt.hist2d(truths, preds, bins=100, norm=mpl.colors.LogNorm(vmax=hist_params['vmax'], vmin=hist_params['vmin']), cmap=plt.cm.jet)
    # Count the maximum extent of the histogram where values are larger than vmin
    counts_0 = np.sum(this_hist > hist_params['vmin'], axis=0)
    counts_1 = np.sum(this_hist > hist_params['vmin'], axis=1)
    max_0 = max(np.where(counts_0 > 0, yedges[:-1], 0))
    max_1 = max(np.where(counts_1 > 0, xedges[:-1], 0))
    padding = 1.1
    axis_lim = max(max_0, max_1) * padding
    # Add line of y=x
    xx = np.arange(0, axis_lim, 1)
    plt.plot(xx, xx, 'k--', lw=2, label='y=x')
    # Limit the x and y axes
    plt.xlim((0, axis_lim))
    plt.ylim((0, axis_lim))
    # Plot the linear regression between the truth and predicted values
    slope, intercept, r_value, p_value, std_err = linregress(truths, preds)
    plt.plot(xx, slope*xx+intercept, 'r--', lw=2, label='y=%.2f x + %.2f, R^2=%.2f'%(slope, intercept, r_value**2))
    # Format the plot
    plt.colorbar(extend='both', ticks=[0.1, 0] + list(range(0, 1100, 100)) )
    plt.legend()
    plt.grid()
    plt.xlabel("'Truth' surface NO2 (ppb)")
    plt.ylabel("Stage 1 surface NO2 (ppb)")

def plot_npy_diff(npy_a,
                  npy_b,
                  filename='npy_diff.png'
                  ):
    """Plots the difference between two numpy arrays.

    Assuming the npy arrays have dimensions (time, lat, lon), creates a heatmap of number of differences for all time across lat vs. lon and the number of differences for all locations across time.

    Parameters
    ----------
    npy_a : numpy.ndarray
        The first numpy array.
    npy_b : numpy.ndarray
        The second numpy array.
    filename : str
        The filename to save the plot. Default is 'npy_diff.png'.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.

    Examples
    --------
    >>> fig = plot_npy_diff(npy_a, npy_b)
    """
    # Verify the numpy arrays
    npy_a = udata.verify_npy(npy_a)
    npy_b = udata.verify_npy(npy_b)
    # Check if the shapes of the numpy arrays match
    if npy_a.shape != npy_b.shape:
        raise ValueError("The shapes of the numpy arrays do not match.")
    # Create an boolean array to tell where the two arrays differ
    ab_diff = npy_a != npy_b
    # Find total number of entries
    total_entries = np.prod(ab_diff.shape)
    print("Number of differences:", np.sum(ab_diff),'/', total_entries, '(', np.sum(ab_diff)/total_entries*100, '% )')

    # Create the figure
    # Make the axis so that they don't share x ranges
    fig, ax = plt.subplots(nrows=2, ncols=1, sharex=False)

    # Plot heatmap showing number of differences for all time across lat vs. lon
    pcm = ax[0].pcolormesh(np.sum(ab_diff, axis=0), cmap='viridis', shading='auto')
    ax[0].set_xlabel('Longitude')
    ax[0].set_ylabel('Latitude')
    # Add colorbar
    cbar = plt.colorbar(pcm)
    # cbar = fig.colorbar(ax[0].get_children()[0], loc='t', label='Number of differences')

    # Plot line plot showing number of differences for all locations across time
    ax[1].plot(np.sum(ab_diff, axis=(1, 2)), color='red')
    # Don't share x or y axes with first plot
    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('Number of differences')

    return fig