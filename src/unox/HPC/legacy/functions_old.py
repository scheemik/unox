from keras import backend as K
import tensorflow as tf

def r2_keras(
    y_true, 
    y_pred
):
    """ Calculate the R-squared metric for Keras models.

        Compute the coefficient of determination (R-squared) for regression tasks, ignoring zero values in the true labels.

        Parameters
        ----------
        y_true : `tensorflow.Tensor`
            The true labels.
        y_pred : `tensorflow.Tensor`
            The predicted labels.

        Returns
        -------
        r2 : `tensorflow.Tensor`
            The R-squared value.
    """
    y_t = tf.multiply(y_true, tf.cast(tf.not_equal(y_true, 0), tf.float32))
    y_p = tf.multiply(y_pred, tf.cast(tf.not_equal(y_true, 0), tf.float32))
    SS_res =  K.sum(K.square(y_t - y_p)) 
    SS_tot = K.sum(K.square(y_t - K.mean(y_t))) 
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )
  

def msenonzero(
    y_true, 
    y_pred
):
    """ Calculate the mean squared error ignoring zero values.

        Compute the MSE for regression tasks, ignoring zero values in the true labels.

        Parameters
        ----------
        y_true : `tensorflow.Tensor`
            The true labels.
        y_pred : `tensorflow.Tensor`
            The predicted labels.

        Returns
        -------
        mse : `tensorflow.Tensor`
            The mean squared error ignoring zeros.
    """
    y_t = tf.multiply(y_true, tf.cast(tf.not_equal(y_true, 0), tf.float32))
    y_p = tf.multiply(y_pred, tf.cast(tf.not_equal(y_true, 0), tf.float32))
    return K.sum(K.square(y_p - y_t), axis=-1)

