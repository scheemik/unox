import numpy as np
import random

def data_split(x, y, ratio, maskname=None):
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
