import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import proplot as pplt

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