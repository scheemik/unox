import numpy as np
import multiprocessing as mp
import logging
import sys
import os
import glob

# -------- Get input arguments --------
# Load first input argument, if it exists: the save directory
try:
    savedir = sys.argv[1] + '/'
except:
    savedir = 'HPC_runs/test_unet/'
print('Running python script with savedir:', savedir)
# Load second input argument, if it exists: the input files to use
try:
    inputfiles = sys.argv[2]
except:
    inputfiles = 'no2_sample_input'
print('Running python script with inputfiles:', inputfiles)
# Load third input argument, if it exists: the number of samples to use
try:
    num_samples = int(sys.argv[3])
    if num_samples == 1:
        num_samples = 'all'
except:
    num_samples = 'all'
print('Running python script with num_samples:', num_samples)

this_year = 2019
this_stage = 1

try:
    os.mkdir(savedir)
except FileExistsError:
    print(savedir+' exists')

# -------- Logging setup --------
def setup_logging(log_filename):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    # Log to file
    fh = logging.FileHandler(log_filename)
    fh.setLevel(logging.INFO)
    # Log to stdout
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger

# --------- Prediction worker function --------
def predict_for_cell(args):
    ilat, ilon, lat_size, lon_size, num_vars, background_sub, x_test_sub, model_weights_path = args
    # Import inside process
    from keras.models import load_model
    from utils import functions
    model = load_model(model_weights_path)
    x_test_cell = x_test_sub[:, ilat, ilon, :]  # (num_samples, 9)
    num_samples = x_test_cell.shape[0]
    # Build full input for each sample, with only this cell set
    X_full = np.zeros((num_samples, lat_size, lon_size, num_vars), dtype=x_test_cell.dtype)
    X_full[:, ilat, ilon, :] = x_test_cell
    preds = model.predict(X_full)  # (num_samples, lat, lon, 1)
    preds_cell = preds[:, ilat, ilon, 0]  # (num_samples,)
    logging.info(f"Completed prediction for cell ({ilat}, {ilon})")
    return (ilat, ilon, preds_cell)

# --------- Main script ---------
if __name__ == "__main__":
    # Parameters (set these as needed)
    num_workers = int(os.environ.get('SLURM_CPUS_PER_TASK', default=1))      # Number of worker processes (set to CPU count or cluster limit)
    num_workers = 192 # the number of available workers per CPU node on Trillium
    print('Using num_workers:', num_workers)
    log_file = f"{savedir}predict_parallel.log"
    predict_output_file = f"{savedir}stage{this_stage}_output/grid_pred_X_{this_year}.npy"
    model_weights_path = f"{savedir}unet_stage{this_stage}_model.keras"  # Path to your saved Keras model

    # Setup logging
    logger = setup_logging(log_file)
    logger.info("Starting prediction parallel calculation with multiprocessing...")
    # Print file paths for debugging
    logger.info(f"Log file: {log_file}")
    logger.info(f"Prediction output file: {predict_output_file}")
    logger.info(f"Model weights path: {model_weights_path}")

    # Prepare your data here (replace these with your actual arrays)
    x_files = sorted(glob.glob(f'inputfiles/{inputfiles}/stage1/x/X_20*.npy'))
    # xtrain_files = x_files[:14]
    # xtrain = np.concatenate([ np.load(s) for s in xtrain_files], axis=0)
    x_test_files = x_files[14:]
    if this_year == 2019:
        x_test = np.load(x_test_files[0])
    elif this_year == 2020:
        x_test = np.load(x_test_files[1])
    logger.info(f"x_test shape: {x_test.shape}")
    if num_samples == 'all' or num_samples > x_test.shape[0]:
        num_samples = x_test.shape[0]
    background = x_test[:num_samples]
    logger.info(f"Background shape: {background.shape}")
    # Save and reload model to disk to avoid TF multiprocessing bugs
    # from tensorflow.keras.models import save_model
    # save_model(this_model2, model_weights_path)
    # logger.info("Model saved to disk for multiprocessing workers.")

    # Load dimensions
    lat_size, lon_size, num_vars = x_test.shape[1:4]
    x_test_sub = x_test[:num_samples]
    background_sub = None

    # Prepare argument list for workers
    worker_args = [
        (ilat, ilon, lat_size, lon_size, num_vars, background_sub, x_test_sub, model_weights_path)
        for ilat in range(lat_size)
        for ilon in range(lon_size)
    ]

    # Pre-allocate output array
    predictions = np.zeros((lat_size, lon_size, num_samples), dtype=np.float32)
    # Parallel prediction
    with mp.Pool(processes=num_workers) as pool:
        for ilat, ilon, preds_cell in pool.imap_unordered(predict_for_cell, worker_args):
            predictions[ilat, ilon, :] = preds_cell
            logger.info(f"Stored predictions for cell ({ilat}, {ilon})")
    # Save results
    np.save(pred_output_file, predictions)
    logger.info(f"All predictions saved to {pred_output_file}")

    

    

    