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
# Load first input argument, if it exists: the job name
try:
    jobname = sys.argv[1]
except:
    jobname = 'test_set_of_runs'
# Get just the part of the job name after the last slash
jobname_suffix = jobname.rsplit('/')[-1]
print(f"\targv[1], jobname:    {jobname} ({jobname_suffix})")

# Load second input argument, if it exists: the config file to use
try:
    config_file = sys.argv[2]
except:
    config_file = 'sample_config'
print(f"\targv[2], config_file: {config_file}")
# Load config file to a dictionary
with open(f"inputfiles/_input_configs/{config_file}.json", 'r') as file:
    config_dict = json.load(file)

# Load third input argument, if it exists: the type of set of runs to do
try:
    run_type = int(sys.argv[3])
except:
    run_type = 'test'
print(f"\targv[3], run_type:   {run_type}")
# Modify the config dictionary based on the run type
if run_type == 'zfi_set':
    # Remove any `lsm_vars` entry
    if 'lsm_vars' in config_dict:
        del config_dict['lsm_vars']
    # Remove any `zfi_var` entry
    if 'zfi_vars' in config_dict:
        del config_dict['zfi_vars']
    savedir = f"HPC_runs/_{jobname}/"
else:
    savedir = f"HPC_runs/{jobname}/"

# -------- Check the directories --------

# Find the ensemble size file in the savedir
ens_size_file = verify_path(f"{savedir}ENSEMBLE_SIZE.sh")
# Read in the ensemble size
with open(ens_size_file, 'r') as file:
    ens_size = int(file.read().strip())

# Make a list of blank dictionaries for each ensemble member
ens_dicts = [{} for _ in range(ens_size)]

# Check that all ensemble members exist
for i in range(1, ens_size + 1):
    # Verify the directory for this ensemble member exists
    ens_dicts[i-1]['member_dir'] = verify_path(f"{savedir}{i:02d}_{jobname_suffix}/")
    # Verify the predictions file exists
    ens_dicts[i-1]['pred_file'] = verify_path(f"{ens_dicts[i-1]['member_dir']}predictions.nc")
    # Verify the input configuration file exists
    ens_dicts[i-1]['input_config'] = verify_path(f"{ens_dicts[i-1]['member_dir']}input_config.json")
    # Verify the output metadata file exists
    ens_dicts[i-1]['output_metadata'] = verify_path(f"{ens_dicts[i-1]['member_dir']}output_metadata.json")

# Compare the input configuration and output metadata files across all ensemble members
## Load those files for the first ensemble member
with open(ens_dicts[0]['input_config'], 'r') as file:
    base_input_config = json.load(file)
with open(ens_dicts[0]['output_metadata'], 'r') as file:
    base_output_metadata = json.load(file)
    # Get the name of the `savedir` entry
    base_savedir = base_output_metadata['savedir']
    # Remove the child directory from that path
    base_output_metadata['savedir'] = f"{os.path.dirname(base_savedir.rstrip('/'))}/"
    # Get just the child directory name, skipping the first three characters as those will be
    # a 2-digit number and an underscore
    base_child_dir = os.path.basename(base_savedir.rstrip('/'))[3:]
for i in range(1, ens_size):
    # Load the input configuration file for this ensemble member
    with open(ens_dicts[i]['input_config'], 'r') as file:
        this_input_config = json.load(file)
    # Compare to the base input configuration
    if this_input_config != base_input_config:
        raise ValueError(f"Input configuration file for ensemble member {i+1} does not match that of member 1.")
    # Load the output metadata file for this ensemble member
    with open(ens_dicts[i]['output_metadata'], 'r') as file:
        this_output_metadata = json.load(file)
        # Get the name of the `savedir` entry
        this_savedir = this_output_metadata['savedir']
        # Remove the child directory from that path
        this_output_metadata['savedir'] = f"{os.path.dirname(this_savedir.rstrip('/'))}/"
        # Get just the child directory name, skipping the first three characters as those will be
        # a 2-digit number and an underscore
        this_child_dir = os.path.basename(this_savedir.rstrip('/'))[3:]
    # Compare to the base output metadata, excluding the `savedir` entry
    if this_output_metadata != base_output_metadata:
        raise ValueError(f"Output metadata file for ensemble member {i+1} does not match that of member 1.")
    # Compare the child directory names, skipping the first three characters as those will be 
    # a 2-digit number and an underscore
    if this_child_dir != base_child_dir:
        raise ValueError(f"The child directory in the `savedir` entry in output metadata file for ensemble member {i+1} does not match that of member 1.\n\tMember 1: {base_savedir}\n\tMember {i+1}: {this_savedir}")
# Save the input configuration file from the first ensemble member to the base directory
print(f"All `input_config.json` files match across the {ens_size} ensemble members.")
print(f"\tSaving `input_config.json` to {savedir}")
with open(f"{savedir}input_config.json", 'w') as file:
    json.dump(base_input_config, file, indent=4)
# Save the output metadata file from the first ensemble member to the base directory
print(f"All `output_metadata.json` files match across the {ens_size} ensemble members.")
print(f"\tSaving `output_metadata.json` to {savedir}")
with open(f"{savedir}output_metadata.json", 'w') as file:
    json.dump(base_output_metadata, file, indent=4)

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

print("===== End combine_predictions.py =====")
print("")