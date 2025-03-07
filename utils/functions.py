from keras import backend as K
import tensorflow as tf
import numpy as np
import random

def r2_keras(y_true, y_pred):
    y_t = tf.multiply(y_true, tf.cast(tf.not_equal(y_true, 0), tf.float32))
    y_p = tf.multiply(y_pred, tf.cast(tf.not_equal(y_true, 0), tf.float32))
    SS_res =  K.sum(K.square(y_t - y_p)) 
    SS_tot = K.sum(K.square(y_t - K.mean(y_t))) 
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )
  

def msenonzero(y_true, y_pred):
    y_t = tf.multiply(y_true, tf.cast(tf.not_equal(y_true, 0), tf.float32))
    y_p = tf.multiply(y_pred, tf.cast(tf.not_equal(y_true, 0), tf.float32))
    return K.sum(K.square(y_p - y_t), axis=-1)


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
