import numpy as np
import random

def data_split(
    x, 
    y, 
    ratio, 
    maskname=None
):
    """ Split data into training and validation sets.

        Randomly split the input data arrays into two sets based on the given ratio.

        Parameters
        ----------
        x : `numpy.ndarray`
            The input features array.
        y : `numpy.ndarray`
            The target variables array.
        ratio : `float`
            The ratio of data to use for the first split (e.g., 0.8 for 80% training).
        maskname : `str`, optional
            If provided, save the split masks to a .npz file with this name.

        Returns
        -------
        x1 : `numpy.ndarray`
            The first split of input features.
        y1 : `numpy.ndarray`
            The first split of target variables.
        x2 : `numpy.ndarray`
            The second split of input features.
        y2 : `numpy.ndarray`
            The second split of target variables.
    """
    dsize = int(x.shape[0] * ratio)
    dmask = np.array(list(range(0, x.shape[0])))
    random.shuffle(dmask)

    dmask1 = dmask[:dsize]
    x1 = x[dmask1]
    y1 = y[dmask1]

    dmask2 = dmask[dsize:]
    x2 = x[dmask2]
    y2 = y[dmask2]

    if maskname:
        np.savez(maskname, mask1=dmask1, mask2=dmask2)

    return x1, y1, x2, y2
