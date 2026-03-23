import keras
from keras import backend as K
import keras.src.legacy.backend as KL
import tensorflow as tf

# Verify version of tensorflow package
target_version = "2.17.0"
if tf.__version__ < target_version:
    raise ImportError(f"TensorFlow version must be {target_version} or higher, got: {tf.__version__}")

@keras.saving.register_keras_serializable(package="unox", name="r2_keras")
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
    SS_res =  KL.sum(KL.square(y_t - y_p)) 
    SS_tot = KL.sum(KL.square(y_t - KL.mean(y_t))) 
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )
  
@keras.saving.register_keras_serializable(package="unox", name="msenonzero")
def msenonzero(
    y_true, 
    y_pred
):
    """Calculate the mean squared error ignoring zero values.

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
    return KL.sum(KL.square(y_p - y_t), axis=-1)

