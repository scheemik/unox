import sys
import os
import json
import xarray as xr
import pandas as pd

from data0.paths import verify_path

# -------- Get input arguments --------
print("===== Begin combine_predictions.py =====")
print(f"Current working directory: {os.getcwd()}")
print('Given input arguments:')
# Load first input argument, and make sure it exists: the job name
try:
    jobname = sys.argv[1]
except:
    raise ValueError(f"(combine_predictions) `sys.argv[1]` must be the job name, but none was provided.")
# Remove any leading or trailing slashes from the job name
jobname = jobname.strip('/')
# Get just the part of the job name after the last slash
jobname_suffix = jobname.rsplit('/')[-1]
print(f"\targv[1], jobname:    {jobname} ({jobname_suffix})")
# Assemble the save directory
savedir = f"HPC_runs/{jobname}/"
# Verify the save directory exists
savedir = verify_path(savedir)
print(f"\t         savedir:    {savedir}")

# -------- Check the directories --------

# Find the ensemble size file in the savedir
ens_size_file = verify_path(f"{savedir}ENSEMBLE_SIZE.txt")
# Read in the ensemble size
with open(ens_size_file, 'r') as file:
    ens_size = int(file.read().strip())

# Make a list of blank dictionaries for each ensemble member
ens_dicts = [{} for _ in range(ens_size)]

# Check that all ensemble members exist
for i in range(1, ens_size + 1):
    # Assemble the path to the directory for this ensemble member
    ens_mem_dir = f"{savedir}{i:02d}_{jobname_suffix}/"
    # Verify the directory for this ensemble member exists
    ens_dicts[i-1]['member_dir'] = verify_path(ens_mem_dir)
    # Verify the predictions file exists
    ens_dicts[i-1]['pred_file'] = verify_path(f"{ens_mem_dir}predictions.nc")
    # Verify the input configuration file exists
    ens_dicts[i-1]['model_config'] = verify_path(f"{ens_mem_dir}model_config.json")
    # Verify the output metadata file exists
    ens_dicts[i-1]['predictions_metadata'] = verify_path(f"{ens_mem_dir}predictions_metadata.json")

# Compare the input configuration and output metadata files across all ensemble members
## Load those files for the first ensemble member
with open(ens_dicts[0]['model_config'], 'r') as file:
    base_model_config = json.load(file)
with open(ens_dicts[0]['predictions_metadata'], 'r') as file:
    base_predictions_metadata = json.load(file)
    # Get the name of the `savedir` entry
    base_savedir = base_predictions_metadata['savedir']
    # Remove the child directory from that path
    base_predictions_metadata['savedir'] = f"{os.path.dirname(base_savedir.rstrip('/'))}/"
    # Get just the child directory name, skipping the first three characters as those will be
    # a 2-digit number and an underscore
    base_child_dir = os.path.basename(base_savedir.rstrip('/'))[3:]
    # Set `config_path` to parent directory to not be specific to one ensemble member
    base_predictions_metadata['config_path'] = f"{base_predictions_metadata['savedir']}model_config.json"
for i in range(1, ens_size):
    # Load the input configuration file for this ensemble member
    with open(ens_dicts[i]['model_config'], 'r') as file:
        this_model_config = json.load(file)
    # Compare to the base input configuration
    if this_model_config != base_model_config:
        raise ValueError(f"Input configuration file for ensemble member {i+1} does not match that of member 1.")
    # Load the output metadata file for this ensemble member
    with open(ens_dicts[i]['predictions_metadata'], 'r') as file:
        this_predictions_metadata = json.load(file)
        # Get the name of the `savedir` entry
        this_savedir = this_predictions_metadata['savedir']
        # Remove the child directory from that path
        this_predictions_metadata['savedir'] = f"{os.path.dirname(this_savedir.rstrip('/'))}/"
        # Get just the child directory name, skipping the first three characters as those will be
        # a 2-digit number and an underscore
        this_child_dir = os.path.basename(this_savedir.rstrip('/'))[3:]
        # Set `config_path` to parent directory to not be specific to one ensemble member
        this_predictions_metadata['config_path'] = f"{this_predictions_metadata['savedir']}model_config.json"
    if this_predictions_metadata != base_predictions_metadata:
        raise ValueError(f"Output metadata file for ensemble member {i+1} does not match that of member 1.")
    # Compare the child directory names, skipping the first three characters as those will be 
    # a 2-digit number and an underscore
    if this_child_dir != base_child_dir:
        raise ValueError(f"The child directory in the `savedir` entry in output metadata file for ensemble member {i+1} does not match that of member 1.\n\tMember 1: {base_savedir}\n\tMember {i+1}: {this_savedir}")
# Save the input configuration file from the first ensemble member to the base directory
print(f"All `model_config.json` files match across the {ens_size} ensemble members.")
print(f"\tSaving `model_config.json` to {savedir}")
with open(f"{savedir}model_config.json", 'w') as file:
    json.dump(base_model_config, file, indent=4)
# Save the output metadata file from the first ensemble member to the base directory
print(f"All `predictions_metadata.json` files match across the {ens_size} ensemble members.")
print(f"\tSaving `predictions_metadata.json` to {savedir}")
with open(f"{savedir}predictions_metadata.json", 'w') as file:
    json.dump(base_predictions_metadata, file, indent=4)

# -------- Combine the predictions --------

# Load the predictions from each ensemble member and combine them into a single xarray Dataset
print(f"Combining predictions from {ens_size} ensemble members...")

# Loop over each ensemble member
prediction_arrays = []
for i in range(ens_size):
    # Load the predictions from each ensemble member
    prediction_arrays.append(xr.open_dataset(ens_dicts[i]['pred_file']))
    # Get a list of the prediction variables, if the first ensemble member
    if i == 0:
        pred_vars = list(prediction_arrays[0].data_vars)
    # Append the ensemble number to each data variable name
    for j in range(len(pred_vars)):
        prediction_arrays[i] = prediction_arrays[i].rename({f"{pred_vars[j]}": f"{pred_vars[j]}_{i+1:02d}"})
# Combine all prediction arrays for each ensemble member into one xarray Dataset
combined_predictions = xr.merge(prediction_arrays)
# Update the attributes of the combined predictions Dataset
combined_predictions.attrs['modification_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
combined_predictions.attrs['ensemble_size'] = ens_size

# Save the xarray to a file
combined_predictions.to_netcdf(f"{savedir}predictions.nc")

# Delete the `predictions.nc` files for each individual ensemble member
for i in range(ens_size):
    # Get the name of the file to delete
    pred_file_to_delete = verify_path(ens_dicts[i]['pred_file'])
    # Delete that file
    print(f"\tRemoving redundant file: {pred_file_to_delete}")
    os.remove(pred_file_to_delete)

print("===== End combine_predictions.py =====")
print("")