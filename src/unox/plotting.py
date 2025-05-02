import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import xarray as xr
import proplot as pplt

from unox import unox
from unox import data as unox_data
from unox import plot_format as uplt_frmt

def plot_extent(xr_dataset=xr.open_dataset('../datafiles/nox_2019_t106_US.nc')):
    """Plots the extent of the given xarray dataset.

    Creates a map with the Robin projection of the entire world
    with a box showing the maximum extent of the dataset.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data for which to plot the extent.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.

    Examples
    --------
    >>> fig = plot_extent(xr_dataset)
    """
    # Verify the xr_dataset
    unox_data.verify_dataset(xr_dataset)
    # Find the min and max lat and lon values
    lat_min, lat_max, lon_min, lon_max = unox_data.get_extent(xr_dataset)
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

def plot_lats_lons(xr_dataset=xr.open_dataset('../datafiles/nox_2019_t106_US.nc'),
                   padding=0.1):
    """Plot the latitude and longitude values in the given dataset.

    Creates a map showing the longitude and latitude resolution of the 
    given dataset.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data for which to plot the longitude and latitude values.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    
    Examples
    --------
    >>> fig = plot_lats_lons(xr_dataset)
    """
    # Verify the xr_dataset
    unox_data.verify_dataset(xr_dataset)
    # Find the min and max lat and lon values
    this_extent = unox_data.get_extent(xr_dataset)
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

def plot_nox(datafile='../datafiles/nox_2019_t106_US.nc',
             datetime='2019-01-01T00:00:00',
             cbar_max=1.2e-10,
             padding=0.1):
    """Plots a map of NOx data.

    Creates a map of NOx data on a map using the provided data file.

    Parameters
    ----------
    datafile : str
        Path to the data file containing NOx data.
    datetime : str
        Date and time to select from the data file.
    cbar_max : float
        Maximum value for the colorbar.
    
    Returns
    -------
    """
    nox = xr.open_dataset(datafile)  #nox dataset used to make y files
    # Simplest way to plot the data
    # nox.nox[0].plot()
    # Verify the xr_dataset
    unox_data.verify_dataset(nox)
    # Find the min and max lat and lon values
    this_extent = unox_data.get_extent(nox)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_frmt.pad_extent(this_extent, padding)
    # A more complex way to plot the data
    # Select the time to plot
    nox_sel_time = nox.nox.sel(time=datetime)
    # Find the min and max lat and lon values
    lat_min, lat_max, lon_min, lon_max = unox_data.get_extent(nox_sel_time)
    # Create the figure
    fig = pplt.figure(refwidth=10)
    axs = fig.subplots(nrows=1, proj='cyl')
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 
    # Plot the data
    this_nox = axs.pcolorfast(nox_sel_time, vmin=0, vmax=cbar_max)
    # Format the map
    axs.format(
        lonlim=(p_lon_min, p_lon_max), latlim=(p_lat_min, p_lat_max),
        suptitle='NOx emissions on ' + datetime,
        latlines=10, lonlines=10, coast=True,
        labels=True, gridminor=True
    )
    # Add a colorbar
    fig.colorbar(this_nox, loc='b', label='NOx emissions (kg/m2/s)')
    # Return the figure
    return fig

def plot_comparison(truth_data={'stage':1, 'x_or_y':'y', 'year':2019},
                    pred_data={'stage':1, 'HPC_run':'test_unet_601760', 'year':2019},
                    hist_params={'bins':100, 'vmax':1000, 'vmin':10}
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
    # truth = np.load(unox.get_sample_data(stage=1, x_or_y='y', year=2019))  #truth (y input file)
    # stage1 = np.load(unox.get_pred_data(stage=1, HPC_run='test_unet_601760', year=2019))  #stage 1 prediction
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