from unox.HPC.data0.dataset import uarray
from unox.HPC.data0.paths import verify_path, remove_non_empty_directory, make_file_path
from unox.plotting import plot_var_maps

import proplot as pplt

# Print the current working directory to verify the path to the data files
import os
print(f"Current working directory: {os.getcwd()}")

# Get the example input dataset
no2_2019_JFM = uarray('no2_2019_JFM', is_input_set=True)

output_dir = 'docs/docs_dev/model_diagram/plots'
# Check to see whether a directory exists for the plots
try:
    verify_path(output_dir)
    # Ask whether to remove the existing directory
    response = input(f"The directory {output_dir} already exists. Do you want to remove it and create a new one? (y/n): ")
    if response.lower() == 'y':
        remove_non_empty_directory(output_dir)
        make_file_path(output_dir)
    else:
        print(f"Aborting script. Please choose a different output directory or remove the existing one.")
        exit()
except:
    # If not, create the directory
    make_file_path(output_dir)

# Get a list of all the variables in the dataset
var_list = list(no2_2019_JFM.xr.data_vars.keys())
print(f"Variables in the dataset: {var_list}")

# Generate a plot for each variable in the dataset
for var in var_list:
    var_plots = plot_var_maps(
        no2_2019_JFM,
        vars=var,
        start_date='2019-01-01',
        interval='1D',
        add_title=False,
        add_clrbar=False,
        padding=0,
    )
    # To turn off the a-b-c labels, set `pplt.rc.abc` to `False` in `plotting.py`
    # Save the plot to a file
    var_plots.savefig(f'{output_dir}/no2_2019_JFM_{var}_plot.png', transparent=True, bbox_inches='tight', pad_inches=0)