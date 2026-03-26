import numpy as np
import xarray as xr
import pandas as pd

from model.core import Unet
from utils.functions import r2_keras
from utils.functions import msenonzero
from data0.load_input import get_npy_from_netcdf

def begin_training(
    savedir,
    stage,
    xtrain,
    ytrain,
    xtest,
    ytest,
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
        xtest : `np.ndarray`
            Testing input features.
        ytest : `np.ndarray`
            Testing target variables.
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
    if not isinstance(xtest, np.ndarray):
        raise TypeError(f"(begin_training) `xtest` must be a numpy array. Got type: {type(xtest)}")
    if not isinstance(ytest, np.ndarray):
        raise TypeError(f"(begin_training) `ytest` must be a numpy array. Got type: {type(ytest)}")
    if not isinstance(unet, Unet):
        raise TypeError(f"(begin_training) `unet` must be a Unet. Got type: {type(unet)}")
    if not isinstance(batch_size, int):
        raise TypeError(f"(begin_training) `batch_size` must be an integer. Got type: {type(batch_size)}")
    if not isinstance(n_epochs, int):
        raise TypeError(f"(begin_training) `n_epochs` must be an integer. Got type: {type(n_epochs)}")
    if save_format not in ['h5', 'keras', 'both']:
        raise ValueError(f"(begin_training) `save_format` must be `h5`, `keras`, or `both`. Got: {save_format}")

    # Set up callbacks, do not import keras functions before using xarray on Trillium
    from keras.callbacks import CSVLogger, EarlyStopping, ModelCheckpoint
    # Log information into a CSV file
    csv_logger = CSVLogger(f"{savedir}unet_stage{stage}_log.csv", append=True, separator=';')
    # Stop the training early if minimal improvements are made
    earlystopper = EarlyStopping(patience=15, verbose=1)
    # Save out checkpoints of the model every epoch
    ## All but the most recent checkpoint will be deleted upon completion of the model run
    checkpointer = ModelCheckpoint(f"{savedir}checkpts/unet_checkpt_{{val_loss:.2f}}_{{r2_keras:.2f}}_stage{stage}.keras", verbose=0, save_best_only=True)
    print("")
    print(f"#### Begin training stage {stage} ####")
    unet.train(xtrain, ytrain, validation_data=(xtest, ytest), batch_size=batch_size, epochs=n_epochs, callbacks=[earlystopper, checkpointer, csv_logger], shuffle=True)
    # Save model weights
    if save_format in ['h5', 'both']:
        unet.save_model(f"{savedir}unet_stage{stage}_model.h5")
    if save_format in ['keras', 'both']:
        unet.save_model(f"{savedir}unet_stage{stage}_model.keras")
    return unet


def make_predictions(
    uarr,
    unet,
    config_dict,
    config_path,
    predictions_metadata,
    stage = 1,
    end_date = None,
):
    """ Prepare the input data for the model.

        Get the training data from the input NetCDF dataset as numpy arrays
        and concatenate them along the time dimension.

        Parameters
        ----------
        uarr : `unox.uarray`
            The dataset of the input NetCDF file.
        unet : `Unet`
            The Unet model to be trained.
        config_dict : `dict`
            A dictionary containing the configuration.
        config_path : `str` 
            Path to the input configuration JSON file used to make `config_dict`.
        predictions_metadata : `dict`
            The dictionary of metadata describing the output of a model run.
        stage : `int`
            The stage of the data to plot (1 or 2).
        
        Returns
        -------
        xtrain : np.ndarray
            Concatenated training input features.
        ytrain : np.ndarray
            Concatenated training target variables.
        predictions_metadata : dict
            The dictionary of metadata describing the output of a model run with values added for `train_years` and `unet_build_shape`.
    """
    # Verify argument types
    uarr._verify()
    if not isinstance(config_dict, (str, type({}))):
        raise TypeError(f"(make_predictions) `config_dict` must be a str or dict. Got type: {type(config_dict)}.")
    if not isinstance(predictions_metadata, type({})):
        raise TypeError(f"(make_predictions) `predictions_metadata` must be a dict. Got type: {type(predictions_metadata)}.")
    if not isinstance(config_path, str):
        raise TypeError(f"(make_predictions) `config_path` must be a string. Got type: {type(config_path)}.")
    if stage not in [1, 2]:
        raise ValueError(f"(make_predictions) `stage` must be either 1 or 2. Got: {stage}.")
    
    # Get the verification split date from the model configuration
    if 'verification_split_date' in config_dict:
        split_date = config_dict['verification_split_date']
    else:
        raise ValueError(f"(make_predictions) `config_dict` must have a `verification_split_date` key specifying the date on which to split the data between training / testing and verification.")
    # Get the end date
    if isinstance(end_date, type(None)):
        # Get the last date in the dataset
        end_date = uarr.xr.time.values[-1]
        # Convert to string in the format 'YYYY-MM-DD'
        end_date = np.datetime_as_string(end_date, unit='D')
    elif not isinstance(end_date, str):
        raise TypeError(f"(make_predictions) `end_date` must be a string in the format 'YYYY-MM-DD' or None. Got type: {type(end_date)}.")
    
    # Get the data arrays
    x_test, in_lats, in_lons = get_npy_from_netcdf(
        uarr.xr,
        config_dict,
        start_date=split_date,
        end_date=end_date,
        x_or_y='x',
    )

    # Make the predictions
    pred = unet.predict(x_test)
    # Put the predictions into an xarray Dataset
    pred_xarray = xr.Dataset(
        data_vars=dict(
            # Squeeze the predictions array to reduce dimensions 
            # from (364, n_lat, n_lon, 1) to (364, n_lat, n_lon)
            pred_temp=(["time", "lat", "lon"], pred.squeeze())
        ),
        coords={
            "time":uarr.xr.time,
            "lat":in_lats, 
            "lon":in_lons,
        },
    )

    #     # Get the years
    #     years = uarr._get_years()
    #     # Get the long name and units of the y variable to put in the new xarray
    #     y_var = uarr.xr.attrs['y_var']
    #     y_var_name = uarr.xr[y_var].long_name
    #     y_var_unit = uarr.xr[y_var].units
    #     # Create a new variable name and long name
    #     if stage == 1:
    #         pred_var = f"{y_var}_pred"
    #         pred_var_name = f"Predicted {y_var_name}"
    #     elif stage == 2:
    #         pred_var = f"{y_var}_pred_s2"
    #         pred_var_name = f"Predicted {y_var_name} (stage 2)"
    #     # Create a blank list to add predictions to
    #     pred_xr_arr = []
    #     # Make predictions based on x data for years >= split_year
    #     for year in range(config_dict['split_year'], max(years)+1):
    #         print(f"Generating predictions for year: {year}")
    #         x_test, in_lats, in_lons = get_npy_from_netcdf(uarr.xr, year, config_path, x_or_y='x')
    #         # Make the predictions
    #         pred = unet.predict(x_test)
    #         # Add year to the list of predictions in the metadata dictionary
    #         predictions_metadata['pred_years'][f'stage{stage}'].append(year)
    # 
    #         # Select the data for the specified year
    #         data_for_year = uarr._select_year(year)
    #         # Load the output to an xarray Dataset
    #         this_year_pred_xr = xr.Dataset(
    #             data_vars=dict(
    #                 # Squeeze the predictions array to reduce dimensions 
    #                 # from (364, n_lat, n_lon, 1) to (364, n_lat, n_lon)
    #                 pred_temp=(["time", "lat", "lon"], pred.squeeze())
    #             ),
    #             coords={
    #                 "time":data_for_year["time"],
    #                 "lat":in_lats, 
    #                 "lon":in_lons,
    #             },
    #         )
    #         pred_xr_arr.append(this_year_pred_xr)
    #     # Concatenate the new data with the existing dataset along the time dimension
    #     pred_xarray = xr.concat(pred_xr_arr, dim='time')
    
    # Rename prediction variable and add attributes
    pred_xarray = pred_xarray.rename({'pred_temp': pred_var})
    pred_xarray[pred_var].attrs = {'long_name': pred_var_name, 'units': y_var_unit}
    # Copy over the attributes for the latitude and longitude
    for coord in ['lat', 'lon']:
        for this_attr in uarr.xr[coord].attrs.keys():
            pred_xarray[coord].attrs[this_attr] = uarr.xr[coord].attrs[this_attr]
    # Add global attributes for the prediction file
    pred_xarray.attrs['description'] = f"Predicted {y_var_name} using a U-net model"
    pred_xarray.attrs['modification_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    pred_xarray.attrs['y_var'] = f"{y_var}"
    pred_xarray.attrs['input_set'] = f"{uarr.name}"
    pred_xarray.attrs['config_path'] = f"{config_path}"
    pred_xarray.attrs['config_dict'] = f"{config_dict}"
    # Copy over global attributes from the input xarray
    for this_attr in uarr.xr.attrs.keys():
        if this_attr in ['stages']:
            pred_xarray.attrs[this_attr] = [1]
        elif this_attr in ['x_vars', 'stage_2_cutoff']:
            pred_xarray.attrs[this_attr] = config_dict[this_attr]
        elif this_attr not in ['description', 'modification_date', 'y_var', 'x_vars', 'x1_vars', 'x2_vars']:
            pred_xarray.attrs[this_attr] = uarr.xr.attrs[this_attr]
    # Undo the scaling of the variables, if applicable
    if 'model_scale_factors' in config_dict:
        scale_factors = config_dict['model_scale_factors']
        for var in pred_xarray.data_vars:
            if var in scale_factors:
                this_scale_factor = scale_factors[var]
                print(f"Undoing scale factor of {this_scale_factor} for variable {var}.")
                pred_xarray[var] = pred_xarray[var]/this_scale_factor

    return pred_xarray, predictions_metadata