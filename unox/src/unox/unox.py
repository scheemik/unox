import numpy as np

def load_lats_lons():
    """Load latitude and longitude data from files."""
    with open('datafiles/lats.npy', 'rb') as f:
        lats = np.load(f)
    with open('datafiles/lons.npy', 'rb') as f:
        lons = np.load(f)
    return lats, lons