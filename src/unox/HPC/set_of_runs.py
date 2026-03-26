import sys
import os
import json

# -------- Get input arguments --------print("")
print("===== Begin set_of_runs.py =====")
print('Given input arguments:')
# Load first input argument, if it exists: the job name
try:
    jobname = sys.argv[1]
except:
    jobname = 'test_set_of_runs'
savedir = f"HPC_runs/_{jobname}/"
print('\targv[1], jobname:', jobname)

# Load second input argument, if it exists: the config file to use
try:
    config_file = sys.argv[2]
except:
    config_file = 'sample_config'
print('\targv[2], config_file:', config_file)
# Load config file to a dictionary
with open(f"model_configs/{config_file}.json", 'r') as file:
    config_dict = json.load(file)

# Load third input argument, if it exists: the type of set of runs to do
try:
    run_type = int(sys.argv[3])
except:
    run_type = 'zfi_set'
print('\targv[3], run_type:', run_type)
# Modify the config dictionary based on the run type
if run_type == 'zfi_set':
    # Remove any `lsm_vars` entry
    if 'lsm_vars' in config_dict:
        del config_dict['lsm_vars']
    # Remove any `zfi_var` entry
    if 'zfi_vars' in config_dict:
        del config_dict['zfi_vars']

# -------- Create the directories --------

try:
    os.mkdir(savedir)
except FileExistsError:
    print(savedir+' exists')

def create_run_sub_dir(
    savedir,
    jobname,
    x_vars,
    run_type,
    config_dict,
):
    """ Create a subdirectory given the set of parameters.

        Make a subdirectory for a run in a set of runs specified by the jobname and create the appropriate configuration file for that run.

        Parameters
        ----------
        savedir : `str`
            The base directory in which to create the subdirectory.
        jobname : `str`
            The name of the job / set of runs.
        x_vars : `list`
            The list of x variables to consider for this run
        run_type : `str`
            The type of set of runs to do.
            Example: 'zfi_set' for a set of runs to test Zeroed Feature Importance.
        config_dict : `dict`
            The configuration dictionary to modify for this run.
    """
    # Assemble the subdirectory path
    if len(x_vars) > 1:
        sub_run_name = "_".join(x_vars)
    elif len(x_vars) == 1:
        sub_run_name = x_vars[0]
    this_sub_dir = f"{savedir}{jobname}_{sub_run_name}/"
    # Check whether that subdirectory exists; if not, create it
    try:
        os.mkdir(this_sub_dir)
    except:
        print(f"{this_sub_dir} exists")
    # Make a copy of the config dictionary
    this_config_dict = config_dict.copy()
    # Modify this config dictionary for this x variable
    if run_type == 'zfi_set':
        this_config_dict['zfi_vars'] = x_vars
    # Check whether the input_config.json file already exists in this subdirectory
    this_input_config = f"{this_sub_dir}input_config.json"
    if os.path.exists(this_input_config):
        print(f"Warning: {this_sub_dir} already exists. Overwriting.")
    # Save a copy of the config file in the subdirectory
    with open(this_input_config, 'w') as file:
        json.dump(this_config_dict, file, indent=4)

# Make a subdirectory and copy of the config file when no variables are zeroed
create_run_sub_dir(
    savedir,
    jobname,
    ['none'],
    run_type,
    config_dict,
)
# Get the list of x variables from the config dictionary
x_vars = config_dict['x_vars']
# For each x variable, make a subdirectory and copy of the config file
for x_var in x_vars:
    create_run_sub_dir(
        savedir,
        jobname,
        [x_var],
        run_type,
        config_dict,
    )
# Make subdirectories for pairs of variables
var_pairs = [
    ['no2', 'no2_tm1'],
    ['ssrd', 'sp'],
    ['u10', 'v10'],
]
for var_pair in var_pairs:
    if var_pair[0] in x_vars and var_pair[1] in x_vars:
        create_run_sub_dir(
            savedir,
            jobname,
            [var_pair[0], var_pair[1]],
            run_type,
            config_dict,
        )

print("===== End set_of_runs.py =====")
print("")