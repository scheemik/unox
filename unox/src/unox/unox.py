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
    # Check if the path exists
    if not os.path.exists(path):
        try:
            path = '../' + path
            os.path.exists(path) == True
        except:
            print(f"Path {path} does not exist.")
            return []
    data_files = recursive_paths(path)
    for data_file in data_files:
        print(data_file)
    return data_files

def recursive_paths(path):
    """Recursively lists all files in the given path."""
    path_list = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            for this_path in recursive_paths(full_path):
                path_list.append(this_path)
        else:
            path_list.append(full_path)
    return path_list