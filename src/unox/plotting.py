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

from unox import unox
from unox.HPC.data0.paths import verify_path
from unox import data as udata
from unox.HPC.data0.dataset import uarray, get_dataset
from unox.HPC.data0.verify_dataset import verify_dataset, verify_var
from unox.HPC.data0.verify_dtype import verify_number
from unox import plot_format as uplt_fmt
from unox.input import x_or_y_var, get_input_index
from unox.HPC.data0.load_input import get_npy_from_netcdf

# Set font sizes
mpl.rcParams['font.size'] = 16
mpl.rcParams['axes.labelsize'] = 16
mpl.rcParams['xtick.labelsize'] = 12
mpl.rcParams['ytick.labelsize'] = 12
mpl.rcParams['legend.fontsize'] = 12
title_font_size = 20

def plot_extent(
    xr_dataset='/datafiles/nox_2019_t106_US.nc',
    **kwargs,
):
    """Plots the extent of the given xarray dataset.

    Creates a map with the Robin projection of the entire world
    with a box showing the maximum extent of the dataset.

    Parameters
    ----------
    xr_dataset : str or xarray.Dataset or xarray.DataArray
        The xarray data for which to plot the extent or the file path to the dataset.
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `uarray()`.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.

    Examples
    --------
    >>> fig = plot_extent(xr_dataset)
    """
    # Make `uarray` object
    u_arr = uarray(xr_dataset, **kwargs)
    # Verify argument types 
    # The `verify_dataset()` function is automatically run when creating a `uarray` object

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
    xr_dataset='/datafiles/nox_2019_t106_US.nc',
    padding=0.1,
    **kwargs,
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
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `uarray()`.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    
    Examples
    --------
    >>> fig = plot_lats_lons(xr_dataset)
    """
    # Make `uarray` object
    u_arr = uarray(xr_dataset, **kwargs)
    # Verify argument types 
    # The `verify_dataset()` function is automatically run when creating a `uarray` object
    # The `verify_number()` function is automatically run in `pad_extent()`
    
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
    ax,
    xr_data_arr,
    plt_title=None,
    cmap=pplt.Colormap('Fire'),
    cbar_max=None,
    cbar_min=None,
    cb_ext='neither',
    padding=0.1,
    **kwargs,
):
    """Plots a map of the data in the given dataset.

    Creates a map of the 'var' data on a map using the provided netCDF file.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes on which to plot the data.
    xr_data_arr : xarray.DataArray
        The xarray data to plot. Must not have a time dimension.
    plt_title : str, optional
        The title for the plot. Default is `None`.
    cmap : matplotlib.colors.Colormap, optional
        The colormap to use for the plot. Default is pplt.cm.Fire.
    cbar_max : float, optional
        Maximum value for the colorbar. When `None`, the colorbar max is set to the max value to plot.
        Default is `None`.
    cbar_min : float, optional
        Minimum value for the colorbar. When `None`, the colorbar max is set to the min value to plot.
        Default is `None`.
    cb_ext : str, optional
        How to extend the ends of the colorbar. Can be 'neither', 'both', 'min', or 'max'.
        Default is 'neither'.
    padding : float
        The padding (in a fraction of total extent) to add to the extent of the map. 
        Default is 0.1.
    **kwargs : keyword arguments
        Additional keyword arguments accepted to facilitate wrapper functions.
    
    Returns
    -------
    this_map_ax : matplotlib.axes.Axes
        The axes object containing the plot.
    clrbar_label : str
        The label for the colorbar containing the variable name and units.
    
    Examples
    --------
    >>> import xarray as xr
    >>> this_dataset = xr.open_dataset('../datafiles/sample_data/nox_2019_t106_US.nc')
    >>> fig = plot_nc_map(xr_data_arr=this_dataset)
    """
    # Verify argument types
    if not isinstance(ax, pplt.axes.Axes):
        raise TypeError(f"(nc_map) `ax` must be a proplot Axes object. Got type: {type(ax)}")
    if not isinstance(xr_data_arr, xr.DataArray):
        raise TypeError(f"(nc_map) `xr_data_arr` must be an xarray DataArray. Got type: {type(xr_data_arr)}")
    if not isinstance(plt_title, (type(None), str)):
        raise TypeError(f"(nc_map) `plt_title` must be a string or None. Got type: {type(plt_title)}")
    if not isinstance(cmap, mpl.colors.Colormap):
        raise TypeError(f"(nc_map) `cmap` must be a matplotlib Colormap. Got type: {type(cmap)}")
    if not isinstance(cbar_max, type(None)):
        verify_number(cbar_max)
    if not isinstance(cbar_min, type(None)):
        verify_number(cbar_min)
    if cb_ext not in ['neither', 'both', 'min', 'max']:
        raise ValueError(f"(nc_map) `cb_ext` must be 'neither', 'both', 'min', or 'max'. Got: {cb_ext}")
    # `padding` is verified in `pad_extent()`

    # Verify the xr_data_arr. Assume there is no time dimension
    xr_data_arr = verify_dataset(xr_data_arr, check_time=False)
    # If there are any dimensions of size 1 (var, for example), squeeze them out
    xr_data_arr = xr_data_arr.squeeze(drop=True)
    # Check to ensure that `lat` and `lon` are the only remaining dimensions
    if not set(xr_data_arr.dims).issubset({'lat', 'lon'}):
        raise ValueError(f"(nc_map) `xr_data_arr` must have only 'lat' and 'lon' dimensions after squeezing. Got dimensions: {xr_data_arr.dims}")
    # Get the variable name from xr_data_arr
    var = xr_data_arr.name

    # Get the long name and units of the specified variable for plot labels
    try:
        var_name = xr_data_arr.long_name
        var_unit = xr_data_arr.units
    except:
        var_name = 'var'
        var_unit = 'units'

    # Find the min and max lat and lon values
    this_extent = udata.get_extent(xr_data_arr, check_time=False)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_fmt.pad_extent(this_extent, padding)

    # Get the maximum value for the colorbar
    if isinstance(cbar_max, type(None)):
        cbar_max = xr_data_arr.max()
        cbar_max = cbar_max.values
        cbar_max = np.unique(cbar_max)[0]
    # Get the minimum value for the colorbar
    if isinstance(cbar_min, type(None)):
        cbar_min = xr_data_arr.min()
        cbar_min = cbar_min.values
        cbar_min = np.unique(cbar_min)[0]
    # Plot the data, use `discrete=False` to set a continuous colorbar
    this_map_ax = ax.pcolormesh(xr_data_arr, vmin=cbar_min, vmax=cbar_max, discrete=False, extend=cb_ext)
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
    datetime='2019-01-02T00:00:00',
    avg_over=None,
    **kwargs,
):
    """Plots a maps of data in a netCDF.

    A wrapper for the `map_ax()` function.
    Creates maps for each specified 'var' using the provided netCDF file.

    Parameters
    ----------
    dataset : str, uarray, xarray.Dataset or xarray.DataArray
        Path to the netCDF data file.
    vars : str or list
        The name(s) of the variable(s) to plot from the netCDF file.
        Default is `nox`.
    datetime : str
        Date and time to select from the data file.
    avg_over : str, numpy.timedelta64, or None
        If provided, averages the data over the specified time period.
        If None, takes just the time slice specified in `datetime`.
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `nc_map()`.
    
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
    # Make `uarray` object
    u_arr = uarray(dataset, **kwargs)
    # Verify argument types 
    # The `verify_dataset()` function is automatically run when creating a `uarray` object
    if not isinstance(vars, list):
        if isinstance(vars, str):
            vars = [vars]
        else:
            raise TypeError(f"(plot_var_maps) `vars` must be a list of variable names or a single variable name string. Got type: {type(vars)}")
    if len(vars) == 0:
        raise ValueError("(plot_var_maps) `vars` list cannot be empty.")
    # `datetime` and `avg_over` are verified in `select_time()`
    
    # Select the time slice to plot
    u_arr.xr, title_segment = select_time(u_arr.xr, datetime, avg_over)

    # Create the figure
    fig = pplt.figure(refwidth=10)
    n_rows, n_cols = uplt_fmt.set_fig_row_col(len(vars))
    axs = fig.subplots(nrows=n_rows, ncols=n_cols, proj='cyl')
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 

    # Plot each of the variables
    for i in range(len(vars)):
        var = vars[i]
        # Verify that the variable is in the dataset
        verify_var(u_arr.xr, var)
        # Reduce the dataset to just the specified variable
        var_xr = u_arr.xr[var]
    
        # Add the plot to the axis
        this_var, clrbar_label = map_ax(
            axs[i], 
            var_xr,
            **kwargs,
        )
        # Add a colorbar
        axs[i].colorbar(this_var, loc='b', label=clrbar_label)
    # Add an overall title
    fig.suptitle(title_segment, fontsize=title_font_size)
    # Return the figure
    return fig

def plot_nc_map(
    xr_dataset='../datafiles/nox_2019_t106_US.nc',
    var='nox',
    datetime='2019-01-02T00:00:00',
    avg_over=None,
    **kwargs,
):
    """Plots a map of the 'var' data in a netCDF.

    Creates a map of the 'var' data on a map using the provided netCDF file.

    Parameters
    ----------
    xr_dataset : str or xarray.Dataset or xarray.DataArray
        Path to the netCDF data file.
    var : str
        The name of the variable to plot from the netCDF file.
        Default is `nox`.
    datetime : str
        Date and time to select from the data file.
    avg_over : str, numpy.timedelta64, or None
        If provided, averages the data over the specified time period.
        If None, takes just the time slice specified in `datetime`.
    cmap : matplotlib.colors.Colormap
        The colormap to use for the plot. Default is pplt.cm.Fire.
    cbar_max : float
        Maximum value for the colorbar. When `None`, the colorbar max is set to the max value to plot.
        Default is `None`.
    padding : float
        The padding (in a fraction of total extent) to add to the extent of the map. 
        Default is 0.1 degrees.
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `nc_map()`.
    
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
        xr_dataset = verify_path(xr_dataset)
        # Now open the dataset
        xr_dataset = xr.open_dataset(xr_dataset)
    # Verify the xr_dataset
    # Squeeze to remove `var` dimension, if present
    xr_dataset = verify_dataset(xr_dataset).squeeze(drop=True)
    # Select the time slice to plot
    var_sel_time, overall_title = select_time(
        xr_dataset,
        var,
        datetime,
        avg_over,
    )

    # Create the figure
    fig = pplt.figure(refwidth=10)
    axs = fig.subplots(nrows=1, proj='cyl')
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 
    
    # Add the plot to the axis
    this_var, clrbar_label = nc_map(
        axs, 
        var_sel_time, 
        datetime,
        avg_over,
        plt_title=overall_title,
        **kwargs,
    )
    # Add a colorbar
    fig.colorbar(this_var, loc='b', label=clrbar_label)
    # Return the figure
    return fig

def select_time(
    xr_dataset,
    var,
    datetime,
    avg_over=None,
):
    """Selects the time from an xarray to plot.

    Either selects a single time slice or averages over a time period to result in 
    an xarray for the specified variable without a time dimension, only lat-lon dimensions.

    Parameters
    ----------
    xr_dataset : xarray.Dataset or xarray.DataArray
        The xarray data to plot. Must have a time dimension.
    var : str
        The name of the variable to plot from the netCDF file.
    datetime : str
        Date and time to select from the data file.
    avg_over : str, numpy.timedelta64, or None
        If provided, averages the data over the specified time period.
        If None, takes just the time slice specified in `datetime`.
    title_fmt : str
        The format of the title. Can be 'date' or 'varname'.

    Returns
    -------
    var_sel_time : xarray.Dataset or xarray.DataArray
        An xarray DataArray of the selected variable without a time dimension.
    overall_title : str
        The title string for the plot.
    """
    # Verify argument types
    xr_dataset = verify_dataset(xr_dataset, check_time=True)
    if isinstance(var, type(None)):
        # Keep all the variables and return an xarray Dataset
        this_xarray = xr_dataset
    else:
        # Verify that the variable is in the dataset, if specified
        udata.verify_var(xr_dataset, var)
        # Save the attributes for the specified variable
        # var_name = xr_dataset[var].long_name
        # var_unit = xr_dataset[var].units
        # Reduce the dataset to just the specified variable
        this_xarray = xr_dataset[var]

    # Select the time to plot
    if isinstance(avg_over, type(None)):
        # Take just that time slice
        # Use squeeze to drop `time` dimension as sel() only automatically drops scalar
        # dimensions, which `time` is not
        var_sel_time = this_xarray.sel(time=datetime, drop=False).squeeze(drop=True)
        # Format a string for the title
        overall_title = datetime.split('T')[0]
    else:
        # Add the increment over which to average to the datetime
        try:
            end_date = udata.add_amount_to_date(datetime, avg_over)
        except:
            raise ValueError(f"(select_time) Invalid `avg_over` value: {avg_over}")
        # Average over the specified amount of time
        # Maintain attributes by using `drop=False` in sel() and `keep_attrs=True` in mean()
        var_sel_time = this_xarray.sel(time=slice(datetime, end_date), drop=False)
        var_sel_time = var_sel_time.mean(dim='time', keep_attrs=True)
        # Get the value and unit of the averaging
        avg_over_num, avg_over_unit = udata.get_increment_info(avg_over)
        # Format a string for the title
        overall_title = f"Averaged over {avg_over_num} {avg_over_unit} from {datetime.split('T')[0]}"
    # if not isinstance(var, type(None)):
    #     # Add the saved attributes to the xarray DataArray
    #     var_sel_time.attrs['long_name'] = var_name
    #     var_sel_time.attrs['units'] = var_unit
    return var_sel_time, overall_title

def nc_map(
    ax,
    xr_data_arr,
    datetime,
    avg_over=None,
    plt_title=None,
    cmap=pplt.Colormap('Fire'),
    cbar_max=None,
    cbar_min=None,
    cb_ext='neither',
    padding=0.1,
):
    """Plots a map of the 'var' data in a netCDF.

    Creates a map of the 'var' data on a map using the provided netCDF file.

    Parameters
    ----------
    xr_dataset : xarray.DataArray
        The xarray data to plot. Must not have a time dimension.
    var : str
        The name of the variable to plot from the netCDF file.
        Default is `nox`.
    datetime : str
        Date and time to select from the data file.
    avg_over : str, numpy.timedelta64, or None
        If provided, averages the data over the specified time period.
        If None, takes just the time slice specified in `datetime`.
    cmap : matplotlib.colors.Colormap
        The colormap to use for the plot. Default is pplt.cm.Fire.
    cbar_max : float
        Maximum value for the colorbar. When `None`, the colorbar max is set to the max value to plot.
        Default is `None`.
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
    >>> fig = plot_nc_map(xr_data_arr=this_dataset)
    """
    # Verify argument types
    if not isinstance(xr_data_arr, xr.DataArray):
        raise TypeError(f"(nc_map) `xr_data_arr` must be an xarray DataArray. Got type: {type(xr_data_arr)}")
    # Verify the xr_data_arr. Assume there is no time dimension
    xr_data_arr = verify_dataset(xr_data_arr, check_time=False)
    # If there are any dimensions of size 1 (var, for example), squeeze them out
    xr_data_arr = xr_data_arr.squeeze(drop=True)
    # Check to ensure that `lat` and `lon` are the only remaining dimensions
    if not set(xr_data_arr.dims).issubset({'lat', 'lon'}):
        raise ValueError(f"(nc_map) `xr_data_arr` must have only 'lat' and 'lon' dimensions after squeezing. Got dimensions: {xr_data_arr.dims}")
    # Get the variable name from xr_data_arr
    var = xr_data_arr.name

    # Get the long name and units of the specified variable for plot labels
    try:
        var_name = xr_data_arr.long_name
        var_unit = xr_data_arr.units
    except:
        var_name = 'var'
        var_unit = 'units'

    # Find the min and max lat and lon values
    this_extent = udata.get_extent(xr_data_arr, check_time=False)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_fmt.pad_extent(this_extent, padding)

    # Check the plot title
    if isinstance(plt_title, type(None)):
        plt_title = var_name

    # Get the maximum value for the colorbar
    if isinstance(cbar_max, type(None)):
        cbar_max = xr_data_arr.max()
        cbar_max = cbar_max.values
        cbar_max = np.unique(cbar_max)[0]
    # Get the minimum value for the colorbar
    if isinstance(cbar_min, type(None)):
        cbar_min = xr_data_arr.min()
        cbar_min = cbar_min.values
        cbar_min = np.unique(cbar_min)[0]
    # Plot the data, use `discrete=False` to set a continuous colorbar
    this_var = ax.pcolormesh(xr_data_arr, vmin=cbar_min, vmax=cbar_max, discrete=False, extend=cb_ext)
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
    return this_var, clrbar_label

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
    padding=0.1,
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
    padding : float
        The padding (in a fraction of total extent) to add to the extent of the map. 
        Default is 0.1 degrees.

    Returns
    -------
    this_ax : matplotlib.axes.Axes
        The axes with the plotted data.

    Examples
    --------
    >>> fig, ax = pplt.subplots()
    >>> plot_npy_map(ax, npy_arr, lats, lons, title='NOx emissions')
    """
    # Squeeze the numpy array
    npy_arr = np.squeeze(npy_arr)
    # Verify the dimensions of the numpy array
    if npy_arr.shape != (len(lats), len(lons)):
        raise ValueError(f"(plot_npy_map) `npy_arr` must have shape (len(lats), len(lons)). Expected: ({len(lats)}, {len(lons)}). Got: {npy_arr.shape}")
    # Verify c_halfrange is a number

    # Plot the data
    if isinstance(c_halfrange, type(None)):
        pcm = this_ax.pcolormesh(lons, lats, npy_arr, cmap=cmap, shading='auto', levels=100)
    elif udata.verify_number(c_halfrange):
        pcm = this_ax.pcolormesh(lons, lats, npy_arr, cmap=cmap, shading='auto', levels=100, vmin=-1*c_halfrange, vmax=c_halfrange, extend=cb_extend)  
    else:
        raise TypeError(f"(plot_npy_map) `c_halfrange` must be a number. Got type: {type(c_halfrange)}. `c_halfrange` value: {c_halfrange}")
    # Get the minimum and maximum latitude and longitude values
    this_extent = udata.get_extent(lats=lats, lons=lons)
    # Enlarge the extent of the map by the given padding value
    p_lat_min, p_lat_max, p_lon_min, p_lon_max = uplt_fmt.pad_extent(this_extent, padding)
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
        n_rows = 1
    else:
        # Get the stage 2 values
        stage2 = np.load(unox.get_pred_data(stage=2, **pred_params))
        # Make a list of the data
        data_list = [truth, stage1, stage2]
        # Set the number of rows in the figure
        n_rows = 2
        
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
    ax = fig.subplots(nrows=n_rows, ncols=3, proj='cyl')
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
            # in_arrs = {'truth': data_list[0], 'stage1': data_list[1], 'stage2': data_list[2]},
            in_arrs = {'truth': data_list[0], 'stage1': stage1, 'stage2': stage2},
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
    fig.suptitle(f"HPC run: {pred_params['HPC_run']}, input set: {truth_params['input_set']} - {overall_title}", fontsize=title_font_size)
    return fig

def get_input_set(
    HPC_run = 'no2_example_run',
):
    """Get the name of the input set used for the given HPC run.

    Parameters
    ----------
    HPC_run : str
        The name of the HPC_run for which to get the input set.
    
    Returns
    -------
    input_set : str
        The name of the input set used for the given HPC run.
    """
    # Verify argument types
    if not isinstance(HPC_run, str):
        raise TypeError(f"(plot_comp_maps) `HPC_run` must be a string. Got type: {type(HPC_run)}")

    # Assemble filepath to the HPC_run configuration dictionary
    config_path = f"HPC_runs/{HPC_run}/input_config.json"
    # Verify the config filepath
    config_path = verify_path(config_path)
    # Load config file to a dictionary
    with open(f"{config_path}", 'r') as file:
        config_dict = json.load(file)
    # Get the name of the input set used to make the predictions
    input_set = config_dict['input_set']
    return input_set

def plot_comp_maps(
    HPC_run = 'no2_example_run',
    year = 2019,
    datetime='2019-01-02T00:00:00',
    avg_over=None,
    restrict_lat_lon_to=None,
    add_corr_plots=False,
    clr_bar_scale=0.5,
    clr_map=pplt.Colormap('seismic'),
    stage1_only=False,
    **kwargs,
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
    HPC_run : str
        The name of the HPC_run for which to make comparison maps.
    year : int
        The year for which to make comparisons.
    this_date : np.datetime64 or str
        Date and time to select from the data file.
        Expected format is 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DD'.
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
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `corr_plot()`.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plots.
    """
    # Verify argument types
    if not isinstance(HPC_run, str):
        raise TypeError(f"(plot_comp_maps) `HPC_run` must be a string. Got type: {type(HPC_run)}")
    if not isinstance(year, int):
        raise TypeError(f"(plot_comp_maps) `year` must be an integer. Got type: {type(year)}")
    
    # Assemble filepath to the HPC_run predictions netcdf
    pred_nc_path = f"HPC_runs/{HPC_run}/predictions.nc"
    # Get and verify predictions data
    pred_xarray = uarray(pred_nc_path).xr
    # Get the input set used in the HPC run
    input_set = get_input_set(HPC_run)
    # Get and verify input set
    input_xarray = uarray(input_set, is_input_set=True).xr

    # Get the `y_var` name from the input dataset
    y_var = input_xarray.attrs['y_var']
    # Make a list for the variables to plot
    vars_to_plot = [y_var]
    # Verify that the prediction array has the correct variable
    pred_var = f"{y_var}_pred"
    udata.verify_var(pred_xarray, pred_var)
    vars_to_plot.append(pred_var)
    # Decide on the number of rows and columns in the figure
    if stage1_only == False:
        pred_var_s2 = f"{y_var}_pred_s2"
        udata.verify_var(pred_xarray, pred_var_s2)
        vars_to_plot.append(pred_var_s2)
        # Set the number of rows and columns in the figure
        if add_corr_plots:
            n_rows = 3
            n_rows_maps = 2
        else:
            n_rows = 2
            n_rows_maps = 2
        n_cols = 3
    else:
        # Set the number of rows and columns in the figure
        if add_corr_plots:
            n_rows = 2
            n_rows_maps = 1
        else:
            n_rows = 1
            n_rows_maps = 1
        n_cols = 3
    
    # Trim the latitude and longitude extents to match
    pred_xarray, input_xarray = udata.match_domains(pred_xarray, input_xarray)
    # Add the "truth" data to the prediction array
    pred_xarray[y_var] = input_xarray[y_var]
    # Select the time slice to plot
    pred_xarray, time_title = select_time(
        pred_xarray,
        var=None,
        datetime=datetime,
        avg_over=avg_over,
    )

    # Get the units of the y_var
    y_var_unit = input_xarray[y_var].units
    # Calculate the difference between the "truth" and the predictions
    pred_xarray['y_m_st1'] = pred_xarray[y_var] - pred_xarray[pred_var]
    pred_xarray['y_m_st1'].attrs = {'long_name': f"'Truth' - Stage 1 prediction", 'units': y_var_unit}
    vars_to_plot.append('y_m_st1')
    if stage1_only == False:
        pred_xarray['y_m_st2'] = pred_xarray[y_var] - pred_xarray[pred_var_s2]
        pred_xarray['y_m_st2'].attrs = {'long_name': f"'Truth' - Stage 2 prediction", 'units': y_var_unit}
        vars_to_plot.append('y_m_st2')
        pred_xarray['st1_m_st2'] = pred_xarray[pred_var] - pred_xarray[pred_var_s2]
        pred_xarray['st1_m_st2'].attrs = {'long_name': f"Stage 1 - Stage 2", 'units': y_var_unit}
        vars_to_plot.append('st1_m_st2')

    # Create tuple of the projections for each subplot
    if add_corr_plots == False:
        # Only one projection required
        these_projs = 'cyl'
    else:
        # Create a list of projections for each subplot
        these_projs = []
        for i in range(n_rows_maps*n_cols):
            these_projs.append('cyl')
        for i in range((n_rows - n_rows_maps)*n_cols):
            these_projs.append(None)
    # Create the figure
    ## Setting `share=False` to allow separate axis labels for each subplot
    fig, axs = pplt.subplots(refwidth=4, nrows=n_rows, ncols=n_cols, proj=these_projs, share=False)
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 

    # Get the maximum and minimum values for each variable
    vmin_arr = pred_xarray.min(skipna=True)
    vmax_arr = pred_xarray.max(skipna=True)
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
    these_vars = [None]*(n_rows_maps*n_cols)
    these_cblbls = [None]*(n_rows_maps*n_cols)
    # Add the plots to the axes
    for i in range(len(vars_to_plot)):
        data_arr = pred_xarray[vars_to_plot[i]]
        these_vars[i], these_cblbls[i] = nc_map(
            axs[i], 
            data_arr, 
            datetime,
            avg_over,
            cmap=clr_map,
            cbar_max=chr,
            cbar_min=-chr,
            cb_ext=cbe,
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
        # Create arrays to hold the plots and titles
        fig_q_list = [None]*3
        title_list = [None]*3
        # Set histogram parameters
        hist_params={'bins':100, 'vmax':10000, 'vmin':10}
        # Add the three correlation plots to the figure
        fig_q_list[0], title_list[0] = corr_plot(
            HPC_run=HPC_run,
            year=year,
            x_ax='pred',
            y_ax='truth',
            ax=axs[-3],
            hist_params=hist_params,
            **kwargs,
        )
        if stage1_only == False:
            fig_q_list[1], title_list[1] = corr_plot(
                HPC_run=HPC_run,
                year=year,
                x_ax='pred_s2',
                y_ax='truth',
                ax=axs[-2],
                hist_params=hist_params,
                **kwargs,
            )
            fig_q_list[2], title_list[2] = corr_plot(
                HPC_run=HPC_run,
                year=year,
                x_ax='pred',
                y_ax='pred_s2',
                ax=axs[-1],
                hist_params=hist_params,
                **kwargs,
            )
        # Add the colorbar
        fig.colorbar(fig_q_list[0], loc='r', label='Count per pixel', extend='both', formatter='sci', rows=(n_rows_maps+1, n_rows))

    # Set the figure title
    fig.suptitle(f"HPC run: {HPC_run}, input set: {input_set}, {time_title}", fontsize=title_font_size)
    return fig

def make_colorbar(
    fig,
    cb_ax,
    cb_label,
    num_ticks=9,
    cb_loc='l',
    cb_extend='neither',
    **kwargs,
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
    **kwargs : keyword arguments
        Additional keyword arguments to pass to `colorbar()`.

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
    cbar = fig.colorbar(cb_ax, loc=cb_loc, label=cb_label, extend=cb_extend, **kwargs)
    # Set ticks for the colorbar (use an odd number of ticks to have a zero tick in the middle)
    cbar.locator = mpl.ticker.LinearLocator(numticks = num_ticks)
    cbar.update_ticks()
    return cbar

def plot_comparison(
    npy_a, 
    npy_b,
    label_x='Array A',
    label_y='Array B',
    ax=None,
    plt_title='',
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
    label_x : str
        The label for the first array in the plot.
    label_y : str
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
        # Create the figure
        fig = pplt.figure(refwidth=4)
        ax = fig.subplots(nrows=1, ncols=1)
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
        xlabel=label_x,
        ylabel=label_y,
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
    HPC_run = 'no2_example_run',
    year = 2019,
    x_ax = 'pred',
    y_ax = 'truth',
    restrict_lat_lon_to = None,
    ax = None,
    **kwargs,
):
    """
    Plot the prediction vs truth values.

    Creates a correlation plot between the prediction values of the given HPC run

    Parameters
    ----------
    HPC_run : str
        The name of the HPC_run for which to make a correlation plot.
    year : int
        The year for which to make comparisons.
    x_ax : str
        What to plot on the x-axis. Must be one of ['truth', 'pred', 'pred_s2'].
    y_ax : str
        What to plot on the y-axis. Must be one of ['truth', 'pred', 'pred_s2'].
    restrict_lat_lon_to : str
        Path to a netCDF file to restrict the latitude and longitude range.
        If None, the entire dataset is used.
    ax : matplotlib.axes.Axes or None
        The axes on which to plot the data. If None, a new figure and axes are created.
    **kwargs : dict
        Additional keyword arguments to pass to the `plot_comparison` function.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.

    Examples
    --------
    >>> fig = corr_plot('no2_example_run', 2019, x_ax='pred', y_ax='truth')
    """
    # Verify argument types
    if not isinstance(HPC_run, str):
        raise TypeError(f"(corr_plot) `HPC_run` must be a string. Got type: {type(HPC_run)}")
    if not isinstance(year, int):
        raise TypeError(f"(corr_plot) `year` must be an integer. Got type: {type(year)}")
    if not x_ax in ['truth', 'pred', 'pred_s2']:
        raise ValueError(f"(corr_plot) `x_ax` must be one of ['truth', 'pred', 'pred_s2']. Got: {x_ax}")
    if not y_ax in ['truth', 'pred', 'pred_s2']:
        raise ValueError(f"(corr_plot) `y_ax` must be one of ['truth', 'pred', 'pred_s2']. Got: {y_ax}")
    
    # Create a new figure and axis if none is provided
    if isinstance(ax, type(None)):
        new_fig = True
    else:
        new_fig = False
    
    # Assemble filepath to the HPC_run predictions netcdf
    pred_nc_path = f"HPC_runs/{HPC_run}/predictions.nc"
    # Get and verify predictions data
    pred_xarray = uarray(pred_nc_path).xr
    # Get the input set used in the HPC run
    input_set = get_input_set(HPC_run)
    # Get and verify input set
    input_xarray = uarray(input_set, is_input_set=True).xr

    # Get the `y_var` name from the input dataset
    y_var = input_xarray.attrs['y_var']
    # For the x and y axes, get the specified data
    plot_data = []
    plot_labels = []
    for this_ax in [x_ax, y_ax]:
        if this_ax == 'truth':
            ax_var = y_var
            # If not done already, add the "truth" data to the prediction xarray
            try:
                udata.verify_var(pred_xarray, ax_var)
            except:
                # Trim the latitude and longitude extents to match
                pred_xarray, input_xarray = udata.match_domains(pred_xarray, input_xarray)
                # Add the "truth" data to the prediction array
                pred_xarray[ax_var] = input_xarray[ax_var]
            # Assemble the axis label
            var_units = pred_xarray[ax_var].attrs['units']
            plot_labels.append(f"'Truth' ({var_units})")
        elif this_ax in ['pred', 'pred_s2']:
            ax_var = f"{y_var}_{this_ax}"
            # Assemble the axis label
            if '2' in this_ax:
                label_mod = r"$_{s2}$"
            else:
                label_mod = ""
            var_units = pred_xarray[ax_var].attrs['units']
            plot_labels.append(f"Predictions{label_mod} ({var_units})")
        else:
            raise ValueError(f"(corr_plot) `this_ax` must be one of ['truth', 'pred', 'pred_s2']. Got: {this_ax}")
        # Verify that the prediction array has the correct variable
        udata.verify_var(pred_xarray, ax_var)
        # Add the data to plot to the list
        plot_data.append(pred_xarray[ax_var].sel(time=str(year)).values)

    # Get the long name and units of the specified variable for plot labels
    try:
        var_name = input_xarray[y_var].attrs['long_name']
    except:
        var_name = 'var'
    # Assemble the plot title
    plt_title = f"HPC run: {HPC_run}, input set: {input_set}, {var_name}"

    # Plot the comparison
    fig_q = plot_comparison(
        plot_data[0],
        plot_data[1],
        label_x=plot_labels[0],
        label_y=plot_labels[1],
        ax = ax,
        plt_title = plt_title,
        **kwargs,
    )
    return fig_q, plt_title

def all_corr_plots(
    HPC_run = 'no2_example_run',
    year = 2019,
    hist_params={'bins':100, 'vmax':10000, 'vmin':10},
    **kwargs,
):
    """Plot all combinations of correlation plots for the given HPC run.

    Parameters
    ----------
    HPC_run : str
        The name of the HPC_run for which to make a correlation plot.
    year : int
        The year for which to make comparisons.
    hist_params : dict
        Dictionary containing the parameters for the histogram.
        Must contain 'bins', 'vmax', and 'vmin'.
        Defined here instead of in **kwargs to insure consistency between plots.
    **kwargs : dict
        Additional keyword arguments to pass to the `corr_plot` function.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.

    Examples
    --------
    >>> fig = all_corr_plots('no2_example_run', 2019)
    """
    # Verify argument types
    if not isinstance(HPC_run, str):
        raise TypeError(f"(corr_plot) `HPC_run` must be a string. Got type: {type(HPC_run)}")
    if not isinstance(year, int):
        raise TypeError(f"(corr_plot) `year` must be an integer. Got type: {type(year)}")
    
    # Create the figure
    ## Setting `share=False` to allow separate axis labels for each subplot
    fig, axs = pplt.subplots(refwidth=4, nrows=1, ncols=3, share=False)

    # Create arrays to hold the plots and titles
    fig_q_list = [None]*3
    title_list = [None]*3
    # Add the three correlation plots to the figure
    fig_q_list[0], title_list[0] = corr_plot(
        HPC_run=HPC_run,
        year=year,
        x_ax='pred',
        y_ax='truth',
        ax=axs[0],
        hist_params=hist_params,
        **kwargs,
    )
    fig_q_list[1], title_list[1] = corr_plot(
        HPC_run=HPC_run,
        year=year,
        x_ax='pred_s2',
        y_ax='truth',
        ax=axs[1],
        hist_params=hist_params,
        **kwargs,
    )
    fig_q_list[2], title_list[2] = corr_plot(
        HPC_run=HPC_run,
        year=year,
        x_ax='pred',
        y_ax='pred_s2',
        ax=axs[2],
        hist_params=hist_params,
        **kwargs,
    )
    # Check whether all the titles are the same
    if len(set(title_list)) != 1:
        warnings.warn(f"(all_corr_plots) The titles of the correlation plots are not the same: {title_list}. Using the first title for the figure title.")
    # Set the figure super title
    fig.suptitle(title_list[0], fontsize=title_font_size)
    # Add the colorbar
    fig.colorbar(fig_q_list[0], loc='r', label='Count per pixel', formatter='sci')

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
    # Flatten the data to just one axis
    truths = truth.flatten()
    preds = stage1.flatten()
    # Plot the comparison
    fig = plot_comparison(
        truths, 
        preds, 
        label_x=f"'Truth' ({var_units})",
        label_y=f"Stage 1 ({var_units})",      
        hist_params=hist_params
    )
    # Set the figure title
    fig.suptitle(f"HPC run: {pred_data['HPC_run']}, input set: {truth_data['input_set']} - {var_label}", fontsize=title_font_size)           
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
        raise ValueError(f"(plot_npy_diff) The shapes of the numpy arrays do not match. Got: {npy_a.shape} and {npy_b.shape}")
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
                        label_x='npy_a (where they differ)',
                        label_y='npy_b (where they differ)',
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

def compare_input_vars(
    input_a_dict = {
        'input_set':'no2_sample_input',
        'year':2019,
        'var':'u10',
        'fmt':'nc',
    },
    input_b_dict = {
        'input_set':'no2_sample_input',
        'year':2019,
        'var':'u10',
        'fmt':'nc',
    },
    abs_tolerance=2e-5,
):
    """
    Compares the data for two input variables.

    Parameters
    ----------
    input_dict_a : dict
        Dictionary containing the parameters for the first input variable.
        Must contain 'input_set', 'year', and 'var'. A value for 'fmt' is optional,
        but must be either 'nc' or 'npy'. Default is 'nc'.
    input_dict_b : dict
        Dictionary containing the parameters for the second input variable.
        Must contain 'input_set', 'year', and 'var'.
    abs_tolerance : float
        The absolute tolerance for comparing the input files. Default is 2e-5.
    """
    # Verify argument types
    if True:
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
            if 'fmt' in input_dict:
                if input_dict['fmt'] not in ['nc', 'npy']:
                    raise ValueError(f"(compare_input_vars) `fmt` must be either 'nc' or 'npy'. Got type: {input_dict['fmt']}")
        if not isinstance(abs_tolerance, float):
            raise TypeError(f"(compare_input_vars) `abs_tolerance` must be a float. Got type: {type(abs_tolerance)}")
    # Loop over the two input dictionaries and load the data
    for input_dict in [input_a_dict, input_b_dict]:
        # Get the requested format, if none was given, select 'nc'
        fmt = input_dict.get('fmt', 'nc')
        if fmt == 'npy':
            # Check for stage 2 variables
            if input_dict['var'] == 'no2_s2':
                this_stage=2
                input_dict['var'] = 'no2'
            elif input_dict['var'] == 'no2_s2_tm1':
                this_stage=2
                input_dict['var'] = 'no2_tm1'
            else:
                this_stage=1
            # Load the input data from npy file
            this_input, var_index = unox.get_one_input_var_array(
                input_dict['var'],
                stage=this_stage, 
                year=input_dict['year'],
                input_set=input_dict['input_set'],
            )
            # Reset the variable name if it was changed
            if this_stage == 2:
                if input_dict['var'] == 'no2':
                    input_dict['var'] = 'no2_s2'
                elif input_dict['var'] == 'no2_tm1':
                    input_dict['var'] = 'no2_s2_tm1'
        elif fmt == 'nc':
            # Load the input data from netCDF
            xr_dataset = udata.get_dataset(
                input_dict['input_set'],
                is_input_set=True,
            )
            from unox.HPC.utils.load_input import get_npy_from_netcdf
            this_input = get_npy_from_netcdf(
                xr_dataset,
                year=input_dict['year'],
                var=input_dict['var'],
            )
            # If nox, remove extra dimension
            if input_dict['var'] == 'nox':
                this_input = this_input.squeeze()
        input_dict['data_array'] = this_input
        print(f"Shape of {input_dict['var']} from {input_dict['input_set']}: {this_input.shape}")
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
        overall_title = f"{input_a_dict['input_set']}-{input_a_dict['year']}-{input_a_dict['var']} vs {input_b_dict['input_set']}-{input_b_dict['year']}-{input_b_dict['var']}"
        return plot_npy_diff(input_a_dict['data_array'], input_b_dict['data_array'], title=overall_title)
    
def set_of_runs(
    set_name,
    year,
    stage=1,
    this_date='2019-01-02',
    avg_over=None,
    restrict_lat_lon_to=None,
    clr_bar_scale=0.5,
    maps_or_comps='maps',
):
    """Creates a figure to summarize a set of runs.

    Creates a set of 12 plots:
    1. Plot of the "Truth"
    2. Summary of the set of runs
    3-12. Plots of each run compared with the "Truth"

    Parameters
    ----------
    set_name : str
        The directory name within `HPC_runs/` containing the set of runs.
    year : int
        The year of the data to plot.
    stage : int
        The stage of the data to plot (1 or 2).
    this_date : np.datetime64 or str
        Date and time to select from the data file.
        Expected format is 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DD'.
    avg_over : str, numpy.timedelta64, or None
        If provided, averages the data over the specified time period.
        If None, takes just the time slice specified in `datetime`.
    restrict_lat_lon_to : str
        Path to a netCDF file to restrict the latitude and longitude range.
        If None, the entire dataset is used.
    clr_bar_scale : float between 0 and 1
        Scale factor for the color bar. If set to 1, the color bar will be scaled 
        to the maximum absolute value of the data. Default is 0.5.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plots.
    """
    # Verify argument types
    if True:
        if not isinstance(set_name, str):
            raise TypeError(f"(set_of_maps) `set_name` must be a string. Got type: {type(set_name)}")
        if not udata.verify_number(year):
            raise TypeError(f"(set_of_maps) `year` must be an integer. Got type: {type(year)}")
        if stage not in [1, 2]:
            raise ValueError(f"(set_of_maps) `stage` must be either 1 or 2. Got: {stage}")
        if not (isinstance(this_date, str) or isinstance(this_date, np.datetime64)):
            raise TypeError(f"(set_of_maps) `this_date` must be a string or np.datetime64. Got type: {type(this_date)}")
        if not (isinstance(avg_over, type(None)) or isinstance(avg_over, str) or udata.verify_timedelta64(avg_over)):
            raise TypeError(f"(set_of_maps) `avg_over` must be None, a string, or a numpy.timedelta64. Got type: {type(avg_over)}")
        if not (isinstance(restrict_lat_lon_to, type(None)) or isinstance(restrict_lat_lon_to, str)):
            raise TypeError(f"(set_of_maps) `restrict_lat_lon_to` must be None or a string. Got type: {type(restrict_lat_lon_to)}")
        if not udata.verify_number(clr_bar_scale):
            raise TypeError(f"(set_of_maps) `clr_bar_scale` must be a number. Got type: {type(clr_bar_scale)}")
        if maps_or_comps not in ['maps', 'comps']:
            raise ValueError(f"(set_of_maps) `maps_or_comps` must be either 'maps' or 'comps'. Got {maps_or_comps}.")
    # Verify the set of runs exists
    set_path = verify_path(f"HPC_runs/{set_name}")
    # Get a list of the runs in the set (the subdirectories of the set directory)
    runs_in_set = os.listdir(set_path)
    # Replace the year in `this_date` with the specified year
    yr, mn, day = udata.get_YMD_from_date(this_date)
    start_date = f"{year:04d}-{mn:02d}-{day:02d}"
    start_doy = udata.get_DOY(start_date)
    # Calculate the end date, if applicable
    if isinstance(avg_over, type(None)):
        # Format overall title
        overall_title = f"stage {stage} comparisons on {start_date}"
    else:
        end_date = udata.add_amount_to_date(start_date, avg_over)
        # If the year incremented, set to December 31st in specified year
        yr, mn, day = udata.get_YMD_from_date(end_date)
        if yr > year:
            end_date = f"{year:04d}-12-31"
        end_doy = udata.get_DOY(end_date)
        # Format overall title
        overall_title = f"stage {stage} comparisons from {start_date}-{end_date}"

    # Calculate the number of rows in the figure
    n_cols = 3
    n_rows = len(runs_in_set)//n_cols + (1 if len(runs_in_set)%n_cols > 0 else 0)
    # Create the figure
    fig = pplt.figure(refwidth=4)
    ax = fig.subplots(nrows=n_rows, ncols=n_cols, proj='cyl')
    # Select medium resolution for features such as coastlines
    pplt.rc.reso = 'med' 

    # Create dictionary with the runs_in_set as keys
    run_metadicts = {run: {} for run in runs_in_set}
    # Create blank lists to be filled
    input_sets = []
    config_files = []
    pred_arrs0 = []
    # Loop across each run
    for run in runs_in_set:
        # Load the output metadata dictionary
        with open(f"{set_path}/{run}/output_metadata.json", 'r') as file:
            run_metadicts[run] = json.load(file)
        # Verify year is in the appropriate stage predictions
        these_pred_years = run_metadicts[run]['pred_years'][f"stage{stage}"]
        if not year in these_pred_years:
            raise ValueError(f"(set_of_maps) Year {year} not found in stage {stage} predictions for run '{run}'. Available years: {these_pred_years}.")
        # Add the input set to the list
        input_sets.append(run_metadicts[run]['config_dict']['input_set'])
        # Add config file to the list
        config_files.append(run_metadicts[run]['config_file'])
        # Load the prediction values for this run
        run_metadicts[run]['pred_arr'] = np.load(unox.get_pred_data(
            stage=stage, 
            HPC_run=f"{set_name}/{run}",
            year=year,
        ))
        # Add prediction array to the list
        pred_arrs0.append(run_metadicts[run]['pred_arr'])
    # Check whether there is a unique input set
    unique_input_sets = list(set(input_sets))
    if len(unique_input_sets) != 1:
        raise ValueError(f"(set_of_maps) input sets found in the set of runs contain multiple values: {unique_input_sets}. All runs must use the same input set.")
    else:
        this_input_set = unique_input_sets[0]
    # Check whether there is a unique config file
    unique_config_files = list(set(config_files))
    if len(unique_config_files) != 1:
        print(f"Warning: multiple values found for config files across runs: {unique_config_files}")
        print(f"Using the first entry as config file: {unique_config_files[0]}")
    if unique_config_files[0] == 'input_config':
        this_config = f"{set_path}/{runs_in_set[0]}/input_config.json"
    else:
        this_config = unique_config_files[0]
    # Open the input netCDF file
    input_dataset = udata.get_dataset(this_input_set, is_input_set=True)
    # Get the y variable
    y_var = input_dataset.attrs['y_var']
    # Load the "truth" array
    truth = get_npy_from_netcdf(
        input_dataset,
        year,
        this_config,
        var=y_var,
    )
    # Get the latitude and longitude values
    lats, lons = udata.get_lats_lons(input_dataset)

    # Restrict the latitude and longitude range
    if not isinstance(restrict_lat_lon_to, type(None)):
        # Create a list of all map data arrays
        data_list = pred_arrs0 + [truth]
        # Restrict the domain of all the arrays in the list
        data_list, lats, lons = udata.restrict_domain(data_list, lats, lons, xr.open_dataset(restrict_lat_lon_to))
        # Put the restricted arrays back into the original variables
        pred_arrs0 = data_list[:-1]
        truth = data_list[-1]
        
    # Average over a time period, if specified
    if isinstance(avg_over, type(None)):
        plt_truth = truth[start_doy, :, :]
    else:
        plt_truth = np.average(truth[start_doy:end_doy, :, :], axis=0)
    # Plot the "truth"
    plot_npy_map(
        fig,
        ax[0],
        plt_truth,
        lats,
        lons,
        cmap=pplt.Colormap('Fire'),
        ax_title="truth",
    )
    if maps_or_comps == 'comps' and isinstance(avg_over, type(None)):
        plt_truth = truth

    # Create blank list to be filled
    pred_arrs = []
    # Loop across each run
    for i in range(len(runs_in_set)):
        run = runs_in_set[i]
        # Select the time to plot
        if isinstance(avg_over, type(None)):
            if maps_or_comps == 'maps':
                # Save the difference on just the specified day
                plt_this = plt_truth - pred_arrs0[i][start_doy, :, :]
            elif maps_or_comps == 'comps':
                # Save all days
                plt_this = pred_arrs0[i]
            # Add the prediction array to the list
            pred_arrs.append(plt_this)
        else:
            if maps_or_comps == 'maps':
                # Take the difference
                temp_arr = truth - pred_arrs0[i]
            elif maps_or_comps == 'comps':
                temp_arr = pred_arrs0[i]
            # Average over the specified time period
            plt_this = np.average(temp_arr[start_doy:end_doy, :, :], axis=0)
            # Add the prediction array to the list
            pred_arrs.append(plt_this)

    # Get the minimum and maximum values across the truth, stage1, and stage2 arrays
    vmin, vmax = udata.get_vminmax(pred_arrs)
    
    # Get the halfrange for use with a diverging color map
    chr = udata.get_max_abs_val([vmin, vmax])
    # Scale the color bar
    if clr_bar_scale < 0 or clr_bar_scale > 1:
        warnings.warn("clr_bar_scale should be between 0 and 1. Setting it to 0.5.")
        clr_bar_scale = 0.5
    if clr_bar_scale != 1:
        chr *= clr_bar_scale
        cbe = 'both'
    else:
        cbe = 'neither'

    # Loop across each run
    for i in range(len(runs_in_set)):
        run = runs_in_set[i]
        # Load the prediction values for this run
        pred_arr = np.load(unox.get_pred_data(
            stage=stage, 
            HPC_run=f"{set_name}/{run}",
            year=year,
        ))
        # Assemble plot title
        if set_name[0] == "_":
            this_ax_title = run.replace(f"{set_name[1:]}_", "")
        else:
            this_ax_title = run.replace(f"{set_name}_", "")
        # Plot this run
        if maps_or_comps == 'maps':
            plot_npy_map(
                fig,
                ax[i+2],
                pred_arrs[i],
                lats,
                lons,
                c_halfrange=chr, 
                cb_extend=cbe,
                ax_title=this_ax_title,
            )
        elif maps_or_comps == 'comps':
            q = plot_comparison(
                plt_truth, 
                pred_arrs[i],
                label_x='truth',
                label_y=f"Pred with {this_ax_title}",
                ax=ax[i+2],
                hist_params={'bins':100, 'vmax':1000, 'vmin':10},
                cmap=pplt.Colormap('viridis'),
                log_scale=True,
                set_under_val=1,
            )
            ax[i+2].colorbar(q, loc='r', label='Count per pixel', formatter='sci')

    # Get the variable label and units
    var_label, var_units = uplt_fmt.get_var_label_and_units(y_var)
    # Add one overall colorbar for the entire figure on the right-hand side
    # cbar = make_colorbar(fig, ax[2].get_children()[0], var_label+' '+var_units, num_ticks=9, cb_loc='b', cb_extend=cbe)
    # Set the figure title
    fig.suptitle(f"HPC run set: {set_name}, input set: {this_input_set} - {overall_title}", fontsize=title_font_size)
    return fig