# read version from installed package
from importlib.metadata import version
__version__ = version("unox")

# Verify version of tensorflow package
import tensorflow as tf
target_version = "2.17.0"
if tf.__version__ < target_version:
    raise ImportError(f"TensorFlow version must be {target_version} or higher, got: {tf.__version__}")