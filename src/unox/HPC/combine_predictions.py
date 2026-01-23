import sys
import os
import json
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
print('\targv[1], jobname:    ', jobname)

# Load second input argument, if it exists: the config file to use
try:
    config_file = sys.argv[2]
except:
    config_file = 'sample_config'
print('\targv[2], config_file:', config_file)
# Load config file to a dictionary
with open(f"inputfiles/_input_configs/{config_file}.json", 'r') as file:
    config_dict = json.load(file)

# Load third input argument, if it exists: the type of set of runs to do
try:
    run_type = int(sys.argv[3])
except:
    run_type = 'test'
print('\targv[3], run_type:   ', run_type)
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
ens_size_file = verify_path(f"{savedir}ENSEMBLE_SIZE.txt")
# Read in the ensemble size
with open(ens_size_file, 'r') as file:
    ens_size = int(file.read().strip())

# Make a list of blank dictionaries for each ensemble member
ens_dicts = [{} for _ in range(ens_size)]

# Check that all ensemble members exist
for i in range(1, ens_size + 1):
    # Verify the directory for this ensemble member exists
    ens_dicts[i-1]['member_dir'] = verify_path(f"{savedir}{i:02d}_{jobname}/")
    # Verify the predictions file exists
    ens_dicts[i-1]['pred_file'] = verify_path(f"{ens_dicts[i-1]['member_dir']}predictions.nc")
    # Verify the input configuration file exists
    ens_dicts[i-1]['input_config'] = verify_path(f"{ens_dicts[i-1]['member_dir']}input_config.json")
    # Verify the output metadata file exists
    ens_dicts[i-1]['output_metadata'] = verify_path(f"{ens_dicts[i-1]['member_dir']}output_metadata.json")

# Verify that all the input configuration files are the same
## Load the first input configuration file
with open(ens_dicts[0]['input_config'], 'r') as file:
    base_input_config = json.load(file)
for i in range(1, ens_size):
    # Load the input configuration file for this ensemble member
    with open(ens_dicts[i]['input_config'], 'r') as file:
        this_input_config = json.load(file)
    # Compare to the base input configuration
    if this_input_config != base_input_config:
        raise ValueError(f"Input configuration file for ensemble member {i+1} does not match that of member 1.")
print(f"All `input_config.json` files match across the {ens_size} ensemble members.")

# -------- Combine the predictions --------

print("===== End combine_predictions.py =====")
print("")