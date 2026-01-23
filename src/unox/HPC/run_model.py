#test code based on Unet_Chinese_NOx example_code.ipynb
import numpy as np
import pandas as pd
import glob
import sys
import os 
import xarray as xr
import json

from data0.load_input import get_npy_from_netcdf
from data0.dataset import uarray
from data0.paths import verify_path
from utils.data_split import data_split
import data0.run_functions as rf
import data0.run_functions as rf

print("")
print("===== Begin run_model.py =====")
print(f"Current working directory: {os.getcwd()}")

# Set parameters
n_epochs = 250
model_fmt = 'keras' # 'h5', 'keras', or 'both'
input_fmt = 'nc' # 'nc' or 'npy'
output_fmt = 'nc' # 'nc', 'npy', or 'both'
split_year = 2019
split_value = 0.9

# -------- Get input arguments --------
print("Using input arguments:")
savedir, config_dict, config_path, version = rf.process_cmd_args(sys.argv)
# Get the inputset from the config file
inputfiles = config_dict['input_set']

##################################################################
##################################################################
# Create output metadata dictionary

output_metadata = rf.make_output_metadata_dict(
    savedir,
    config_path,
    config_dict,
    version,
    n_epochs,
    model_fmt,
    input_fmt,
    split_year,
    split_value,
)

##################################################################
# Stage-1 training
## Load stage-1 data sets

if input_fmt == 'npy':
    from legacy.run_functions_old import prepare_input
elif input_fmt == 'nc':
    prepare_input = rf.prepare_input
# Load the input netcdf file
uarr = uarray(inputfiles, is_input_set=True)
# Get the years
years = uarr._get_years()
# Prepare the input files
xtrain, ytrain, output_metadata = prepare_input(uarr, config_path, output_metadata, split_year, stage=1)
# Split into training and validation sets
xtrain, ytrain, xvalid, yvalid = data_split(xtrain, ytrain, split_value)
print("After data split:")
print(f"\tShape of xtrain: {xtrain.shape}")
print(f"\tShape of ytrain: {ytrain.shape}")
print(f"\tShape of xvalid: {xvalid.shape}")
print(f"\tShape of yvalid: {yvalid.shape}")

print("Done loading data sets for stage 1")
print(output_metadata['unet_build_shape'])
# exit(0)

##################################################################

# Import packages based on version
if version == 0: # keras v2.9.0, tensorflow v2.9.2
    from utils.functions_old import r2_keras
    from utils.functions_old import msenonzero
    from model.core_old import Unet
elif version == 1: # keras v3.10.0, tensorflow v2.17.0
    from utils.functions import r2_keras
    from utils.functions import msenonzero
    from model.core import Unet
from tensorflow.keras.optimizers import Adam
from keras.callbacks import CSVLogger, EarlyStopping, ModelCheckpoint

##################################################################
# Build and compile the Unet

unet = Unet()
# The input shape for `build` should be [lat, lon, var]
print(f"\tShape of model input layer to build: ({output_metadata['unet_build_shape']})")
unet.build(output_metadata['unet_build_shape'])
opt = Adam(learning_rate=1e-5) 

unet.compile(optimizer=opt, loss=msenonzero, metrics=[r2_keras, msenonzero])
unet.summary()

##################################################################

# Stage-1 training of the Unet

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
    """Begin training the Unet model.

    Parameters
    ----------
    savedir : str
        Directory to save outputs.
    stage : int
        The stage number (1 or 2).
    xtrain : np.ndarray
        Training input features.
    ytrain : np.ndarray
        Training target variables.
    xvalid : np.ndarray
        Validation input features.
    yvalid : np.ndarray
        Validation target variables.
    unet : Unet
        The Unet model to be trained.
    batch_size : int, optional
        Batch size for training.
    n_epochs : int, optional
        Number of epochs for training.
    save_format : str, optional
        Format to save the model ('h5', 'keras', or 'both').
    
    Returns
    -------
    unet : Unet
        The trained Unet model.
    """
    # Check the stage number
    if stage not in [1, 2]:
        raise ValueError(f"(begin_training) `stage` must be 1 or 2. Got: {stage}")
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

unet = begin_training(savedir, stage=1, xtrain=xtrain, ytrain=ytrain, xvalid=xvalid, yvalid=yvalid, unet=unet, batch_size=30, n_epochs=n_epochs, save_format=model_fmt)

# Generate predictions for evaluation
### Load testing data sets

def load_test_files(
    x_files,
    stage,
):
    """Load test files for a given stage.

    Parameters
    ----------
    x_files : list
        List of input feature files.
    stage : int
        The stage number (1 or 2).

    Returns
    -------
    xtest_files : list
        List of test input feature files.
    """
    # Decide on split index based on stage
    if stage == 1:
        split_index = 14
    elif stage == 2:
        split_index = 5
    else:
        raise ValueError(f"(load_test_files) `stage` must be 1 or 2. Got: {stage}")
    # Gather just the testing files
    xtest_files = x_files[split_index:]
    print("")
    print(f"Number of xtest_files: {len(xtest_files)}")
    return xtest_files

def predict_and_save(
    savedir,
    model,
    **kwargs,
):
    """Generate predictions using the model and save them.

    Parameters
    ----------
    savedir : str
        Directory to save outputs.
    model : Unet
        The trained Unet model.
    **kwargs : dict
        Additional keyword arguments to be passed to load_test_files().
    """
    xtest_files = load_test_files(**kwargs)
    # Loop across test files and generate predictions
    for x in xtest_files:
        xnow = np.load(x)
        pred = model.predict(xnow)
        np.save(f"{savedir}stage{kwargs['stage']}_output/pred_{x.split('/')[-1]}", pred)

if output_fmt == 'npy':
    predict_and_save(savedir, unet, x_files=x_files, stage=1)
elif output_fmt == 'nc' or output_fmt == 'both':
    # Get the long name and units of the y variable to put in the new xarray
    y_var = uarr.xr.attrs['y_var']
    y_var_name = uarr.xr[y_var].long_name
    y_var_unit = uarr.xr[y_var].units
    # Create a new variable name and long name
    pred_var = f"{y_var}_pred"
    pred_var_name = f"Predicted {y_var_name}"
    # Create a blank list to add predictions to
    pred_xr_arr = []
    # Make predictions based on x data for years >= split_year
    for year in range(split_year, max(years)+1):
        print(f"Generating predictions for year: {year}")
        x_test, in_lats, in_lons = get_npy_from_netcdf(uarr.xr, year, config_path, x_or_y='x')
        # Make the predictions
        pred = unet.predict(x_test)
        # Save the numpy array to file
        if output_fmt == 'both':
            np.save(f"{savedir}stage1_output/pred_X_{year}.npy", pred)
        # Add year to the list of predictions in the metadata dictionary
        output_metadata['pred_years']['stage1'].append(year)

        # Select the data for the specified year
        data_for_year = uarr._select_year(year)
        # Load the output to an xarray Dataset
        this_year_pred_xr = xr.Dataset(
            data_vars=dict(
                # Squeeze the predictions array to reduce dimensions 
                # from (364, n_lat, n_lon, 1) to (364, n_lat, n_lon)
                pred_temp=(["time", "lat", "lon"], pred.squeeze())
            ),
            coords={
                "time":data_for_year["time"],
                "lat":in_lats, 
                "lon":in_lons,
            },
        )
        pred_xr_arr.append(this_year_pred_xr)
    # Concatenate the new data with the existing dataset along the time dimension
    pred_xarray = xr.concat(pred_xr_arr, dim='time')
    # Rename prediction variable and add attributes
    pred_xarray = pred_xarray.rename({'pred_temp': pred_var})
    pred_xarray[pred_var].attrs = {'long_name': pred_var_name, 'units': y_var_unit}
    # Copy over the attributes for the latitude and longitude
    for coord in ['lat', 'lon']:
        for this_attr in data_for_year[coord].attrs.keys():
            pred_xarray[coord].attrs[this_attr] = data_for_year[coord].attrs[this_attr]
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
    # Save the xarray to a file
    pred_xarray.to_netcdf(f"{savedir}predictions.nc")
else:
    raise ValueError(f"`output_fmt` must be 'npy', 'nc', or 'both'. Got: {output_fmt}")

print('Done with stage 1')
if config_dict['stage_2'] == False:
    exit(0)

##################################################################
# Stage-2 training
## Load stage-2 data sets

if input_fmt == 'npy':
    x_files, y_files = load_input_files(inputfiles, stage=2)
    x_train, y_train, x_valid, y_valid = split_input_files(x_files, y_files, stage=2, split_value=0.9)
elif input_fmt == 'nc':
    # Load the input netcdf file
    uarr = uarray(inputfiles, is_input_set=True)
    # Get the years
    years = uarr._get_years()
    # Prepare the input files
    xtrain, ytrain, output_metadata = rf.prepare_input(uarr, config_path, output_metadata, split_year, stage=2)
    # Split into training and validation sets
    xtrain, ytrain, xvalid, yvalid = data_split(xtrain, ytrain, split_value)
    print("After data split:")
    print(f"\tShape of xtrain: {xtrain.shape}")
    print(f"\tShape of ytrain: {ytrain.shape}")
    print(f"\tShape of xvalid: {xvalid.shape}")
    print(f"\tShape of yvalid: {yvalid.shape}")

print('Done loading data sets for stage 2')

# Load the pre-trained model weights from stage-1
if model_fmt in ['keras', 'both']:
    unet.load_weights(f"{savedir}unet_stage1_model.keras")
elif model_fmt in ['h5']:
    unet.load_weights(f"{savedir}unet_stage1_model.h5")
else:
    raise ValueError(f"`model_fmt` must be 'h5', 'keras', or 'both'. Got: {model_fmt}")


# Stage-2 training of the Unet

unet = begin_training(savedir, stage=2, xtrain=xtrain, ytrain=ytrain, xvalid=xvalid, yvalid=yvalid, unet=unet, batch_size=30, n_epochs=n_epochs, save_format=model_fmt)

if output_fmt == 'npy':
    predict_and_save(savedir, unet, x_files=x_files, stage=2)
elif output_fmt == 'nc' or output_fmt == 'both':
    # Create a new variable name and long name
    pred_var = f"{y_var}_pred_s2"
    pred_var_name = f"Predicted {y_var_name} (stage 2)"
    # Create a blank list to add predictions to
    pred_xr_arr_s2 = []
    # Make predictions based on x data for years >= split_year
    for year in range(split_year, max(years)+1):
        print(f"Generating predictions for year: {year}")
        x_test, in_lats, in_lons = get_npy_from_netcdf(uarr.xr, year, config_path, x_or_y='x')
        # Make the predictions
        pred = unet.predict(x_test)
        # Save out the numpy array to file
        if output_fmt == 'both':
            np.save(f"{savedir}stage2_output/pred_X_{year}.npy", pred)
        # Add year to the list of predictions in the metadata dictionary
        output_metadata['pred_years']['stage2'].append(year)

        # Select the data for the specified year
        data_for_year = uarr._select_year(year)
        # Load the output to an xarray Dataset
        this_year_pred_xr = xr.Dataset(
            data_vars=dict(
                # Squeeze the predictions array to reduce dimensions 
                # from (364, n_lat, n_lon, 1) to (364, n_lat, n_lon)
                pred_temp=(["time", "lat", "lon"], pred.squeeze())
            ),
            coords={
                "time":data_for_year["time"],
                "lat":in_lats, 
                "lon":in_lons,
            },
        )
        pred_xr_arr_s2.append(this_year_pred_xr)
    # Concatenate the new data with the existing dataset along the time dimension
    pred_xarray_s2 = xr.concat(pred_xr_arr_s2, dim='time')
    # Rename prediction variable and add attributes
    pred_xarray_s2 = pred_xarray_s2.rename({'pred_temp': pred_var})
    pred_xarray_s2[pred_var].attrs = {'long_name': pred_var_name, 'units': y_var_unit}
    # Add the stage 2 predictions to the stage 1 xarray
    pred_xarray[pred_var] = pred_xarray_s2[pred_var]
    # Merge the stage 2 predictions into the stage 1 xarray
    # pred_xarray.merge(pred_xarray_s2)
    # Copy over the attributes for the latitude and longitude
    for coord in ['lat', 'lon']:
        for this_attr in data_for_year[coord].attrs.keys():
            pred_xarray[coord].attrs[this_attr] = data_for_year[coord].attrs[this_attr]
    # Add global attributes for the prediction file
    pred_xarray.attrs['modification_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    # Copy over global attributes from the input xarray
    for this_attr in uarr.xr.attrs.keys():
        if this_attr in ['stages']:
            pred_xarray.attrs[this_attr] = [1,2]
    # Save the xarray to a file
    pred_xarray.to_netcdf(f"{savedir}predictions.nc")
else:
    raise ValueError(f"`output_fmt` must be 'npy', 'nc', or 'both'. Got: {output_fmt}")

# Save the output metadata dictionary to file
print('output_metadata:', output_metadata)
import json
with open(f"{savedir}output_metadata.json", 'w') as file:
    file.write(json.dumps(output_metadata, indent=4))

print("")
print("Done running test_unet.py")





