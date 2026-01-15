from tensorflow.keras import models

from unox.HPC.data0.paths import verify_path
# Import functions used in building models to allow for importing custom objects
from unox.HPC.utils import functions

def load_model(
    model_path: str,
):
    """Load a trained model from a file.

    Parameters
    ----------
    model_path : str
        Path to the model file. Should be an .h5 or .keras file.

    Returns
    -------
    model : tf.keras.Model
        The loaded model.

    Examples
    --------
    >>> model = load_model('model.h5')
    >>> model.summary()
    """
    # Verify the model path
    model_path = verify_path(model_path)
    # Vertify the path ends with .h5 or .keras
    if not (model_path.endswith('.h5') or model_path.endswith('.keras')):
        raise ValueError(f"(load_model) `model_path` must end with .h5 or .keras. Got: {model_path}")
    # Load the model
    model = models.load_model(model_path)
    return model