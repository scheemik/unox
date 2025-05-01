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

def plot_nox(datafile='../../datafiles/nox_2019_t106_US.nc'):
    """Plots a map of NOx data.

    Creates a map of NOx data on a map using the provided data file.

    Parameters
    ----------
    datafile : str
        Path to the data file containing NOx data.
    """
    import xarray as xr
    nox = xr.open_dataset(datafile)  #nox dataset used to make y files
#     lat_us = nox.lat.data.round(3)  #select lat and lon range where we have nox data
#     lon_us = nox.lon.data.round(3)
# 
#     from unox import load_lats_lons
#     lats, lons = load_lats_lons()
# 
#     #find indices of lats and lons that are in the us nox data
#     #for some reason the simpler way doesn't work
#     latmin = np.where(np.abs(lats-np.min(lat_us))<0.1)[0][0]
#     latmax = np.where(np.abs(lats-np.max(lat_us))<0.1)[0][0] + 1
#     print(latmin,latmax)
#     print(lats[latmin:latmax])
#     print(lat_us)
# 
#     lonmin = np.where(np.abs(lons-np.min(lon_us))<0.1)[0][0]
#     lonmax = np.where(np.abs(lons-np.max(lon_us))<0.1)[0][0] + 1
#     print(lonmin,lonmax)
#     print(lons[lonmin:lonmax])
#     print(lon_us)

    # print(lat_ind)
    nox.nox[0].plot()