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