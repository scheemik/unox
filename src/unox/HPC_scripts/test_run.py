#test code based on Unet_Chinese_NOx example_code.ipynb
import numpy as np
import glob
import sys
import os 
import xarray as xr
from utils.load_input import get_npy_from_netcdf

print('')
print(f'Running test_run.py from current working directory:{os.getcwd()}')

# Load first input argument, if it exists: the save directory
try:
    savedir = sys.argv[1] + '/'
except:
    savedir = 'HPC_runs/test_unet/'  #directory to save output in
print('Running python script with savedir:', savedir)

# Load second input argument, if it exists: the input files to use
try:
    inputfiles = sys.argv[2]
except:
    inputfiles = 'no2_sample_input'
print('Running python script with inputfiles:', inputfiles)

# Load third input argument, if it exists: the version of the code to use
try:
    version = int(sys.argv[3])
except:
    version = 1
print('Running python script with version:', version)

try:
    os.mkdir(savedir)
except FileExistsError:
    print(savedir+' exists')

try:
    os.mkdir(savedir+'stage1_output/')
except FileExistsError:
    print('stage1_output/ exists')
try:
    os.mkdir(savedir+'stage2_output/')
except FileExistsError:
    print('stage2_output/ exists')
try:
    os.mkdir(savedir+'checkpts/')
except FileExistsError:
    print('checkpts/ exists')

n_epochs = 250
save_fmt = 'both' # 'h5', 'keras', or 'both'
input_fmt = 'nc' # 'nc' or 'npy'
split_year = 2019
split_value = 0.9

##################################################################
from utils.data_split import data_split
##################################################################
# Stage-1 training
## Load stage-1 data sets

def load_input_files(
    inputfiles, 
    stage,
    ):
    """Load input files for a given stage.

    Parameters
    ----------
    inputfiles : str
        The directory containing the input files.
    stage : int
        The stage number (1 or 2).

    Returns
    -------
    x_files : list
        List of input feature files.
    y_files : list
        List of target variable files.
    """
    # Assemble the file paths
    x_files_path = f'inputfiles/{inputfiles}/stage{stage}/x/'
    y_files_path = f'inputfiles/{inputfiles}/stage{stage}/y/'
    # Ensure the directories exist
    if not os.path.exists(x_files_path):
        raise FileNotFoundError(f"Directory not found: {x_files_path}")
    if not os.path.exists(y_files_path):
        raise FileNotFoundError(f"Directory not found: {y_files_path}")
    # Load and sort the files
    x_files = sorted(glob.glob(f'inputfiles/{inputfiles}/stage{stage}/x/X_20*.npy'))
    y_files = sorted(glob.glob(f'inputfiles/{inputfiles}/stage{stage}/y/Y_20*.npy'))
    print('')
    print(f'Number of x_files: {len(x_files)}')
    print(f'Number of y_files: {len(y_files)}')
    return x_files, y_files

def split_input_files(
    x_files,
    y_files,
    stage,
    split_value=0.9,
    ):
    """Split input files into training and validation sets.

    Parameters
    ----------
    x_files : list
        List of input feature files.
    y_files : list
        List of target variable files.
    stage : int
        The stage number (1 or 2).
    split_value : float, optional
        Proportion of files to use for training.
    
    Returns
    -------
    xtrain : np.ndarray
        Concatenated training input features.
    ytrain : np.ndarray
        Concatenated training target variables.
    xvalid : np.ndarray
        Concatenated validation input features.
    yvalid : np.ndarray
        Concatenated validation target variables.
    """
    # Decide on split index based on stage
    if stage == 1:
        split_index = 14
    elif stage == 2:
        split_index = 5
    else:
        raise ValueError("Stage must be 1 or 2.")
    # Gather just the training files
    xtrain_files, ytrain_files = x_files[:split_index], y_files[:split_index]
    print('')
    print(f'Shape of first xtrain file: {np.load(xtrain_files[0]).shape}')
    print(f'Shape of first ytrain file: {np.load(ytrain_files[0]).shape}')
    # Concatenate training data
    xtrain = np.concatenate([ np.load(s) for s in xtrain_files], axis=0)
    ytrain = np.concatenate([ np.load(s) for s in ytrain_files], axis=0)
    print('After concatenation:')
    print(f'Shape of xtrain: {xtrain.shape}')
    print(f'Shape of ytrain: {ytrain.shape}')
    # Split into training and validation sets
    xtrain, ytrain, xvalid, yvalid = data_split(xtrain, ytrain, split_value)
    print('After data split:')
    print(f'Shape of xtrain: {xtrain.shape}')
    print(f'Shape of ytrain: {ytrain.shape}')
    print(f'Shape of xvalid: {xvalid.shape}')
    print(f'Shape of yvalid: {yvalid.shape}')
    return xtrain, ytrain, xvalid, yvalid

if input_fmt == 'npy':
    x_files, y_files = load_input_files(inputfiles, stage=1)
    xtrain, ytrain, xvalid, yvalid = split_input_files(x_files, y_files, stage=1, split_value=0.9)
elif input_fmt == 'nc':
    # Assemble the file path to the netcdf
    netcdf_path = f'inputfiles/{inputfiles}/{inputfiles}.nc'
    # Ensure the netcdf file exists
    if not os.path.exists(netcdf_path):
        raise FileNotFoundError(f"NetCDF file not found: {netcdf_path}")
    # Load the netcdf file
    input_ds = xr.open_dataset(netcdf_path)
    print(f'Finished loading: {netcdf_path}')
    # Get list of years present in the `from_xr` netcdf
    years = input_ds['time'].dt.year.values
    years = sorted(list(set(years)))
    xtrain_list = []
    ytrain_list = []
    # If before the split year, add x and y data to train lists
    for year in range(min(years), split_year):
        xtrain_list.append(get_npy_from_netcdf(input_ds, year, x_or_y='x'))
        ytrain_list.append(get_npy_from_netcdf(input_ds, year, x_or_y='y'))
    print(f'Shape of first xtrain file: {xtrain_list[0].shape}')
    print(f'Shape of first ytrain file: {ytrain_list[0].shape}')
    # Concatenate training data
    xtrain = np.concatenate(xtrain_list, axis=0)
    ytrain = np.concatenate(ytrain_list, axis=0)
    print('After concatenation:')
    print(f'Shape of xtrain: {xtrain.shape}')
    print(f'Shape of ytrain: {ytrain.shape}')
    # Split into training and validation sets
    xtrain, ytrain, xvalid, yvalid = data_split(xtrain, ytrain, split_value)
    print('After data split:')
    print(f'Shape of xtrain: {xtrain.shape}')
    print(f'Shape of ytrain: {ytrain.shape}')
    print(f'Shape of xvalid: {xvalid.shape}')
    print(f'Shape of yvalid: {yvalid.shape}')

print('Done loading data sets for stage 1')
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
        raise ValueError("Stage must be 1 or 2.")
    # Set up callbacks
    csv_logger = CSVLogger( savedir+f'unet_stage{stage}_log.csv', append=True, separator=';')
    earlystopper = EarlyStopping(patience=15, verbose=1)
    checkpointer = ModelCheckpoint(savedir+f'checkpts/unet_checkpt_{{val_loss:.2f}}_{{r2_keras:.2f}}_stage{stage}.h5', verbose=1, save_best_only=True)
    print('')
    print(f'Begin training stage {stage}')
    unet.train(xtrain, ytrain, validation_data=(xvalid, yvalid), batch_size=batch_size, epochs=n_epochs, callbacks=[earlystopper, checkpointer, csv_logger], shuffle=True)
    # Save model weights
    if save_format in ['h5', 'both']:
        unet.save_model(savedir+f'unet_stage{stage}_model.h5')
    if save_format in ['keras', 'both']:
        unet.save_model(savedir+f'unet_stage{stage}_model.keras')
    return unet

unet = begin_training(savedir, stage=1, xtrain=xtrain, ytrain=ytrain, xvalid=xvalid, yvalid=yvalid, unet=unet, batch_size=30, n_epochs=n_epochs, save_format=save_fmt)

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
        raise ValueError("Stage must be 1 or 2.")
    # Gather just the testing files
    xtest_files = x_files[split_index:]
    print('')
    print(f'Number of xtest_files: {len(xtest_files)}')
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
        np.save(savedir+f'stage{kwargs["stage"]}_output/pred_' + x.split('/')[-1], pred)

if input_fmt == 'npy':
    predict_and_save(savedir, unet, x_files=x_files, stage=1)
elif input_fmt == 'nc':
    # Make predictions based on x data for years >= split_year
    for year in range(split_year, max(years)+1):
        print(f'Generating predictions for year: {year}')
        x_test = get_npy_from_netcdf(input_ds, year, x_or_y='x')
        pred = unet.predict(x_test)
        np.save(savedir+f'stage1_output/pred_X_{year}.npy', pred)

# xtest_files = x_files[14:]
# 
# ### Predict using Unet
# for x in xtest_files:
#     xnow = np.load(x)#[:,:,:,:9]
#     pred = unet.predict(xnow)
#     np.save(savedir+'stage1_output/pred_' + x.split('/')[-1], pred)

#for y in y_files[14:]:
#    ynow = np.load(y)
#    pred = unet.predict(ynow)
#    np.save(savedir+'stage1_output/ypred_' + y.split('/')[-1], pred)

print('Done with stage 1')
exit(0)

##################################################################
# Stage-2 training
## Load stage-2 data sets

# x_files = sorted(glob.glob(f'inputfiles/{inputfiles}/stage2/x/X_20*.npy'))
# y_files = sorted(glob.glob(f'inputfiles/{inputfiles}/stage2/y/Y_20*.npy'))
x_files, y_files = load_input_files(inputfiles, stage=2)
# print(x_files, y_files)
# xtrain_files, ytrain_files = x_files[:5], y_files[:5]
# xtrain = np.concatenate([ np.load(s) for s in xtrain_files], axis=0)
# #xtrain = xtrain[:,:,:,:9] #definitely not the right way to make the data the right size
# 
# ytrain = np.concatenate([ np.load(s) for s in ytrain_files], axis=0)
# # print(xtrain.shape, ytrain.shape)
# 
# # split into training, validation, and test sets
# xtrain, ytrain, xvalid, yvalid = data_split(xtrain, ytrain, 0.9)
# print(xtrain.shape, ytrain.shape, xvalid.shape, yvalid.shape)

x_train, y_train, x_valid, y_valid = split_input_files(x_files, y_files, stage=2, split_value=0.9)

# # Load the stage-1 model weights to the U-net model
# unet.load_weights(savedir+'unet_stage1_model.h5')


# Load the pre-trained model from stage-1
if save_fmt in ['keras', 'both']:
    unet.load_weights(f'{savedir}unet_stage1_model.keras')
elif save_fmt in ['h5']:
    unet.load_weights(f'{savedir}unet_stage1_model.h5')
else:
    raise ValueError(f"save_fmt must be 'h5', 'keras', or 'both', got {save_fmt}")


# Stage-2 training of the Unet
# csv_logger = CSVLogger( savedir+'unet_stage2_log.csv', append=True, separator=';')
# earlystopper = EarlyStopping(patience=15, verbose=1)
# checkpointer = ModelCheckpoint(savedir+'checkpts/unet_checkpt_{val_loss:.2f}_{r2_keras:.2f}_stage2.h5', verbose=1, save_best_only=True)
# 
# print('begin training stage 2')
# unet.train(xtrain, ytrain, validation_data=(xvalid, yvalid), 
#            batch_size=30, epochs=n_epochs, callbacks=[earlystopper, checkpointer, csv_logger], shuffle=True)
# 
# # Save stage-2 model weights
# unet.save_model(savedir+'unet_stage2_model.h5')
# unet.save_model(savedir+'unet_stage2_model.keras')


unet = begin_training(savedir, stage=2, xtrain=x_train, ytrain=y_train, xvalid=x_valid, yvalid=y_valid, unet=unet, batch_size=30, n_epochs=n_epochs, save_format=save_fmt)


# Generate predictions for evaluation
### Load testing data sets
# xtest_files = x_files[5:]
# print(xtest_files)
# 
# ### Predict using Unet
# for x in xtest_files:
#     xnow = np.load(x)#[:,:,:,:9]
#     pred = unet.predict(xnow)
#     np.save(savedir+'stage2_output/pred_' + x.split('/')[-1], pred)

#for y in y_files[14:]:
#    ynow = np.load(y)
#    pred = unet.predict(ynow)
#    np.save(savedir+'stage2_output/ypred_' + y.split('/')[-1], pred)

predict_and_save(savedir, unet, x_files=x_files, stage=2)

print('')
print('Done running test_unet.py')





