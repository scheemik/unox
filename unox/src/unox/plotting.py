import matplotlib.pyplot as plt

def plot_lats_lons(lats, lons):
    """Plot the given latitudes and longitudes."""
    # Get the shorter of the two list lengths
    min_length = min(len(lats), len(lons))
    print('min_length', min_length)
    fig = plt.scatter(lats[0:min_length], lons[0:min_length])
    plt.xlabel("Latitudes")
    plt.ylabel("Longitudes")
    plt.show()
    return fig