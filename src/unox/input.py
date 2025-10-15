import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import xarray as xr
import pandas as pd
import json
import warnings

import unox.unox as unox
import unox.data as udata
from unox.plot_format import pad_extent

# emiss = Emissions (TCR-2 t106)
# chemra = Chemical Reanalysis (TROPESS TCR-2)
# insitu = Insitu data (EPA)
# era5 = ERA5 reanalysis data

# Define a dictionary of the variables to be used for each model variable
era5_vars_list = ['u10', 'v10', 'blh', 'sp', 'skt', 't2m', 'ssrd']
input_vars_dict = {
    'no2': {
        'x_vars': ['no2', 'no2_tm1'] + era5_vars_list,
        'y_vars': ['nox'],
    },
    'co': {
        'x_vars': ['SpeciesConcVV_CO', 'SpeciesConcVV_CO_tm1'] + era5_vars_list,
        'y_vars': ['EmisCO_Total'],
    }
}

def x_or_y_var(
    var,
    ):
    """
    Return whether the given variable is an x or y variable.

    Parameters
    ----------
    var : str
        The variable to check.

    Returns
    -------
    x_or_y : str
        'x' if the variable is an x variable, 'y' if it is a y variable.
    
    Examples
    --------
    >>> x_or_y_var('no2')
    'x'
    >>> x_or_y_var('nox')
    'y'
    """
    # Verify the variable is a string
    if not isinstance(var, str):
        raise TypeError(f'Variable must be a string, got {type(var)}.')
    # Check if the variable is in the input_vars_dict
    for key in input_vars_dict.keys():
        if var in input_vars_dict[key]['x_vars']:
            return 'x'
        elif var in input_vars_dict[key]['y_vars']:
            return 'y'
    raise ValueError(f"Variable '{var}' not recognized. Available variables in input_vars_dict: {input_vars_dict}")

def get_input_index(
    var,
    ):
    """
    Get the index of the given variable in the input array.

    Parameters
    ----------
    var : str
        The variable to check.
    
    Returns
    -------
    index : int
        The index of the variable in the input array.

    Examples
    --------
    >>> get_input_index('no2')
    0
    >>> get_input_index('u10')
    2
    """
    # Verify the variable is a string
    if not isinstance(var, str):
        raise TypeError(f'Variable must be a string, got {type(var)}.')
    # Check if the variable is in the input_vars_dict
    for key in input_vars_dict.keys():
        if var in input_vars_dict[key]['x_vars']:
            return input_vars_dict[key]['x_vars'].index(var)
        elif var in input_vars_dict[key]['y_vars']:
            return input_vars_dict[key]['y_vars'].index(var)
    raise ValueError(f"Variable '{var}' not recognized. Available variables in input_vars_dict: {input_vars_dict}")

def make_y_input_file(
    year,
    var='nox',
    emiss_dir='/data/high_res/emacdonald/unet/datafiles/t106',
    emiss_pre='nox_',
    emiss_post='_t106_US.nc',
    scale_factor=1e12,
    nan_fill=0,
    stage_2_cutoff=2013,
    output_dir='test_input',
    overwrite=True,
    **kwargs,
    ):
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
        Directory inside `inputfiles/` where the output y input file will be saved.
        Default is `'test_input'`.
    overwrite : bool, optional
        Whether to overwrite existing netcdf files. Default is True.
    **kwargs : dict, optional
        Additional keyword arguments (not used).

    Returns
    -------
    y_data : numpy.ndarray
        The y input data for the specified year, scaled and processed.
    """
    # Assemble file path
    filepath = os.path.join(emiss_dir, f"{emiss_pre}{year}{emiss_post}")
    # Verify the path
    filepath = unox.verify_path(filepath)
    # Load data for the specified year
    y_data = xr.load_dataset(filepath)
    # If level dimension present, sum across levels
    if "lev" in list(y_data.coords):
        print("level dimension detected")
        y_data = y_data.sum("lev")
    # Scale data
    y_data = scale_xr_var(y_data, var, scale_factor)
    # y_data = y_data * scale_factor
    # Load lats and lons
    lats, lons = unox.load_lats_lons()
    # Interpolate to the latitude and longitude grid, resample to daily mean, 
    # and fill NaNs with specified value
    y_data = y_data.interp(lat=lats, lon=lons).resample(time='d').mean().fillna(nan_fill)
    # Add a dimension of size 1 to the end to match the number of dimensions for the x input files
    y_data = y_data.expand_dims('var',-1)
    # Convert calendar to 'noleap' to remove February 29th
    y_data = y_data.convert_calendar('noleap')
    # Skip the first day because of the t-1 thing
    input_netcdf_xr = y_data.isel(time=slice(1,None))
    y_data = y_data[var][1::]
    # Create a dictionary of global attributes
    g_attr_dict={
        'y_var': var,
        'emiss_dir': emiss_dir,
        'emiss_pre': emiss_pre,
        'emiss_post': emiss_post,
        'nan_fill': nan_fill,
        'stage_2_cutoff': stage_2_cutoff,
    }
    # Save the data as a numpy file
    if not isinstance(output_dir, type(None)):
        # Assemble the file path
        output_filepath = os.path.join(f'inputfiles/{output_dir}/stage1/y/Y_{year}.npy')
        # Make sure the output directory exists
        unox.make_file_path(output_filepath)
        np.save(output_filepath, y_data)
        if year > stage_2_cutoff:
            # Save in stage 2 for years later than specified
            output_filepath_stage2 = os.path.join(f'inputfiles/{output_dir}/stage2/y/Y_{year}.npy')
            # Make sure the output directory exists
            unox.make_file_path(output_filepath_stage2)
            np.save(output_filepath_stage2, y_data)
        # Create metadata file
        make_input_metadata_file(
            year=year,
            x_or_y='y',
            attr_dict={
                'vars': var,
                'emiss_dir': emiss_dir,
                'emiss_pre': emiss_pre,
                'emiss_post': emiss_post,
                'scaled_by': scale_factor,
                'nan_fill': nan_fill,
                'stage_2_cutoff': stage_2_cutoff,
            },
            stage=None,
            output_dir=output_dir,
        )
        # Output message
        print(f"Created Y input file for {var} in {year}, saved to {output_filepath}")
        ### For netcdf
        # Assemble the file path
        output_filepath = f'inputfiles/{output_dir}/{output_dir}.nc'
        # Write data out to a netcdf
        input_netcdf_xr = write_input_netcdf(
            input_netcdf_xr,
            output_filepath,
            g_attr_dict=g_attr_dict,
            overwrite=overwrite,
            **kwargs,
        )
        print(f"Saved y input data to {output_filepath}")
        return xr.load_dataset(output_filepath), g_attr_dict
    else:
        return input_netcdf_xr, g_attr_dict

def write_input_netcdf(
    input_netcdf_xr,
    output_filepath,
    g_attr_dict=None,
    overwrite=True,
    sort=True,
    **kwargs,
    ):
    """
    Write an xarray Dataset to a netcdf file, appending or overwriting as needed.

    Parameters
    ----------
    input_netcdf_xr : xarray.Dataset
        The dataset to write to the netcdf file.
    output_filepath : str
        Path to the output netcdf file.
    g_attr_dict : dict, optional
        Dictionary of global attributes to add to the dataset if creating a new file.
    overwrite : bool, optional
        Whether to overwrite existing data in the netcdf file if there are overlapping times.
        Default is True.
    sort : bool, optional
        Whether to sort the xarray before writing to netcdf. Sorting takes a long time.
        Default is True.

    Returns
    -------
    input_netcdf_xr : xarray.Dataset
        The dataset that was written to the netcdf file.
    """
    # Check whether the netcdf file already exists
    if os.path.exists(output_filepath):
        # Load the existing netcdf file
        existing_ds = xr.load_dataset(output_filepath)
        # Verify the dataset
        existing_ds = udata.verify_dataset(existing_ds)
        # Check if the existing dataset and the new one have the same lat/lon values
        existing_lats = existing_ds.coords['lat'].values
        existing_lons = existing_ds.coords['lon'].values
        new_lats = input_netcdf_xr.coords['lat'].values
        new_lons = input_netcdf_xr.coords['lon'].values
        if not np.array_equal(existing_lats, new_lats):
            raise ValueError(f"Latitude values of the existing netcdf file and the new data do not match. \nExisting lats: \n{existing_lats} \nNew lats: \n{new_lats}")
        if not np.array_equal(existing_lons, new_lons):
            raise ValueError(f"Longitude values of the existing netcdf file and the new data do not match. \nExisting lons: \n{existing_lons} \nNew lons: \n{new_lons}")
        # Get lists of variables from both datasets
        new_vars = list(input_netcdf_xr.data_vars)
        existing_vars = list(existing_ds.data_vars)
        # Find the variables in common, if any
        shared_vars = set(new_vars) & set(existing_vars)
        if len(shared_vars) > 0:
            # Check whether any time values are already present in the existing dataset
            existing_times = set(existing_ds.coords['time'].values)
            new_times = set(input_netcdf_xr.coords['time'].values)
            overlapping_times = existing_times.intersection(new_times)
            if len(overlapping_times) > 1:
                # Get the first and last overlapping times
                first_overlap = min(overlapping_times)
                last_overlap = max(overlapping_times)
                # Format them to YYYY-MM-DD
                first_overlap = pd.to_datetime(str(first_overlap)).strftime('%Y-%m-%d')
                last_overlap = pd.to_datetime(str(last_overlap)).strftime('%Y-%m-%d')
            if overlapping_times and overwrite==False:
                raise ValueError(f"The new data overlaps with the existing file in {output_filepath} between {first_overlap} and {last_overlap}. To overwrite, set overwrite=True.")
            elif overlapping_times and overwrite==True:
                print(f"Overwriting overlapping data in {output_filepath} for times between {first_overlap} and {last_overlap}.")
                # Remove the overlapping times from the existing dataset
                existing_ds = existing_ds.drop_sel(time=list(overlapping_times))
            # Concatenate the new data with the existing dataset along the time dimension
            input_netcdf_xr = xr.concat([existing_ds, input_netcdf_xr], dim='time')
        else:
            # Merge the datasets
            input_netcdf_xr = xr.merge([existing_ds, input_netcdf_xr])
        # Sort the dataset by time
        if sort:
            print("Sorting the dataset by time.")
            input_netcdf_xr = input_netcdf_xr.sortby('time')
    else:
        # Add a description
        input_netcdf_xr.attrs['description'] = f"Input data for the Unet model. Data for each year is added to this file as it is generated."
    # Add global attributes
    input_netcdf_xr = set_global_attrs(input_netcdf_xr, g_attr_dict)
    # Save the netcdf file
    # Make sure the output directory exists
    unox.make_file_path(output_filepath)
    input_netcdf_xr.to_netcdf(output_filepath)
    return input_netcdf_xr

def set_global_attrs(
    xr_dataset,
    attr_dict,
    ):
    """
    Add attributes to an xarray Dataset.

    Parameters
    ----------
    xr_dataset : xarray.Dataset
        The dataset to which attributes will be added.
    attr_dict : dict
        Dictionary of attributes to add to the dataset.

    Returns
    -------
    xarray.Dataset
        The dataset with added attributes.
    """
    # Verify the dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Verify the attribute dictionary
    if not isinstance(attr_dict, dict):
        raise TypeError(f'attr_dict must be a dictionary, got {type(attr_dict)}.')
    # Add each attribute to the dataset
    for key, value in attr_dict.items():
        xr_dataset.attrs[key] = value
    # Update the modification date
    xr_dataset.attrs['modification_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    return xr_dataset

def set_var_attrs(
    xr_dataset,
    var,
    attr_dict,
    ):
    """
    Add attributes to a variable in an xarray Dataset.

    Parameters
    ----------
    xr_dataset : xarray.Dataset
        The dataset containing the variable to which attributes will be added.
    var : str
        The variable to which attributes will be added.
    attr_dict : dict
        Dictionary of attributes to add to the variable.

    Returns
    -------
    xarray.Dataset
        The dataset with the variable having added attributes.
    """
    # Verify the dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Verify the variable is in the dataset
    if var not in xr_dataset.data_vars:
        raise ValueError(f"Variable '{var}' not found in dataset. Available variables: {list(xr_dataset.data_vars)}")
    # Verify the attribute dictionary
    if not isinstance(attr_dict, dict):
        raise TypeError(f'attr_dict must be a dictionary, got {type(attr_dict)}.')
    # Add each attribute to the variable
    for key, value in attr_dict.items():
        xr_dataset[var].attrs[key] = value
    return xr_dataset

def scale_xr_var(
    xr_dataset,
    var,
    scale_factor,
    ):
    """
    Scale a variable in an xarray Dataset by a given factor.

    Parameters
    ----------
    xr_dataset : xarray.Dataset
        The dataset containing the variable to be scaled.
    var : str
        The variable to be scaled.
    scale_factor : float
        The factor by which to scale the variable.

    Returns
    -------
    xarray.Dataset
        The dataset with the scaled variable.
    """
    # Verify the dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Verify the variable is in the dataset
    if var not in xr_dataset.data_vars:
        raise ValueError(f"Variable '{var}' not found in dataset. Available variables: {list(xr_dataset.data_vars)}")
    # Note the variable attributes
    var_attrs = xr_dataset[var].attrs
    # Print the time range
    time_start = xr_dataset.coords['time'].values[0]
    time_end = xr_dataset.coords['time'].values[-1]
    # print(f"Scaling variable '{var}' for time range {time_start} to {time_end} by a factor of {scale_factor}.")
    # Print the maximum, minimum, and mean before scaling
    # this_max = xr_dataset[var].max().item()
    # this_min = xr_dataset[var].min().item()
    # this_mean = xr_dataset[var].mean().item()
    # print(f"Before scaling {var}: max={this_max}, min={this_min}, mean={this_mean}")
    # Scale the variable
    xr_dataset[var] = xr_dataset[var] * scale_factor
    # Print the maximum, minimum, and mean after scaling
    # this_max = xr_dataset[var].max().item()
    # this_min = xr_dataset[var].min().item()
    # this_mean = xr_dataset[var].mean().item()
    # print(f"After scaling {var}: max={this_max}, min={this_min}, mean={this_mean}")
    # Add scale factor to the attributes
    ## Note: `scale_factor` is a protected attribute name in xarray. If used, the variable
    ## will be scaled by that factor when loading with xr.load_dataset() and `scale_factor`
    ## will not show up in the loaded xarray. I'm using `scaled_by` to avoid this confusion.
    var_attrs['scaled_by'] = scale_factor
    # Reapply the variable attributes
    xr_dataset = set_var_attrs(xr_dataset, var, var_attrs)
    return xr_dataset

def make_x_input_file(
    year,
    stage,
    data_dir='/data/high_res/emacdonald/unet/datafiles/',
    chemra_path='TROPESS/TROPESS_reanalysis_2hr_no2_sfc_',
    chemra_var='no2',
    insitu_path='US_EPA/daily_42602_',
    era5_path='ERA5concatenated/',
    scale_factors={'chemra': 1000,
                    'sp': 100000,
                    'ssrd': 1000000,
                    'blh': 1000},
    stage_2_cutoff=2013,
    output_dir='test_input',
    overwrite=True,
    **kwargs,
    ):
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
        Default is '/data/high_res/emacdonald/unet/datafiles/'.
    chemra_path : str, optional
        Path to the chemical reanalysis data files. 
        Default is 'TROPESS/TROPESS_reanalysis_2hr_no2_sfc_'.
    chemra_var : str, optional
        The variable to extract from the dataset. Default is 'no2'
    insitu_path : str, optional
        Path to the insitu data files. Default is 'US_EPA/daily_42602_'.
    era5_path : str, optional
        Path to the ERA5 reanalysis data files. Default is 'ERA5concatenated/'.
    scale_factors : dict, optional
        Scaling factors for the variables. Default is a dictionary with
        scaling factors for 'chemra', 'sp', 'ssrd', and 'blh'.
    stage_2_cutoff : int, optional
        Year after which input files will also be generated for stage 2. Default is 2013.
    output_dir : str, optional
        Directory inside `inputfiles/` where the output x input file will be saved.
        Default is `'test_input'`.

    Returns
    -------
    x_data : xarray.Dataset
        The x input data for the specified year and stage.
    """
    # Assemble the file path for the chemical reanalysis data
    chemra_filepath = f'{data_dir}/{chemra_path}{year}.nc'
    # Verify the path
    chemra_filepath = unox.verify_path(chemra_filepath)
    # Load chemical reanalysis data
    # chemra = xr.load_dataset(chemra_filepath)
    chemra = xr.open_dataset(chemra_filepath)
    # If level dimension present, sum across levels
    if "lev" in list(chemra.coords):
        print("level dimension detected")
        chemra = chemra.sum("lev")
    # Regularize the data depending on the source
    if chemra_path=='TROPESS/TROPESS_reanalysis_2hr_no2_sfc_':
        # Change longitude coordinate convention to match other data
        # chemra.coords['lon'] = (chemra.coords['lon'] + 180) % 360 - 180
        chemra = udata.shift_lon_arr(chemra)
        # Drop the `nv` dimension and the `bnds` variables
        if 'nv' in chemra.dims:
            chemra = chemra.isel(nv=0).drop_vars(['time_bnds', 'lon_bnds', 'lat_bnds'])
        # For time, latitude, and longitude, drop the var+`_bnds` attributes
        for coord in ['time', 'lat', 'lon']:
            if 'bounds' in chemra[coord].attrs:
                chemra[coord].attrs.pop('bounds')
    # Get latitude and longitude values
    lats, lons = unox.load_lats_lons()
    # Get the extent of the lats and lons
    extent = udata.get_extent(lats=lats, lons=lons)
    # Pad the extent
    extent = pad_extent(extent, padding=0.1)
    # Trim the chemical reanalysis data to the extent of the lat/lon grid
    chemra = chemra.where(
        (chemra.lat >= extent[0]) &
        (chemra.lat <= extent[1]) &
        (chemra.lon >= extent[2]) &
        (chemra.lon <= extent[3]),
        drop=True,
    )
    # Resample the time to days
    chemra = chemra.resample(time='d').mean()
    # Rescale the chemical reanalysis data
    chemra = scale_xr_var(chemra, chemra_var, 1/scale_factors['chemra'])
    # Find the number of days in the year
    ndays = len(chemra.coords['time'])
    # Fix the time coordinate to match the year
    if chemra_path=='TROPESS/TROPESS_reanalysis_2hr_no2_sfc_':
        # Save the time attributes
        time_attrs = chemra['time'].attrs
        # For an unexplained reason, the year in all TCR-2 files is always 2005.
        chemra.coords['time'] = pd.date_range(f"{year}-01-01", periods=ndays)
        # Reapply the time attributes
        chemra['time'].attrs = time_attrs
    
    # Combine chemical reanalysis and insitu data for stage 2
    if stage == 2 and year > stage_2_cutoff:
        # Assemble the file path for the insitu data
        epa_filepath = os.path.join(data_dir, f'{insitu_path}{year}.csv')
        # Verify the path
        epa_filepath = unox.verify_path(epa_filepath)
        # Combine chemical reanalysis and insitu data
        chemra = fill_w_insitu(chemra, epa_filepath)
    
    # Interpolate to latitude and longitude grid
    chemra = chemra.interp(lat=lats, lon=lons, method='slinear')
    
    # Start a list to hold datasets
    datasets = []
    # Add the chemical reanalysis data for day t (starting from the second day)
    datasets.append(chemra[chemra_var][1::])

    # Get the time-shifted variable (day t-1)
    previousday = chemra.copy()
    # Fix rounding
    previousday.coords['time'] = (previousday.coords['time'] + 1).dt.ceil('D')
    # Rename t-1 variable
    chemra_var_tm1 = chemra_var+'_tm1'
    previousday = previousday.rename({chemra_var: chemra_var_tm1})
    # Add the chemical reanalysis data for the previous day (t-1)
    datasets.append(previousday[chemra_var_tm1][:-1])  # day t-1
    chemra[chemra_var_tm1] = chemra[chemra_var].shift(time=1)
    # Drop January 1st, as the t-1 variable will have null values on that day
    chemra = chemra.drop_sel(time=f'{year}-01-01')

    # Add the other variables from the ERA5 dataset
    for variable in era5_vars_list:
        # Assemble the file path for the ERA5 variable
        era5_var_filepath = os.path.join(data_dir, f'{era5_path}{year}{variable}.nc')
        # Verify the path
        era5_var_filepath = unox.verify_path(era5_var_filepath)
        # Load the ERA5 variable dataset
        # Note: The variable name in the dataset is assumed to be the same as `variable`
        era5_var = xr.load_dataset(era5_var_filepath)
        # Drop the `number` coordinate
        era5_var = era5_var.drop_vars('number')
        # Rename coordinates to match the other datasets
        era5_var = era5_var.rename({'valid_time': 'time', 'latitude': 'lat', 'longitude': 'lon'})
        # Add the variable data to the datasets list, skipping the first day
        datasets.append(getattr(era5_var, variable)[1:])
        # Drop January 1st, as the t-1 variable will have null values on that day
        era5_var = era5_var.drop_sel(time=f'{year}-01-01')
        # Add the variable to the xarray
        ## Note: This assumes that the coordinates are the same
        ## which is true in this case as the lat lon arrays used to interpolate
        ## the chemra data came from the ERA5 data originally
        chemra[variable] = era5_var[variable]
    
    # Merge all datasets into a single xarray Dataset
    x_data = xr.merge(datasets)
    # Convert calendar to 'noleap' to remove February 29th
    x_data = x_data.convert_calendar('noleap')
    chemra = chemra.convert_calendar('noleap')

    # Scale some variables to make orders of magnitude more similar
    for variable in era5_vars_list:
        if variable in scale_factors.keys():
            x_data = scale_xr_var(x_data, variable, 1/scale_factors[variable])
            chemra = scale_xr_var(chemra, variable, 1/scale_factors[variable])
    # x_data['sp'] = x_data['sp'] / scale_factors['sp']        # Surface pressure
    # x_data['ssrd'] = x_data['ssrd'] / scale_factors['ssrd']  # Surface solar radiation
    # x_data['blh'] = x_data['blh'] / scale_factors['blh']     # Boundary layer height
    # Reorder dimensions to match the expected format
    x_data = x_data[['time', 'lat', 'lon', *list(x_data.data_vars)]]

    # Get a list of the variables in the dataset
    datavars = list(x_data.data_vars)
    # print(datavars)
    # Create an empty numpy array to hold the data
    xnp = np.ndarray([364, 56, 120, len(datavars)])  # Adjust dimensions as needed
    # Fill the numpy array with data from the xarray Dataset
    for i in range(len(datavars)):
        xnp[:, :, :, i] = x_data[datavars[i]]  # Put it in the numpy array

    # Create a dictionary of global attributes
    g_attr_dict={
        'x_vars': datavars,
        'data_dir': data_dir,
        'chemra_path': chemra_path,
        'insitu_path': insitu_path,
        'era5_path': era5_path,
    }
    ## Save the data as a numpy file
    if not isinstance(output_dir, type(None)):
        # Assemble the file path
        output_filepath = os.path.join(f'inputfiles/{output_dir}/stage{stage}/x/X_{year}.npy')
        # Make sure the output directory exists
        unox.make_file_path(output_filepath)
        np.save(output_filepath, xnp)
        # Create metadata file
        make_input_metadata_file(
            year=year,
            x_or_y='x',
            
            attr_dict={
                'vars': datavars,
                'data_dir': data_dir,
                'chemra_path': chemra_path,
                'insitu_path': insitu_path,
                'era5_path': era5_path,
                'var_scale_factors': scale_factors,
                'stage_2_cutoff': stage_2_cutoff,
            },
            stage=stage,
            output_dir=output_dir,
        )
        # Output message
        print(f"Created X input file for stage {stage} in {year}, saved to {output_filepath}")
        ### For netcdf
        # Assemble the file path
        output_filepath = f'inputfiles/{output_dir}/{output_dir}.nc'
        # Write data out to a netcdf
        input_netcdf_xr = write_input_netcdf(
            chemra,
            output_filepath,
            g_attr_dict=g_attr_dict,
            overwrite=overwrite,
            **kwargs,
        )
        print(f"Saved x input data to {output_filepath}")
        return xr.load_dataset(output_filepath), g_attr_dict
    else:
        return chemra, g_attr_dict

def get_npy_from_netcdf(
    netcdf,
    var,
    year,
    ):
    """ 
    Extract a numpy array for a specific variable and year from a netcdf file.

    Parameters
    ----------
    netcdf : str or xr.Dataset
        Path to the netcdf file or an xarray Dataset.
    var : str
        The variable to extract.
    year : int
        The year for which to extract the data.

    Returns
    -------
    np.ndarray
        The extracted data as a numpy array.
    """
    # Check if netcdf is a string (file path) or an xarray Dataset
    if isinstance(netcdf, str):
        # Verify the netcdf file path
        netcdf_filepath = unox.verify_path(netcdf_filepath)
        # Load the netcdf file
        xr_dataset = xr.load_dataset(netcdf_filepath)
    elif isinstance(netcdf, xr.Dataset):
        xr_dataset = netcdf
    else:
        raise TypeError(f'netcdf must be a file path (str) or an xarray.Dataset, got {type(netcdf)}.')
    # Verify the dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Verify the variable is in the dataset
    if var not in xr_dataset.data_vars:
        raise ValueError(f"Variable '{var}' not found in dataset. Available variables: {list(xr_dataset.data_vars)}")
    # Select the data for the specified year
    data_for_year = xr_dataset[var].sel(time=slice(f'{year}-01-01', f'{year}-12-31'))
    # Convert to numpy array
    data_array = data_for_year.to_numpy()
    return data_array

def fill_w_insitu(
    xr_dataset,
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
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Verify the insitu file path
    insitu_filepath = unox.verify_path(insitu_filepath)
    # Load the insitu data
    ## Specific to the EPA csv format
    insitu_data = pd.read_csv(insitu_filepath, parse_dates={'Date':['Date Local']}, index_col=['Date'], usecols=['Date Local', 'Latitude', 'Longitude', 'Arithmetic Mean'])
    # insitu_data = csv_to_pd(insitu_filepath, is_US_EPA=True)
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

def make_all_y_input_files(
    years=range(2005, 2021),
    var='nox',
    output_dir='test_input',
    sort=True,
    **kwargs,
    ):
    """
    Create y input files for multiple years.

    Runs the `make_y_input_file` function for each year in the specified range.

    Parameters
    ----------
    years : iterable, optional
        Years for which to create y input files. Default is range(2005, 2021).
    var : str, optional
        Variable to extract from the dataset. Default is 'nox'.
    output_dir : str, optional
        Directory inside `inputfiles/` where the output y input files will be saved.
        Default is `'test_input'`.
    sort : bool, optional
        Whether to sort the xarray after making all y inputs. Sorting takes a long time.
        Default is True.
    **kwargs : dict, optional
        Additional keyword arguments to pass to the `make_y_input_file` function.

    Returns
    -------
    y_data_array : list of numpy.ndarray
        List of y input data arrays for the specified years.
    """
    # Assemble the filepath
    output_filepath = f'inputfiles/{output_dir}/{output_dir}.nc'
    # Make sure the output directory exists
    # if not os.path.exists(f'inputfiles/{output_dir}/stage1/y'):
    #     os.makedirs(f'inputfiles/{output_dir}/stage1/y')
    # if not os.path.exists(f'inputfiles/{output_dir}/stage2/y'):
    #     os.makedirs(f'inputfiles/{output_dir}/stage2/y')
    y_data_array = []
    for year in years:
        print(f"\tCreating y input data for {var} in {year}...")
        y_data, g_attr_dict = make_y_input_file(
            year=year, 
            var=var,
            output_dir=None,
            sort=False,
            **kwargs,
        )
        y_data_array.append(y_data)
    # Concatenate the datasets along the time dimension
    print(f"Concatenating the y datasets")
    input_netcdf_xr = xr.concat(y_data_array, dim='time')
    # Sort the dataset by time
    if sort:
        print("Sorting the y data by time.")
        input_netcdf_xr = input_netcdf_xr.sortby('time')
    # Save the y data to a netcdf
    print(f"Saving y inputs to {output_filepath}")
    input_netcdf_xr = write_input_netcdf(
        input_netcdf_xr,
        output_filepath,
        g_attr_dict=g_attr_dict,
        **kwargs,
    )
    return xr.load_dataset(output_filepath)

def make_all_x_input_files(
    years=range(2005, 2021),
    stage=1,
    stage_2_cutoff=2013,
    output_dir='test_input',
    sort=True,
    **kwargs,
    ):
    """
    Create x input files for multiple years and stages.

    Runs the `make_x_input_file` function for each year and stage in the specified ranges.

    Parameters
    ----------
    years : iterable, optional
        Years for which to create x input files. Default is range(2005, 2021).
    stage : int, optional
        Stage of the model (1 or 2) for which to create x input files. 
        Default is 1.
    stage_2_cutoff : int, optional
        Year after which the data will also be saved in stage 2. Default is 2013.
    output_dir : str, optional
        Directory inside `inputfiles/` where the output x input files will be saved.
        Default is `'test_input'`.
    sort : bool, optional
        Whether to sort the xarray after making all x inputs. Sorting takes a long time.
        Default is True.
    **kwargs : dict, optional
        Additional keyword arguments to pass to the `make_x_input_file` function.

    Returns
    -------
    x_data_array : list of xarray.Dataset
        List of x input data arrays for the specified years and stages.
    """
    # Assemble the filepath
    output_filepath = f'inputfiles/{output_dir}/{output_dir}.nc'
    # Make sure the output directory exists
    # if not os.path.exists(f'inputfiles/{output_dir}/stage{stage}/x'):
    #     os.makedirs(f'inputfiles/{output_dir}/stage{stage}/x')
    x_data_array = []
    for year in years:
        if stage == 2 and year <= stage_2_cutoff:
            # Skip stage 2 for years before the cutoff
            continue
        print(f"Creating x input file for stage {stage} in {year}...")
        x_data, g_attr_dict = make_x_input_file(
            year=year,
            stage=stage,
            stage_2_cutoff=stage_2_cutoff,
            output_dir=None,
            sort=False,
            **kwargs,
        )
        x_data_array.append(x_data)
    # Concatenate the datasets along the time dimension
    print(f"Concatenating the x datasets")
    input_netcdf_xr = xr.concat(x_data_array, dim='time')
    # Sort the dataset by time
    if sort:
        print("Sorting the x data by time.")
        input_netcdf_xr = input_netcdf_xr.sortby('time')
    # Save the x data to a netcdf
    print(f"Saving x inputs to {output_filepath}")
    input_netcdf_xr = write_input_netcdf(
        input_netcdf_xr,
        output_filepath,
        g_attr_dict=g_attr_dict,
        **kwargs,
    )
    return xr.load_dataset(output_filepath)

def make_all_input_files(
    years=range(2005, 2021),
    stages=[1, 2],
    output_dir='test_input',
    sort=True,
    **kwargs,
    ):
    """
    Create all input files for the Unet model.

    This function combines the creation of y input files and x input files 
    for both stages.

    Parameters
    ----------
    years : iterable, optional
        Years for which to create input files. Default is range(2005, 2021).
    stages : iterable, optional
        Stages of the model for which to create x input files. 
        Default is [1, 2].
    output_dir : str, optional
        Directory inside `inputfiles/` where the output input files will be saved.
        Default is `'test_input'`.
    sort : bool, optional
        Whether to sort the xarray after making all inputs. Sorting takes a long time.
        Default is True.
    **kwargs : dict, optional
        Additional keyword arguments to pass to the `make_y_input_file` and 
        `make_x_input_file` functions.

    Returns
    -------
    None
    """
    print("It may take around 3 hours to generate all input files.")
    # Make sure the output directory exists
    if not os.path.exists(f'inputfiles/{output_dir}'):
        os.makedirs(f'inputfiles/{output_dir}')
    # Make sure the directories for the stages exist
    for stage in stages:
        stage_dir = os.path.join(f'inputfiles/{output_dir}/stage{stage}')
        if not os.path.exists(stage_dir):
            os.makedirs(stage_dir)
    # Create y input files
    print("Creating y input files...")
    input_netcdf_xr = make_all_y_input_files(
        years=years,
        output_dir=output_dir,
        sort=False,
        **kwargs,
    )
    # Create x input files for each stage
    for stage in stages:
        print(f"Creating x input files for stage {stage}...")
        input_netcdf_xr = make_all_x_input_files(
            years=years,
            stage=stage,
            output_dir=output_dir,
            sort=False,
            **kwargs,
        )
    # Sort the dataset by time
    if sort:
        print("Sorting the y data by time.")
        input_netcdf_xr = input_netcdf_xr.sortby('time')
    print("Completed making all input files.")
    return input_netcdf_xr

def make_input_metadata_file(
    year,
    x_or_y,
    attr_dict,
    stage=None,
    output_dir='test_input',
    ):
    """
    Create a metadata file for the input data.

    Gather the metadata for the input files and save it to a csv in the same 
    directory as those input files.

    Parameters
    ----------
    year : int
        The year for which the metadata is being created.
    x_or_y : str
        Specify whether the metadata is for 'x' or 'y' input files.
    attr_dict : dict
        Dictionary containing metadata attributes and their values.
    stage : int, optional
        The stage of the model (1 or 2) this metadata is for.
    output_dir : str, optional
        Directory inside `inputfiles/` where the metadata file will be saved.
        Default is `'test_input'`. If None, the metadata will not be saved to a file.

    Returns
    -------
    metadata_dict : dict
        The metadata dictionary that was saved to the json file.
        Has the format:
        ```json
        {
            "years": {
                "stage1": {
                    "x": [2005, ...],
                    "y": [2005, ...]
                },
                "stage2": {
                    "x": [2014, ...],
                    "y": [2014, ...]
                }
            },
            "x_attrs": {
                "data_dir": "/data/high_res/emacdonald/unet/datafiles/",
                ...,
                "var_scale_factors": {"chemra": 1000, ...},
                "stage_2_cutoff": 2013
            },
            "y_attrs": {
                "var": "nox",
                ...,
                "stage_2_cutoff": 2013
            }
        }
        ```
    """
    # Verify `year` is a number
    if udata.verify_number(year) == False:
        raise TypeError(f'Year must be a number, got {year}.')
    # Verify `x_or_y` is either 'x' or 'y'
    if x_or_y not in ['x', 'y']:
        raise ValueError(f"x_or_y must be either 'x' or 'y', got {x_or_y}.")
    # Verify `attr_dict` is a dictionary
    if not isinstance(attr_dict, dict):
        raise TypeError(f'attr_dict must be a dictionary, got {type(attr_dict)}.')
    # Check for a valid stage number
    if udata.verify_number(stage):
        if stage in [1, 2]:
            pass
        else:
            raise ValueError("Stage must be 1, 2, or None.")
    elif isinstance(stage, type(None)):
        pass
    else:
        raise ValueError("Stage must be 1, 2, or None.")
    # Verify output_dir is a string or None
    if not (isinstance(output_dir, str) or isinstance(output_dir, type(None))):
        raise TypeError(f'output_dir must be a string or None, got {type(output_dir)}.')
    # Check whether the given output directory includes 'inputfiles/'
    if isinstance(output_dir, type(None)):
        output_filepath = None
    elif not output_dir.startswith('inputfiles/'):
        output_filepath = 'inputfiles/' + output_dir + '/input_metadata.json'
        output_dir = 'inputfiles/' + output_dir
    else:
        output_filepath = output_dir + '/input_metadata.json'
    # Make sure the output directory exists
    if not isinstance(output_dir, type(None)) and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # If the file already exists, load it
    if not isinstance(output_filepath, type(None)) and os.path.exists(output_filepath):
        with open(output_filepath, 'r') as f:
            metadata_dict = json.load(f)
            isNew = False
    else:
        metadata_dict = {
            'years': {
                'stage1': {
                    'x': [],
                    'y': [],
                },
                'stage2': {
                    'x': [],
                    'y': [],
                },
            },
            'x_attrs': {},
            'y_attrs': {},
        }
        isNew = True
    ## Add the attributes and years to the metadata dictionary
    # Check if the attrs match
    if isNew == False and metadata_dict[x_or_y+'_attrs'] != attr_dict:
        warnings.warn(f'Metadata attributes for {x_or_y} {year} input files do not match the existing metadata. Overwriting existing attributes.')
    # Add the y attributes to the metadata dictionary
    metadata_dict[x_or_y+'_attrs'] = attr_dict
    # Select the stage
    if stage in [1, None]:
        # Add the year to the metadata dictionary
        metadata_dict['years']['stage1'][x_or_y].append(year)
        # Sort the list of years in ascending order, removing duplicates
        metadata_dict['years']['stage1'][x_or_y] = sorted(list(set(metadata_dict['years']['stage1'][x_or_y])))
    # Add info about stage 2 if applicable
    if stage in [2, None]:
        if year > attr_dict['stage_2_cutoff']:
            metadata_dict['years']['stage2'][x_or_y].append(year)
            # Sort the list of years in ascending order, removing duplicates
            metadata_dict['years']['stage2'][x_or_y] = sorted(list(set(metadata_dict['years']['stage2'][x_or_y])))
        else:
            print(f'Stage 2 cutoff is {attr_dict["stage_2_cutoff"]}, skipping {x_or_y} {year} input file for stage 2.')
            
    # Output the metadata dictionary to a json file
    if not isinstance(output_dir, type(None)):
        with open(output_filepath, 'w') as file:
            file.write(json.dumps(metadata_dict, indent=4))
    return metadata_dict