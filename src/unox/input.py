import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib as mpl

def find_npy(year, which='old'):
    """Load latitude and longitude data from files.

    Loads arrays of latitude and longitude values that cover 
    the region of interest.

    Parameters
    ----------
    path : str
        Relative path to the directory containing data files.

    Returns
    -------
    lats : numpy.ndarray
        Array of latitude values.
    lons : numpy.ndarray
        Array of longitude values.

    Examples
    --------
    >>> lats, lons = load_lats_lons()
    """
    if which == 'old':
        this_str = 'sample_data'
        this_title = this_str
    elif which == 'new':
        this_str = 'inputfiles'
        this_title = this_str
    elif which == 'evelyns':
        this_str = '/data/high_res/emacdonald/unet/datafiles/inputfiles'
        this_title = '/data/.../inputfiles'
    year_str = '/stage1/y/Y_'+str(year)+'.npy'
    filepath = this_str+year_str
    with open(filepath, 'rb') as f:
        this_npy = np.load(f)
    return this_npy, this_title+year_str

def plot_npy(year, which='old', compare=None):
    this_npy, this_npy_title = find_npy(year, which)
    if isinstance(compare, type(None)):
        plt.imshow(this_npy[0])
    plt.colorbar()
    plt.title(this_npy_title)
    plt.show()