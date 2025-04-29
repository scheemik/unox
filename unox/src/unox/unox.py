import numpy as np
import os

def load_lats_lons():
    """Load latitude and longitude data from files."""
    with open('datafiles/lats.npy', 'rb') as f:
        lats = np.load(f)
    with open('datafiles/lons.npy', 'rb') as f:
        lons = np.load(f)
    return lats, lons

def show_available_data(path='original_sample_data/'):
    """Prints a list of available data in the given directory."""
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            show_available_data(full_path)
        else:
            print(full_path)