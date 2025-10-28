"""
Regrid and resample, then concatenate all 12 months of each resampled ERA5 variable for each year. 
Output should be (365,56,120). Or 366 for leap years. Save to netcdf.
"""
# Launch with tmux and pipe the output to a log file:
# $ tmux
# $ conda activate uplt
# $ python datafiles/era5_concatenate.py > datafiles/era5_concatenate_log.txt 2>&1

import numpy as np
import netCDF4 as nc
import xarray as xr
import os
import sys
from unox.unox import load_lats_lons

# Define ERA5 download path
home_dir = os.getenv('HOME')
datafiles_dir = f'{home_dir}/unox/datafiles'
era5_download_dir = f'{datafiles_dir}/era5_downloads'
era5_concatenated_dir = f'{datafiles_dir}/ERA5concatenated'

# Make sure the era5_downloads directory exists
if not os.path.exists(era5_download_dir):
    raise FileNotFoundError(f'ERA5 download directory does not exist: {era5_download_dir}')

# If it does not exist already, make the concatenated output directory
if not os.path.exists(era5_concatenated_dir):
    print(f'Creating directory: {era5_concatenated_dir}')
    os.makedirs(era5_concatenated_dir)

# Get the lats and lons for regridding
lats, lons = load_lats_lons()
# lons = np.load('lons.npy')  #lon and lat grid for Unet
# lats = np.load('lats.npy')

# Get list of directories in the ERA5 download path
era5_dirs = os.listdir(era5_download_dir)
print('era5_dirs:', era5_dirs)
# Loop across each of these directories
for era5_subdir in era5_dirs:
    # If not a directory or the name is not a year, skip it
    if not os.path.isdir(f'{era5_download_dir}/{era5_subdir}') or not era5_subdir.isdigit():
        print(f'Skipping non-year directory: {era5_subdir}')
        continue
    print(f'Processing year directory: {era5_subdir}')
    # Get the list of directories in this year directory
    year_dirs = os.listdir(f'{era5_download_dir}/{era5_subdir}/')
    # Make a blank dictionary to store lists of nc files for each variable
    nc_dict = {}
    # Loop across each of these directories (one per month per variable)
    for mon_dir in year_dirs:
        # If not a directory, skip it
        if not os.path.isdir(f'{era5_download_dir}/{era5_subdir}/{mon_dir}'):
            # print(f'Skipping non-directory: {mon_dir}')
            continue
        # Get the variable name from the directory name
        var_name = mon_dir.split('_')[2]
        # If this variable is not already in the dictionary, add it with an empty list
        if var_name not in nc_dict:
            nc_dict[var_name] = []
        # Get the full path to the nc file inside mon_dir
        temp_list = os.listdir(f'{era5_download_dir}/{era5_subdir}/{mon_dir}/')
        # If there isn't exactly one nc file, print a warning
        if len(temp_list) != 1 or not temp_list[0].endswith('.nc'):
            print(f'\tWarning: Expected one .nc file in {mon_dir}, found: {temp_list}')
            continue
        # Assemble full path to this nc file
        nc_file_path = f'{era5_download_dir}/{era5_subdir}/{mon_dir}/{temp_list[0]}'
        # Make sure that the file exists
        if not os.path.isfile(nc_file_path):
            raise FileNotFoundError(f'File does not exist: {nc_file_path}')
        # Append the file path to the list for this variable
        # The file names are something like "data_stream-oper_stepType-instant.nc"
        nc_dict[var_name].append(nc_file_path)
    # Loop across each variable
    for var in nc_dict:
        print(f'\tProcessing variable: {var} for year {era5_subdir}')
        # Assemble the output filepath
        output_filepath = f'{era5_concatenated_dir}/{era5_subdir}{var}.nc'
        # Check whether the output file already exists
        if os.path.exists(output_filepath):
            print(f'\tOutput file already exists: {output_filepath}. Skipping variable {var}.')
            continue
        datasets = []
        # Loop across each nc file for this variable (should be one per month)
        for nc_file in nc_dict[var]:
            print(f'\tOpening file: {nc_file}')
            data = xr.open_dataset(nc_file)
            # Regrid to coarser spatial resolution, time x 56 lat x 120 lon.
            regridded = data.interp(latitude=lats, longitude=lons)
            # Take daily average of the variable, dimensions (n_days, 56, 120)
            # where n_days is the number of days in the month. Deal with February 29th later.
            daily_avg = regridded.resample(valid_time='d').mean()
            # Append to the list of datasets for this variable
            datasets.append(daily_avg)
        # Concatenate all the months, keeping the datetime
        fullyear = xr.concat(datasets, dim='valid_time')
        # Check the shape of the dimensions, should be (365,56,120)
        print(f'\t{fullyear.sizes}')
        # Write out this netcdf
        fullyear.to_netcdf(output_filepath)





