import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import xarray as xr
import pandas as pd
import json
import warnings

import unox.unox as unox
from unox.HPC.data0.paths import verify_path
import unox.data as udata
from unox.plot_format import pad_extent

# emiss = Emissions (TCR-2 t106)
# chemra = Chemical Reanalysis (TROPESS TCR-2)
# insitu = Insitu data (EPA)
# era5 = ERA5 reanalysis data

# Define a dictionary of the variables to be used for each model variable
era5_vars_list = ['u10', 'v10', 'blh', 'sp', 'skt', 't2m', 'ssrd', 'lsm']
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
    write_this_year=True,
    overwrite=True,
    output_format='nc',
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
        Default is '/data/high_res/t106'.
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
    write_this_year : bool, optional
        Whether to write the data for this year or just return the xarray without writing to file.
        Default is True.
    output_format : str, optional
        Whether to save netcdf files ('nc'), numpy arrays ('npy'), or 'both'.
        Default is 'nc'. Irrelevant if `write_this_year` is False.
    overwrite : bool, optional
        Whether to overwrite existing netcdf files. Default is True.
    **kwargs : dict, optional
        Additional keyword arguments (not used).

    Returns
    -------
    input_netcdf_xr : xarray.Dataset
        The y input data for the specified year.
    g_attr_dict : dict
        Dictionary of global attributes for the dataset.
    """
    # Assemble file path
    filepath = f'{emiss_dir}/{emiss_pre}{year}{emiss_post}'
    # Verify the path
    filepath = verify_path(filepath)
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
    # Write out results
    if not isinstance(output_dir, type(None)):
        # Create metadata file
        meta_dict = make_input_metadata_file(
            input_netcdf_xr,
            output_dir=output_dir,
            g_attrs=g_attr_dict,
        )
        # Save the data to file
        # For writing out a numpy file
        if output_format in ['npy', 'both']:
            # Assemble the file path
            output_filepath = f'inputfiles/{output_dir}/stage1/y/Y_{year}.npy'
            # Make sure the output directory exists
            unox.make_file_path(output_filepath)
            np.save(output_filepath, y_data)
            if year > stage_2_cutoff:
                # Save in stage 2 for years later than specified
                output_filepath_stage2 = f'inputfiles/{output_dir}/stage2/y/Y_{year}.npy'
                # Make sure the output directory exists
                unox.make_file_path(output_filepath_stage2)
                np.save(output_filepath_stage2, y_data)
            # Output message
            print(f"Created Y input file for {var} in {year}, saved to {output_filepath}")
        if write_this_year:
            # For writing out a netcdf file
            if output_format in ['nc', 'both']:
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
    # Verify `var` is in the dataset
    udata.verify_var(xr_dataset, var)
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
    # Verify `var` is in the dataset
    udata.verify_var(xr_dataset, var)
    # Note the variable attributes
    var_attrs = xr_dataset[var].attrs
    # Scale the variable
    xr_dataset[var] = xr_dataset[var] * scale_factor
    # Add scale factor to the attributes
    ## Note: `scale_factor` is a protected attribute name in xarray. If used, the variable
    ## will be scaled by that factor when loading with xr.load_dataset() and `scale_factor`
    ## will not show up in the loaded xarray. I'm using `scaled_by` to avoid this confusion.
    var_attrs['scaled_by'] = scale_factor
    # Reapply the variable attributes
    xr_dataset = set_var_attrs(xr_dataset, var, var_attrs)
    return xr_dataset

def add_tm1_var(
    xr_dataset,
    var,
    year,
):
    """
    Add a version of the given variable which is shifted by one day (t-1)
    to the dataset, and drop January 1st from the time coordinate.

    Parameters
    ----------
    xr_dataset : xarray.Dataset
        The dataset containing the variable to shifted.
    var : str
        The variable to be shifted.
    year : int
        The year which xr_dataset covers (between 2005 and 2021).

    Returns
    -------
    xarray.Dataset
        The dataset with the shifted variable.
    """
    # Verify the dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Verify `var` is in the dataset
    udata.verify_var(xr_dataset, var)
    # Note the variable attributes
    var_attrs = xr_dataset[var].attrs
    # Create name for t-1 variable
    var_tm1 = f'{var}_tm1'
    # Create a t-1 shifted version of the variable
    xr_dataset[var_tm1] = xr_dataset[var].shift(time=1)
    # Add shifted_from to the attributes
    var_attrs['shifted_from'] = var
    # Check for stage 2 variable
    var_s2 = f'{var}_s2'
    if var_s2 in xr_dataset.data_vars:
        # Note the variable attributes
        var_s2_attrs = xr_dataset[var].attrs
        # Create name for t-1 variable
        var_s2_tm1 = f'{var_s2}_tm1'
        # Create a t-1 shifted version of the variable
        xr_dataset[var_s2_tm1] = xr_dataset[var_s2].shift(time=1)
        # Add shifted_from to the attributes
        var_s2_attrs['shifted_from'] = var_s2
    # Drop January 1st, as the t-1 variable will have null values on that day
    try:
        xr_dataset = xr_dataset.drop_sel(time=f'{year}-01-01')
    except:
        print(f'\tJanuary 1st, {year} not present in xr_dataset')
    # Reapply the variable attributes
    xr_dataset = set_var_attrs(xr_dataset, var_tm1, var_attrs)
    if var_s2 in xr_dataset.data_vars:
        xr_dataset = set_var_attrs(xr_dataset, var_s2_tm1, var_s2_attrs)
    return xr_dataset

def make_x_input_file(
    year,
    stage_2=True,
    data_dir='/data/high_res',
    chemra_path='emacdonald/unet/datafiles/TROPESS/TROPESS_reanalysis_2hr_no2_sfc_',
    chemra_var='no2',
    insitu_path='US_EPA/NO2/daily_NO2/daily_42602_',
    era5_path='ERA5concatenated',
    scale_factors={'chemra': 1e-3,
                    'sp': 1e-5,
                    'ssrd': 1e-6,
                    'blh': 1e-3},
    stage_2_cutoff=2013,
    output_dir='test_input',
    write_this_year=True,
    output_format='nc',
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
    stage_2 : bool, optional
        Whether or not to make stage 2 in addition to stage 1 for the input.
        Default is True.
    data_dir : str, optional
        Directory where the NOx data are stored. 
        Default is '/data/high_res'.
    chemra_path : str, optional
        Path to the chemical reanalysis data files. 
        Default is 'emacdonald/unet/datafiles/TROPESS/TROPESS_reanalysis_2hr_no2_sfc_'.
    chemra_var : str, optional
        The variable to extract from the dataset. Default is 'no2'
    insitu_path : str, optional
        Path to the insitu data files. Default is 'US_EPA/NO2/daily_NO2/daily_42602_'.
    era5_path : str, optional
        Path to the ERA5 reanalysis data files. Default is 'ERA5concatenated'.
    scale_factors : dict, optional
        Scaling factors for the variables. Default is a dictionary with
        scaling factors for 'chemra', 'sp', 'ssrd', and 'blh'.
    stage_2_cutoff : int, optional
        Year after which input files will also be generated for stage 2. Default is 2013.
    output_dir : str, optional
        Directory inside `inputfiles/` where the output x input file will be saved.
        Default is `'test_input'`.
    write_this_year : bool, optional
        Whether to write the data for this year or just return the xarray without writing to file.
        Default is True.
    output_format : str, optional
        Whether to save netcdf files ('nc'), numpy arrays ('npy'), or 'both'.
        Default is 'nc'. Irrelevant if `write_this_year` is False.
    overwrite : bool, optional
        Whether to overwrite existing netcdf files. Default is True.
    **kwargs : dict, optional
        Additional keyword arguments (not used).

    Returns
    -------
    x_data : xarray.Dataset
        The x input data for the specified year.
    """
    # Assemble the file path for the chemical reanalysis data
    chemra_filepath = f'{data_dir}/{chemra_path}{year}.nc'
    # Verify the path
    chemra_filepath = verify_path(chemra_filepath)
    # Load chemical reanalysis data
    # chemra = xr.load_dataset(chemra_filepath)
    chemra = xr.open_dataset(chemra_filepath)
    # If level dimension present, sum across levels
    if "lev" in list(chemra.coords):
        print("level dimension detected")
        chemra = chemra.sum("lev")
    # Regularize the data depending on the source
    if chemra_path=='emacdonald/unet/datafiles/TROPESS/TROPESS_reanalysis_2hr_no2_sfc_':
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
    chemra = scale_xr_var(chemra, chemra_var, scale_factors['chemra'])
    # Find the number of days in the year
    ndays = len(chemra.coords['time'])
    # Fix the time coordinate to match the year
    if chemra_path=='emacdonald/unet/datafiles/TROPESS/TROPESS_reanalysis_2hr_no2_sfc_':
        # Save the time attributes
        time_attrs = chemra['time'].attrs
        # For an unexplained reason, the year in all TCR-2 files is always 2005.
        chemra.coords['time'] = pd.date_range(f"{year}-01-01", periods=ndays)
        # Reapply the time attributes
        chemra['time'].attrs = time_attrs
    
    # Combine chemical reanalysis and insitu data for stage 2
    if stage_2 and year > stage_2_cutoff:
        stages=[1,2]
        print(f'\tAdding stage 2 data for {chemra_var} in {year}')
        # Assemble the file path for the insitu data
        epa_filepath = f'{data_dir}/{insitu_path}{year}.csv'
        # Verify the path
        epa_filepath = verify_path(epa_filepath)
        # Combine chemical reanalysis and insitu data
        chemra = fill_w_insitu(chemra, epa_filepath)
    else:
        stages=[1]
    
    # Interpolate to latitude and longitude grid
    chemra = chemra.interp(lat=lats, lon=lons, method='slinear')

    # Get the time-shifted variable (day t-1)
    previousday = chemra.copy()
    # Fix rounding
    previousday.coords['time'] = (previousday.coords['time'] + 1).dt.ceil('D')
    # Rename t-1 variable
    chemra_var_tm1 = chemra_var+'_tm1'
    previousday = previousday.rename({chemra_var: chemra_var_tm1})

    # Add the chemical reanalysis data for the previous day (t-1)
    chemra = add_tm1_var(chemra, chemra_var, year)

    # Add the other variables from the ERA5 dataset
    for variable in era5_vars_list:
        # Assemble the file path for the ERA5 variable
        era5_var_filepath = f'{data_dir}/{era5_path}/{year}{variable}.nc'
        # Verify the path
        era5_var_filepath = verify_path(era5_var_filepath)
        # Load the ERA5 variable dataset
        # Note: The variable name in the dataset is assumed to be the same as `variable`
        era5_var = xr.load_dataset(era5_var_filepath)
        # Drop the `number` coordinate
        era5_var = era5_var.drop_vars('number')
        # Rename coordinates to match the other datasets
        era5_var = era5_var.rename({'valid_time': 'time', 'latitude': 'lat', 'longitude': 'lon'})
        # Drop January 1st, as the t-1 variable will have null values on that day
        era5_var = era5_var.drop_sel(time=f'{year}-01-01')
        # Add the variable to the xarray
        ## Note: This assumes that the coordinates are the same
        ## which is true in this case as the lat lon arrays used to interpolate the
        ## chemra data were used to interpolate the ERA5 data upon their concatenation
        chemra[variable] = era5_var[variable]
    
    # Convert calendar to 'noleap' to remove February 29th
    input_netcdf_xr = chemra.convert_calendar('noleap')

    # Scale some variables to make orders of magnitude more similar
    for variable in era5_vars_list:
        if variable in scale_factors.keys():
            input_netcdf_xr = scale_xr_var(input_netcdf_xr, variable, scale_factors[variable])

    # Get a list of the variables in the dataset
    datavars = list(input_netcdf_xr.data_vars)
    all_datavars = list(input_netcdf_xr.data_vars)
    # Remove `lsm` from the list of datavars
    datavars.remove('lsm')
    all_datavars.remove('lsm')
    # Prepare data to be saved to numpy array files
    if stage_2 and year > stage_2_cutoff:
        # Assemble the names of the stage 2 variables
        chemra_var_s2 = f'{chemra_var}_s2'
        chemra_var_s2_tm1 = f'{chemra_var}_s2_tm1'
        datavars_s2 = list(input_netcdf_xr.data_vars)
        datavars_s2.remove('lsm')
        datavars_s2.remove(chemra_var)
        datavars_s2.remove(chemra_var_tm1)
        # Prepare a separate numpy array for stage 2
        xnp_s2 = np.ndarray([364, 56, 120, len(datavars_s2)])  # Adjust dimensions as needed
        # Fill the numpy array with data from the xarray Dataset
        for i in range(len(datavars_s2)):
            xnp_s2[:, :, :, i] = input_netcdf_xr[datavars_s2[i]].values
        # Remove stage 2 variables from the datavars list
        datavars.remove(chemra_var_s2)
        datavars.remove(chemra_var_s2_tm1)
    else:
        datavars_s2 = []
    print('all_datavars:',all_datavars)
    print('datavars:',datavars)
    # Create an empty numpy array to hold the data
    xnp = np.ndarray([364, 56, 120, len(datavars)])  # Adjust dimensions as needed
    # Fill the numpy array with data from the xarray Dataset
    for i in range(len(datavars)):
        xnp[:, :, :, i] = input_netcdf_xr[datavars[i]].values

    # Create a dictionary of global attributes
    g_attr_dict={
        'x_vars': all_datavars,
        'x1_vars': datavars,
        'x2_vars': datavars_s2,
        'data_dir': data_dir,
        'chemra_path': chemra_path,
        'insitu_path': insitu_path,
        'era5_path': era5_path,
        'stages': stages,
    }
    # Write out results
    if not isinstance(output_dir, type(None)):
        # Create metadata file
        meta_dict = make_input_metadata_file(
            input_netcdf_xr,
            output_dir=output_dir,
            g_attrs=g_attr_dict,
        )
        # Save the data to file
        # For writing out a numpy file
        if output_format in ['npy', 'both']:
            for stage in stages:
                # Assemble the file path
                output_filepath = f'inputfiles/{output_dir}/stage{stage}/x/X_{year}.npy'
                # Make sure the output directory exists
                unox.make_file_path(output_filepath)
                # Choose the correct array to save
                if stage == 1:
                    np.save(output_filepath, xnp)
                elif stage == 2:
                    np.save(output_filepath, xnp_s2)
                # Output message
                print(f"Created X input file for stage {stage} in {year}, saved to {output_filepath}")
        if write_this_year:
            # For writing out a netcdf file
            if output_format in ['nc', 'both']:
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
                print(f"Saved x input data to {output_filepath}")
                return xr.load_dataset(output_filepath), g_attr_dict
    return input_netcdf_xr, g_attr_dict

@unox.time_this
def fill_w_insitu(
    xr_dataset,
    insitu_filepath, 
    var='no2',
):
    """
    Add stage 2 for the variable in an xarray Dataset using available insitu data.

    Given an xarray Dataset with reanalysis data, duplicate the specified variable and
    replace values of that duplicated variable when and where there is available 
    insitu data in the provided filepath, to be used for stage 2 of training the unet.

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
    # Make a new variable to store the stage 2 data, filled with insitu
    var_s2 = f'{var}_s2'
    # Make a deep copy so that changes to `var_s2` don't affect `var`
    xr_dataset[var_s2]= xr_dataset[var].copy(deep=True)
    # Save the variable attributes
    var_s2_attrs = xr_dataset[var_s2].attrs
    # Verify the insitu file path
    insitu_filepath = verify_path(insitu_filepath)
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
    in1 = xr_dataset[var_s2].where((xr_dataset.lat >= np.min(lats)), drop=True)
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
            xr_dataset[var_s2].loc[{'time': insitu_keys[i], 'lon': pt.lon, 'lat': pt.lat}] = values[j]
    # Add attribute to note which variable this is from
    var_s2_attrs['insitu_filled_from'] = var
    # Reapply the variable attributes
    xr_dataset = set_var_attrs(xr_dataset, var_s2, var_s2_attrs)
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
    # Create an empty array to hold y data
    y_data_array = []
    for year in years:
        print(f"\tCreating y input data for {var} in {year}...")
        y_data, g_attr_dict = make_y_input_file(
            year=year, 
            var=var,
            output_dir=output_dir,
            write_this_year=False,
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
    stage_2=True,
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
    stage_2 : bool, optional
        Whether or not to make stage 2 in addition to stage 1 for the input.
        Default is True.
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
        print(f"\tCreating x input file for {year}...")
        x_data, g_attr_dict = make_x_input_file(
            year=year,
            stage_2=stage_2,
            stage_2_cutoff=stage_2_cutoff,
            output_dir=output_dir,
            write_this_year=False,
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

@unox.time_this
def make_all_input_files(
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
    input_netcdf_xr : xarray.Dataset
        The combined input data for both x and y.
    """
    print("Note: It may take around an hour to generate all input files.")
    # Make sure the output directory exists
    if not os.path.exists(f'inputfiles/{output_dir}'):
        os.makedirs(f'inputfiles/{output_dir}')
    # Create y input data
    print("Creating y input data...")
    input_netcdf_xr = make_all_y_input_files(
        output_dir=output_dir,
        sort=False,
        **kwargs,
    )
    # Create x input data
    print("Creating x input data...")
    input_netcdf_xr = make_all_x_input_files(
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
    input_set,
    output_dir=None,
    g_attrs=None,
    overwrite=True,
):
    """
    Create a metadata file for the dataset in the given directory.

    Gather the metadata from the given dataset, format it, and output
    to a clear-text file that can be easily read.

    Parameters
    ----------
    input_set : str, xr.Dataset
        Directory inside `inputfiles/` where the dataset is found and 
        in which the metadata file will be saved, or the xarray Dataset

    Returns
    -------
    metadata_dict : dict
        The metadata dictionary that was saved to the json file.
        Has the format:
    ```json
    {
        "years": {
            "x": [
                2005,
                ...
                2020
            ],
            "y": [
                2005,
                ...
                2020
            ]
        },
        "y_var": "nox",
        "emiss_dir": "/data/high_res/t106",
        "emiss_pre": "nox_",
        "emiss_post": "_t106_US.nc",
        "nan_fill": 0,
        "stage_2_cutoff": 2013,
        "x_vars": [
            "no2",
            ...
            "ssrd"
        ],
        "data_dir": "/data/high_res",
        "chemra_path": "emacdonald/unet/datafiles/TROPESS/TROPESS_reanalysis_2hr_no2_sfc_",
        "insitu_path": "US_EPA/NO2/daily_NO2/daily_42602_",
        "era5_path": "ERA5concatenated",
        "stages": [
            1,
            2
        ]
    }
    ```
    """
    # Verify input_set is a string or xr.Dataset
    if isinstance(input_set, str):
        # Check whether the given input_set exists in 'inputfiles/'
        xr_path = f'inputfiles/{input_set}/{input_set}.nc'
        if not os.path.exists(xr_path):
            raise ValueError(f'File {xr_path} does not exist.')
        # Load the dataset
        xr_dataset = xr.load_dataset(xr_path)
    elif isinstance(input_set, xr.Dataset):
        xr_dataset = input_set
    # Verify the dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # If the metadata file already exists, load it
    if not isinstance(output_dir, type(None)):
        # Assemble the filepath for the metadata file
        output_filepath = 'inputfiles/' + output_dir + '/input_metadata.json'
        if os.path.exists(output_filepath):
            with open(output_filepath, 'r') as f:
                metadata_dict = json.load(f)
                isNew = False
        else:
            isNew = True
            # Make sure the output directory exists
            unox.make_file_path(output_filepath)
    else:
        isNew = True
    if isNew:
        metadata_dict = {
            'years': {
                'x': [],
                'y': [],
            },
        }
    # Get a list of years present in the dataset
    years = udata.get_years(xr_dataset)
    # Check for global attributes
    if isinstance(g_attrs, type(None)):
        g_attrs = xr_dataset.attrs
    # Check whether `lsm` is in the list of data variables
    if 'lsm' in list(xr_dataset.data_vars):
        # Add `lsm: True` to the global attributes
        g_attrs['lsm'] = 'True'
    else:
        g_attrs['lsm'] = 'False'
    # Add select global attributes to the metadata dictionary
    for g_attr in [
        'y_var',
        'x_vars',
        'description',
        'data_dir',
        'chemra_path',
        'insitu_path',
        'era5_path',
        'modification_date',
        'emiss_dir',
        'emiss_pre',
        'emiss_post',
        'nan_fill',
        'stage_2_cutoff',
        'stages',
        'lsm',
    ]:
        if g_attr in g_attrs:
            # Add to metadata dictionary
            metadata_dict[g_attr] = g_attrs[g_attr]
            # If x_vars or y_var, also add year
            if g_attr == 'x_vars':
                metadata_dict['years']['x'] = metadata_dict['years']['x'] + years
            elif g_attr == 'y_var':
                metadata_dict['years']['y'] = metadata_dict['years']['y'] + years
    ## Add the attributes and years to the metadata dictionary
    # Check if the attrs match and decide whether to overwrite
    # if isNew == False and metadata_dict[x_or_y+'_attrs'] != attr_dict:
    #     warnings.warn(f'Metadata attributes for {x_or_y} {year} input files do not match the existing metadata. Overwriting existing attributes.')
    # Sort the list of years in ascending order, removing duplicates
    metadata_dict['years']['x'] = sorted(list(set(metadata_dict['years']['x'])))
    metadata_dict['years']['y'] = sorted(list(set(metadata_dict['years']['y'])))

    # Output the metadata dictionary to a json file
    if not isinstance(output_dir, type(None)):
        with open(output_filepath, 'w') as file:
            file.write(json.dumps(metadata_dict, indent=4))
    return metadata_dict

def make_input_config(
    config_name,
    input_set = 'no2_sample_input',
    grid_size = [56, 120],
    x_vars = [
        'no2',
        'no2_tm1',
        'u10',
        'v10',
        'blh',
        'sp',
        'skt',
        't2m',
        'ssrd',
    ],
    stage_2 = True,
    stage_2_cutoff = 2013,
    lsm_vars = [
        # 'nox',
        # 'no2',
        # 'no2_tm1',
        # 'no2_s2',
        # 'no2_s2_tm1',
        # 'u10',
        # 'v10',
        # 'blh',
        # 'sp',
        # 'skt',
        # 't2m',
        # 'ssrd',
    ],
    zfi_vars = [
        # 'nox',
        # 'no2',
        # 'no2_tm1',
        # 'no2_s2',
        # 'no2_s2_tm1',
        # 'u10',
        # 'v10',
        # 'blh',
        # 'sp',
        # 'skt',
        # 't2m',
        # 'ssrd',
    ],
    overwrite=False,
    **kwargs,
):
    """
    Create a configuration file for using input data with the Unet model.

    Parameters
    ----------
    config_name : str
        Name of the configuration file to be created.
    input_set : str or xr.Dataset, optional
        Directory inside `inputfiles/` where the dataset is found, or the xarray Dataset.
        Default is 'no2_sample_input'.
    grid_size : list of int, optional
        The number of grid cells to have in [latitude, longitude] when running the Unet model.
        Default is [56, 120].
    x_vars : list of str, optional
        List of variable names to be used as input features for the model.
        Default is a list of common meteorological and chemical variables.
    stage_2 : bool, optional
        Whether or not stage 2 should be run with the Unet model.
        Default is True.
    stage_2_cutoff : int, optional
        Year after which stage 2 data will be used.
        Default is 2013.
    lsm_vars : list of str, optional
        List of variable names that should use land-sea mask.
        Default is ['no2', 'no2_tm1'].
    zfi_vars : list of str, optional
        List of variable names that should use zero-fill mask.
        Default is ['t2m'].
    **kwargs : dict, optional

    Returns
    -------
    config_dict : dict
        The configuration dictionary that was saved to the json file.
    """
    # Verify argument types
    if not isinstance(config_name, str):
        raise TypeError(f"config_name must be a string. Got type: {type(config_name)}")
    # Verify input_set is a string or xr.Dataset
    if isinstance(input_set, str):
        # Check whether the given input_set exists in 'inputfiles/'
        xr_path = f'inputfiles/{input_set}/{input_set}.nc'
        if not os.path.exists(xr_path):
            raise ValueError(f'File {xr_path} does not exist.')
        # Load the dataset
        xr_dataset = xr.load_dataset(xr_path)
    elif isinstance(input_set, xr.Dataset):
        xr_dataset = input_set
    else:
        raise TypeError(f"input_set must be a string or xarray.Dataset. Got type: {type(input_set)}")
    if not isinstance(grid_size, list):
        raise TypeError(f"grid_size must be a list of integers. Got type: {type(grid_size)}")
    if not isinstance(x_vars, list):
        raise TypeError(f"x_vars must be a list of strings. Got type: {type(x_vars)}")
    if not isinstance(stage_2, bool):
        raise TypeError(f"stage_2 must be a boolean. Got type: {type(stage_2)}")
    if not isinstance(stage_2_cutoff, int):
        raise TypeError(f"stage_2_cutoff must be an integer. Got type: {type(stage_2_cutoff)}")
    if not isinstance(lsm_vars, list):
        raise TypeError(f"lsm_vars must be a list of strings. Got type: {type(lsm_vars)}")
    if not isinstance(zfi_vars, list):
        raise TypeError(f"zfi_vars must be a list of strings. Got type: {type(zfi_vars)}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"overwrite must be a boolean. Got type: {type(overwrite)}")
    # Verify the dataset
    xr_dataset = udata.verify_dataset(xr_dataset)
    # Verify that grid_size has exactly 2 integers
    if not len(grid_size) == 2:
        raise TypeError(f'Expected `grid_size` to have a length of 2. Got length of {len(grid_size)}: {grid_size}')
    else:
        if isinstance(grid_size[0], int):
            n_lats = grid_size[0]
        else:
            raise TypeError(f"Number of latitudes in `grid_size` must be an integer. Got type: {type(grid_size[0])}")
        if isinstance(grid_size[1], int):
            n_lons = grid_size[1]
        else:
            raise TypeError(f"Number of longitudes in `grid_size` must be an integer. Got type: {type(grid_size[1])}")
    # Verify that `grid_size` is not larger than the lat-lon grid in xr_dataset
    xr_n_lats = xr_dataset.sizes['lat']
    xr_n_lons = xr_dataset.sizes['lon']
    if n_lats > xr_n_lats:
        raise ValueError(f'Requested length of latitude grid ({n_lats}) cannot exceed length of latitude dimension in the given netcdf ({xr_n_lats}).')
    if n_lons > xr_n_lons:
        raise ValueError(f'Requested length of longitude grid ({n_lons}) cannot exceed length of longitude dimension in the given netcdf ({xr_n_lons}).')
    # Verify that all x_vars are in the dataset
    for var in x_vars:
        udata.verify_var(xr_dataset, var)
    # Verify that stage 2 exists in the dataset
    if not 2 in xr_dataset.attrs.get('stages', []):
        stage_2 = False
        print('Stage 2 not found in dataset. Setting stage_2 to False in configuration.')
    # Verify that stage_2_cutoff is a year that exists in the dataset
    years = udata.get_years(xr_dataset)
    if stage_2_cutoff not in years:
        raise ValueError(f'stage_2_cutoff {stage_2_cutoff} not found in dataset years: {years}')
    # Verify that the lsm_vars are in the dataset
    for var in lsm_vars:
        udata.verify_var(xr_dataset, var)
    # Verify that the zfi_vars are in the dataset
    for var in zfi_vars:
        udata.verify_var(xr_dataset, var)
    # Build the dictionary
    config_dict = {
        'input_set': input_set,
        'grid_size': grid_size,
        'x_vars': x_vars,
        'stage_2': stage_2,
        'stage_2_cutoff': stage_2_cutoff,
        'lsm_vars': lsm_vars,
        'zfi_vars': zfi_vars,
    }
    # Check whether the configuration file already exists
    config_filepath = f'inputfiles/_input_configs/{config_name}.json'
    if os.path.exists(config_filepath) and overwrite == False:
        # Ask whether to overwrite the existing file
        overwrite = unox.interpret_user_input(input(f'Configuration file {config_filepath} already exists. Overwrite? (y/n)'))
        if not overwrite:
            print('Aborting configuration file creation.')
            return
    # Save the configuration dictionary to a json file
    with open(config_filepath, 'w') as file:
        file.write(json.dumps(config_dict, indent=4))
    print(f'Saved configuration file to {config_filepath}')
    return config_dict