# Script to run the U-net model training and prediction
# Should be launched from the `HPC_slurm.sh` script
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

print("")
print("===== Begin run_model.py =====")
print(f"Current working directory: {os.getcwd()}")

# Set parameters
model_fmt = 'keras' # 'h5', 'keras', or 'both'

# -------- Get input arguments --------
print("Using input arguments:")
savedir, config_dict, config_path, version = rf.process_cmd_args(sys.argv)
# Get the inputset from the config file
inputfiles = config_dict['input_set']

##################################################################
##################################################################
# Create output metadata dictionary

predictions_metadata = rf.make_predictions_metadata_dict(
    savedir,
    config_path,
    config_dict,
    version,
    model_fmt,
)

##################################################################
# Stage-1 training
## Load stage-1 data sets

# Load the input netcdf file
uarr = uarray(inputfiles, is_input_set=True)
# Get the years
years = uarr._get_years()
# Prepare the input files
xtrain, ytrain, predictions_metadata = rf.prepare_input(uarr, config_path, predictions_metadata, config_dict['split_year'], stage=1)
# Split into training and validation sets
xtrain, ytrain, xvalid, yvalid = data_split(xtrain, ytrain, config_dict['split_value'])
print("After data split:")
print(f"\tShape of xtrain: {xtrain.shape}")
print(f"\tShape of ytrain: {ytrain.shape}")
print(f"\tShape of xvalid: {xvalid.shape}")
print(f"\tShape of yvalid: {yvalid.shape}")

print("Done loading data sets for stage 1")
print(predictions_metadata['unet_build_shape'])


##################################################################

from training import begin_training, make_predictions
# Import packages based on version
if version == 0: # keras v2.9.0, tensorflow v2.9.2
    from legacy.functions_old import r2_keras
    from legacy.functions_old import msenonzero
    from model.core_old import Unet
elif version == 1: # keras v3.10.0, tensorflow v2.17.0
    from utils.functions import r2_keras
    from utils.functions import msenonzero
    from model.core import Unet
from tensorflow.keras.optimizers import Adam

##################################################################
# Build and compile the Unet

unet = Unet()
# The input shape for `build` should be [lat, lon, var]
print(f"\tShape of model input layer to build: ({predictions_metadata['unet_build_shape']})")
unet.build(predictions_metadata['unet_build_shape'], act_reg=config_dict['act_reg'], act_reg_factor=config_dict['act_reg_factor'])
opt = Adam(learning_rate=1e-5) 

unet.compile(optimizer=opt, loss=msenonzero, metrics=[r2_keras, msenonzero])
unet.summary()

##################################################################

# Stage-1 training of the Unet
unet = begin_training(savedir, stage=1, xtrain=xtrain, ytrain=ytrain, xvalid=xvalid, yvalid=yvalid, unet=unet, batch_size=30, n_epochs=config_dict['n_epochs'], save_format=model_fmt)

# Generate predictions for evaluation
pred_xarray, predictions_metadata = make_predictions(uarr, unet, config_dict, config_path, predictions_metadata, stage=1)
# Save the xarray to a file
pred_xarray.to_netcdf(f"{savedir}predictions.nc")

print('Done with stage 1')
if config_dict['stage_2'] == False:
    exit(0)

##################################################################
# Stage-2 training
## Load stage-2 data sets

# Load the input netcdf file
uarr = uarray(inputfiles, is_input_set=True)
# Get the years
years = uarr._get_years()
# Prepare the input files
xtrain, ytrain, predictions_metadata = rf.prepare_input(uarr, config_path, predictions_metadata, config_dict['split_year'], stage=2)
# Split into training and validation sets
xtrain, ytrain, xvalid, yvalid = data_split(xtrain, ytrain, config_dict['split_value'])
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
unet = begin_training(savedir, stage=2, xtrain=xtrain, ytrain=ytrain, xvalid=xvalid, yvalid=yvalid, unet=unet, batch_size=30, n_epochs=config_dict['n_epochs'], save_format=model_fmt)

# Generate predictions for evaluation
pred_xarray_s2, predictions_metadata = make_predictions(uarr, unet, config_dict, config_path, predictions_metadata, stage=2)

# Create a new variable name and long name
pred_var = f"{uarr.xr.attrs['y_var']}_pred_s2"
# Add the stage 2 predictions to the stage 1 xarray
pred_xarray[pred_var] = pred_xarray_s2[pred_var]
# Merge the stage 2 predictions into the stage 1 xarray
# pred_xarray.merge(pred_xarray_s2)
# Copy over the attributes for the latitude and longitude
# for coord in ['lat', 'lon']:
#     for this_attr in data_for_year[coord].attrs.keys():
#         pred_xarray[coord].attrs[this_attr] = data_for_year[coord].attrs[this_attr]
# Add global attributes for the prediction file
pred_xarray.attrs['modification_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
# Copy over global attributes from the input xarray
for this_attr in uarr.xr.attrs.keys():
    if this_attr in ['stages']:
        pred_xarray.attrs[this_attr] = [1,2]
# Save the xarray to a file
pred_xarray.to_netcdf(f"{savedir}predictions.nc")


# Save the output metadata dictionary to file
print('predictions_metadata:', predictions_metadata)
import json
with open(f"{savedir}predictions_metadata.json", 'w') as file:
    file.write(json.dumps(predictions_metadata, indent=4))

print("===== End run_model.py =====")
print("")


