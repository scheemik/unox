import matplotlib.pyplot as plt

def plot_lats_lons(lats, lons):
    """Plot the given latitudes and longitudes.

    This will eventually plot the latitudes and longitudes on a map.

    Parameters
    ----------
    lats : numpy.ndarray
        Array of latitude values.
    lons : numpy.ndarray
        Array of longitude values.
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    
    Examples
    --------
    >>> lats, lons = load_lats_lons()
    >>> fig = plot_lats_lons(lats, lons)
    """
    # Get the shorter of the two list lengths
    min_length = min(len(lats), len(lons))
    print('min_length', min_length)
    fig = plt.scatter(lats[0:min_length], lons[0:min_length])
    plt.xlabel("Latitudes")
    plt.ylabel("Longitudes")
    plt.show()
    return fig

def plot_nox(datafile='../datafiles/nox_2019_t106_US.nc',
             datetime='2019-01-01T00:00:00',
             cbar_max=1.2e-10,):
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
    import xarray as xr
    import proplot as pplt
    nox = xr.open_dataset(datafile)  #nox dataset used to make y files
    # Simplest way to plot the data
    # nox.nox[0].plot()
    # A more complex way to plot the data
    # Select the time to plot
    nox_sel_time = nox.nox.sel(time=datetime)
    # Find the min and max lat and lon values
    lat_min = nox.lat.min().values
    lat_max = nox.lat.max().values
    lon_min = nox.lon.min().values
    lon_max = nox.lon.max().values
    fig = pplt.figure(refwidth=10)
    pplt.rc.reso = 'med' # Select medium resolution for features
    axs = fig.subplots(nrows=1, proj='cyl')
    this_nox = axs.pcolorfast(nox_sel_time, vmin=0, vmax=cbar_max)
    axs.format(
        lonlim=(lon_min, lon_max), latlim=(lat_min, lat_max),
        suptitle='Figure with single projection',
        latlines=10, lonlines=10, coast=True,
        labels=True, gridminor=True
    )
    fig.colorbar(this_nox, loc='b', label='NOx emissions (kg/m2/s)')
    plt.show()