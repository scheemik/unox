import numpy as np
from keras.callbacks import CSVLogger, EarlyStopping, ModelCheckpoint

from model.core import Unet
from utils.functions import r2_keras
from utils.functions import msenonzero

def begin_training(
    savedir,
    stage,
    xtrain,
    ytrain,
    xvalid,
    yvalid,
    unet,
    batch_size=30,
    n_epochs=250,
    save_format='keras',
):
    """ Begin training the Unet model.

        Parameters
        ----------
        savedir : `str`
            Directory to save outputs.
        stage : `int`
            The stage number (1 or 2).
        xtrain : `np.ndarray`
            Training input features.
        ytrain : `np.ndarray`
            Training target variables.
        xvalid : `np.ndarray`
            Validation input features.
        yvalid : `np.ndarray`
            Validation target variables.
        unet : `Unet`
            The Unet model to be trained.
        batch_size : `int`, optional
            Batch size for training.
        n_epochs : `int`, optional
            Number of epochs for training.
        save_format : `str`, optional
            Format to save the model ('h5', 'keras', or 'both').
        
        Returns
        -------
        unet : Unet
            The trained Unet model.
    """
    # Verify argument types
    if not isinstance(savedir, str):
        raise TypeError(f"(begin_training) `savedir` must be a string. Got type: {type(savedir)}")
    if stage not in [1, 2]:
        raise ValueError(f"(begin_training) `stage` must be 1 or 2. Got: {stage}")
    if not isinstance(xtrain, np.ndarray):
        raise TypeError(f"(begin_training) `xtrain` must be a numpy array. Got type: {type(xtrain)}")
    if not isinstance(ytrain, np.ndarray):
        raise TypeError(f"(begin_training) `ytrain` must be a numpy array. Got type: {type(ytrain)}")
    if not isinstance(xvalid, np.ndarray):
        raise TypeError(f"(begin_training) `xvalid` must be a numpy array. Got type: {type(xvalid)}")
    if not isinstance(yvalid, np.ndarray):
        raise TypeError(f"(begin_training) `yvalid` must be a numpy array. Got type: {type(yvalid)}")
    if not isinstance(unet, Unet):
        raise TypeError(f"(begin_training) `unet` must be a Unet. Got type: {type(unet)}")
    if not isinstance(batch_size, int):
        raise TypeError(f"(begin_training) `batch_size` must be an integer. Got type: {type(batch_size)}")
    if not isinstance(n_epochs, int):
        raise TypeError(f"(begin_training) `n_epochs` must be an integer. Got type: {type(n_epochs)}")
    if save_format not in ['h5', 'keras', 'both']:
        raise ValueError(f"(begin_training) `save_format` must be `h5`, `keras`, or `both`. Got: {save_format}")

    # Set up callbacks
    csv_logger = CSVLogger(f"{savedir}unet_stage{stage}_log.csv", append=True, separator=';')
    earlystopper = EarlyStopping(patience=15, verbose=1)
    checkpointer = ModelCheckpoint(f"{savedir}checkpts/unet_checkpt_{{val_loss:.2f}}_{{r2_keras:.2f}}_stage{stage}.h5", verbose=1, save_best_only=True)
    print("")
    print(f"#### Begin training stage {stage} ####")
    unet.train(xtrain, ytrain, validation_data=(xvalid, yvalid), batch_size=batch_size, epochs=n_epochs, callbacks=[earlystopper, checkpointer, csv_logger], shuffle=True)
    # Save model weights
    if save_format in ['h5', 'both']:
        unet.save_model(f"{savedir}unet_stage{stage}_model.h5")
    if save_format in ['keras', 'both']:
        unet.save_model(f"{savedir}unet_stage{stage}_model.keras")
    return unet