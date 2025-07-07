import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import xarray as xr
import pandas as pd

import unox.unox as unox
import unox.data as udata

# emiss = Emissions (TCR-2 t106)
# chemra = Chemical Reanalysis (TROPESS TCR-2)
# insitu = Insitu data (EPA)
# era5 = ERA5 reanalysis data

def make_y_input_file(year,
                      var='nox',
                      emiss_dir='/data/high_res/emacdonald/unet/datafiles/t106',
                      emiss_pre='nox_',
                      emiss_post='_t106_US.nc',
                      scale_factor=1e12,
                      nan_fill=0,
                      stage_2_cutoff=2013,
                      output_dir='inputfiles/'):
    """
    Create a y input file for the Unet model for the given year.

    The array in the generated file will have these dimensions:
    - time: 364 (or 365 for leap years)
        - One day less than usual to allow for t-1 variable
    - lat: length depends on the latitude grid
    - lon: length depends on the longitude grid
    - var: 1 (a dummy dimension to match the x input files)

    Parameters
    ----------
    year : int
        The year for which to create the y input file (between 2005 and 2021).
    var : str, optional
        The variable to extract from the dataset. Default is 'nox'.
    emiss_dir : str, optional
        Directory where the emissions data are stored. 
        Default is '/data/high_res/emacdonald/unet/datafiles/t106'.
    emiss_pre : str, optional
        Prefix for the emissions input file name. Default is 'nox_'.
    emiss_post : str, optional
        Extension for the input file name. Default is '_t106_US.nc'.
    scale_factor : float, optional
        Factor by which to scale the data. Default is 1e12.
    nan_fill : float, optional
        Value to fill NaNs in the dataset. Default is 0.
    stage_2_cutoff : int, optional
        Year after which the data will also be saved in stage 2.
    output_dir : str, optional
        Directory where the output y input file will be saved.
        Default is 'inputfiles/'.

    Returns
    -------
    y_data : numpy.ndarray
        The y input data for the specified year, scaled and processed.
    """
    # Assemble file path
    filepath = os.path.join(data_dir, f"{emiss_pre}{year}{emiss_post}")
    # Verify the path
    filepath = unox.verify_path(filepath)
    # Load data for the specified year
    y_data = xr.load_dataset(filepath)
    # Scale data
    y_data = y_data * scale_factor
    # Load lats and lons
    lats, lons = unox.load_lats_lons()
    # Interpolate to the latitude and longitude grid, resample to daily mean, 
    # and fill NaNs with specified value
    y_data = y_data.interp(lat=lats, lon=lons).resample(time='d').mean().fillna(nan_fill)
    # Add a dimension of size 1 to the end to match the number of dimensions for the x input files
    y_data = y_data.expand_dims('var',-1)  
    # Skip the first day because of the t-1 thing
    y_data = y_data[var][1::]
    # Save the data as a numpy file
    if not isinstance(output_dir, type(None)):
        # Assemble the file path
        output_filepath = os.path.join(output_dir, f"stage1/y/Y_{year}.npy")
        np.save(output_filepath, y_data)
        if year > stage_2_cutoff:
            # Save in stage 2 for years later than specified
            output_filepath_stage2 = os.path.join(output_dir, f"stage2/y/Y_{year}.npy")
            np.save(output_filepath_stage2, y_data)
        # Output message
        print(f"Created Y input file for {var} in {year}, saved to {output_filepath}")
    return np.array(y_data)

def make_x_input_file(year,
                      stage,
                      data_dir='/data/high_res/emacdonald/unet/datafiles/',
                      chemra_path='TROPESS/TROPESS_reanalysis_2hr_no2_sfc_',
                      insitu_path='US_EPA/daily_42602_',
                      era5_path='ERA5concatenated/',
                      scale_factors={'chemra': 1000,
                                     'sp': 100000,
                                     'ssrd': 1000000,
                                     'blh': 1000},
                      output_dir='inputfiles/'):
    """
    Create an x input file for the Unet model for the given year and stage.

    The array in the file will have these dimensions:
    - time: 364 (or 365 for leap years)
        - One day less than usual to allow for t-1 variable
    - lat: length depends on the latitude grid
    - lon: length depends on the longitude grid
    - var: 9 variables (e.g., 'no2', 'u10', 'v10', etc.)

    Parameters
    ----------
    year : int
        The year for which to create the x input file.
    stage : int
        The stage of the model (1 or 2) this will be input for.
    data_dir : str, optional
        Directory where the NOx data are stored. 
        Default is '/data/high_res/emacdonald/unet/datafiles/t106'.
    chemra_path : str, optional
        Path to the chemical reanalysis data files. 
        Default is 'TROPESS/TROPESS_reanalysis_2hr_no2_sfc_'.
    insitu_path : str, optional
        Path to the insitu data files. Default is 'US_EPA/daily_42602_'.
    era5_path : str, optional
        Path to the ERA5 reanalysis data files. Default is 'ERA5concatenated/'.
    output_dir : str, optional
        Directory where the output x input file will be saved. 
        Default is 'inputfiles/'.

    Returns
    -------
    x_data : xarray.Dataset
        The x input data for the specified year and stage.
    """
    # Assemble the file path for the chemical reanalysis data
    chemra_filepath = os.path.join(data_dir, f'{chemra_path}{year}.nc')
    # Verify the path
    chemra_filepath = unox.verify_path(chemra_filepath)
    # Load chemical reanalysis data
    chemra = xr.load_dataset(chemra_filepath)
    # Change longitude coordinate convention to match other data
    chemra.coords['lon'] = (chemra.coords['lon'] + 180) % 360 - 180  
    # chemra.coords['lon'] = udata.shift_lon(chemra.coords['lon'])  
    # Resample and rescale
    chemra = chemra.resample(time='d').mean() / scale_factors['chemra']
    # Find the number of days in the year
    ndays = len(chemra.coords['time'])
    # Fix the time coordinate to match the year
    if chemra_path=='TROPESS/TROPESS_reanalysis_2hr_no2_sfc_':
        # For an unexplained reason, the year in all TCR-2 files is always 2005.
        chemra.coords['time'] = pd.date_range(f"{year}-01-01", periods=ndays)
    
    # Combine chemical reanalysis and insitu data for stage 2
    if stage == 2:
        # Assemble the file path for the insitu data
        epa_filepath = os.path.join(data_dir, f'{insitu_path}{year}.csv')
        # Verify the path
        epa_filepath = unox.verify_path(epa_filepath)
        # Combine chemical reanalysis and insitu data
        chemra = fill_w_insitu(chemra, epa_filepath)
    
    # Interpolate to latitude and longitude grid
    lats, lons = unox.load_lats_lons()
    chemra = chemra.interp(lat=lats, lon=lons)
    
    # Start a list to hold datasets
    datasets = []
    # Add the chemical reanalysis data for day t (starting from the second day)
    datasets.append(chemra.no2[1::])

    # Get the time-shifted variable (day t-1)
    previousday = chemra.copy()
    # Fix rounding
    previousday.coords['time'] = (previousday.coords['time'] + 1).dt.ceil('D')
    # Rename t-1 variable
    previousday = previousday.rename({'no2': 'no2_tm1'})
    # Add the chemical reanalysis data for the previous day (t-1)
    datasets.append(previousday.no2_tm1[:-1])  # day t-1

    # Add the other variables from the ERA5 dataset
    for variable in ['u10', 'v10', 'blh', 'sp', 'skt', 't2m', 'ssrd']:
        # Assemble the file path for the ERA5 variable
        era5_var_filepath = os.path.join(data_dir, f'{era5_path}{year}{variable}.nc')
        # Verify the path
        era5_var_filepath = unox.verify_path(era5_var_filepath)
        # Load the ERA5 variable dataset
        # Note: The variable name in the dataset is assumed to be the same as `variable`
        era5_var = xr.load_dataset(era5_var_filepath)
        # Rename coordinates to match the other datasets
        era5_var = era5_var.rename({'valid_time': 'time', 'latitude': 'lat', 'longitude': 'lon'})
        # Add the variable data to the datasets list, skipping the first day
        datasets.append(getattr(era5_var, variable)[1:])
    
    # Merge all datasets into a single xarray Dataset
    x_data = xr.merge(datasets)
    # Convert calendar to 'noleap' to remove February 29th
    x_data = x_data.convert_calendar('noleap')

    # Scale some variables to make orders of magnitude more similar
    x_data['sp'] = x_data['sp'] / scale_factors['sp']        # Surface pressure
    x_data['ssrd'] = x_data['ssrd'] / scale_factors['ssrd']  # Surface solar radiation
    x_data['blh'] = x_data['blh'] / scale_factors['blh']     # Boundary layer height
    # Reorder dimensions to match the expected format
    x_data = x_data[['time', 'lat', 'lon', *list(x_data.data_vars)]]

    # Get a list of the variables in the dataset
    datavars = list(x_data.data_vars)
    print(datavars)
    # Create an empty numpy array to hold the data
    xnp = np.ndarray([364, 56, 120, len(datavars)])  # Adjust dimensions as needed
    # Fill the numpy array with data from the xarray Dataset
    for i in range(len(datavars)):
        xnp[:, :, :, i] = x_data[datavars[i]]  # Put it in the numpy array

    ## Save the data as a numpy file
    if not isinstance(output_dir, type(None)):
        # Assemble the file path
        output_filepath = os.path.join(output_dir, f'stage{stage}/x/X_{year}.npy')
        np.save(output_filepath, xnp)
        # Output message
        print(f"Created X input file for stage {stage} in {year}, saved to {output_filepath}")
    return xnp

def fill_w_insitu(xr_dataset,
                  insitu_filepath, 
                  var='no2',
                  ):
    """
    Replace the variable in an xarray Dataset with available insitu data.

    Given an xarray Dataset of reanalysis data, replace those values of the specified 
    variable when there is available insitu data in the provided filepath.

    Parameters
    ----------
    xr_dataset : xarray.Dataset
        The dataset containing reanalysis data.
    insitu_filepath : str
        Path to the CSV file containing insitu data.
    var : str, optional
        The variable to replace in the dataset. Default is 'no2'.

    Returns
    -------
    xarray.Dataset
        The updated dataset with insitu data replacing the specified variable.
    """
    # Verify the dataset
    udata.verify_dataset(xr_dataset)
    # Verify the insitu file path
    insitu_filepath = unox.verify_path(insitu_filepath)
    # Load the insitu data
    ## Specific to the EPA csv format
    insitu_data = pd.read_csv(insitu_filepath, parse_dates={'Date':['Date Local']}, index_col=['Date'], usecols=['Date Local', 'Latitude', 'Longitude', 'Arithmetic Mean'])
    # One group for each day of data in the insitu data file
    insitu_groups = insitu_data.groupby(['Date'])
    # Get the keys (dates) from the groups
    insitu_keys = [key for key in insitu_groups.groups.keys()]
    # Narrow the domain to the selected latitude and longitude grid
    lats, lons = unox.load_lats_lons()
    in1 = xr_dataset[var].where((xr_dataset.lat >= np.min(lats)), drop=True)
    in2 = in1.where((in1.lon <= np.max(lons)), drop=True)

    # Loop through each day in the insitu data
    for i in range(len(insitu_keys)):
        # Get the group for the ith day
        new_group = insitu_groups.get_group((insitu_keys[i]),)
        # Convert the group to a numpy array
        group_array = new_group.to_numpy()
        # Swap axes to get the shape (lat, lon, no2) for this day
        group_array = group_array.swapaxes(0, 1)
        # Get the latitude, longitude, and var values of the group
        lt = group_array[0]
        ln = group_array[1]
        values = group_array[2]
        # Select the day in the chemical reanalysis dataset
        day = in2.sel(indexers={'time': insitu_keys[i]})
        # Loop through each latitude in the group
        for j in range(len(lt)):
            # Find the nearest point in the chemical reanalysis dataset
            ## Tolerance is set to the grid cell size (1.125 degrees)
            pt = day.sel({'lat': lt[j], 'lon': ln[j]}, method='nearest', tolerance=1.125)
            # Replace the chemical reanalysis value with the insitu value
            xr_dataset[var].loc[{'time': insitu_keys[i], 'lon': pt.lon, 'lat': pt.lat}] = values[j]
    return xr_dataset
