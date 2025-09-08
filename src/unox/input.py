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

# emiss = Emissions (TCR-2 t106)
# chemra = Chemical Reanalysis (TROPESS TCR-2)
# insitu = Insitu data (EPA)
# era5 = ERA5 reanalysis data

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
                'var': var,
                'emiss_dir': emiss_dir,
                'emiss_pre': emiss_pre,
                'emiss_post': emiss_post,
                'scale_factor': scale_factor,
                'nan_fill': nan_fill,
                'stage_2_cutoff': stage_2_cutoff,
            },
            stage=None,
            output_dir=output_dir,
        )
        # Output message
        print(f"Created Y input file for {var} in {year}, saved to {output_filepath}")
    return np.array(y_data)

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
    chemra_filepath = os.path.join(data_dir, f'{chemra_path}{year}.nc')
    # Verify the path
    chemra_filepath = unox.verify_path(chemra_filepath)
    # Load chemical reanalysis data
    # chemra = xr.load_dataset(chemra_filepath)
    chemra = xr.open_dataset(chemra_filepath)
    # If level dimension present, sum across levels
    if "lev" in list(chemra.coords):
        print("level dimension detected")
        chemra = chemra.sum("lev")
    # Change longitude coordinate convention to match other data
    # chemra.coords['lon'] = (chemra.coords['lon'] + 180) % 360 - 180
    if chemra_path=='TROPESS/TROPESS_reanalysis_2hr_no2_sfc_':
        chemra.coords['lon'] = udata.shift_lon_arr(chemra.coords['lon'])
    # Resample and rescale
    chemra = chemra.resample(time='d').mean() / scale_factors['chemra']
    # Find the number of days in the year
    ndays = len(chemra.coords['time'])
    # Fix the time coordinate to match the year
    if chemra_path=='TROPESS/TROPESS_reanalysis_2hr_no2_sfc_':
        # For an unexplained reason, the year in all TCR-2 files is always 2005.
        chemra.coords['time'] = pd.date_range(f"{year}-01-01", periods=ndays)
    
    # Combine chemical reanalysis and insitu data for stage 2
    if stage == 2 and year > stage_2_cutoff:
        # Assemble the file path for the insitu data
        epa_filepath = os.path.join(data_dir, f'{insitu_path}{year}.csv')
        # Verify the path
        epa_filepath = unox.verify_path(epa_filepath)
        # Combine chemical reanalysis and insitu data
        chemra = fill_w_insitu(chemra, epa_filepath)
    
    # Interpolate to latitude and longitude grid
    lats, lons = unox.load_lats_lons()
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
    # print(datavars)
    # Create an empty numpy array to hold the data
    xnp = np.ndarray([364, 56, 120, len(datavars)])  # Adjust dimensions as needed
    # Fill the numpy array with data from the xarray Dataset
    for i in range(len(datavars)):
        xnp[:, :, :, i] = x_data[datavars[i]]  # Put it in the numpy array

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
    return xnp

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
    **kwargs : dict, optional
        Additional keyword arguments to pass to the `make_y_input_file` function.

    Returns
    -------
    y_data_array : list of numpy.ndarray
        List of y input data arrays for the specified years.
    """
    # Make sure the output directory exists
    if not os.path.exists(f'inputfiles/{output_dir}/stage1/y'):
        os.makedirs(f'inputfiles/{output_dir}/stage1/y')
    if not os.path.exists(f'inputfiles/{output_dir}/stage2/y'):
        os.makedirs(f'inputfiles/{output_dir}/stage2/y')
    y_data_array = []
    for year in years:
        print(f"Creating y input file for {var} in {year}...")
        y_data = make_y_input_file(
            year=year, 
            var=var,
            output_dir=output_dir,
            **kwargs,
        )
        y_data_array.append(y_data)
    return y_data_array

def make_all_x_input_files(
    years=range(2005, 2021),
    stage=1,
    stage_2_cutoff=2013,
    output_dir='test_input',
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
    **kwargs : dict, optional
        Additional keyword arguments to pass to the `make_x_input_file` function.

    Returns
    -------
    x_data_array : list of xarray.Dataset
        List of x input data arrays for the specified years and stages.
    """
    # Make sure the output directory exists
    if not os.path.exists(f'inputfiles/{output_dir}/stage{stage}/x'):
        os.makedirs(f'inputfiles/{output_dir}/stage{stage}/x')
    x_data_array = []
    for year in years:
        if stage == 2 and year <= stage_2_cutoff:
            # Skip stage 2 for years before the cutoff
            continue
        print(f"Creating x input file for stage {stage} in {year}...")
        x_data = make_x_input_file(
            year=year,
            stage=stage,
            stage_2_cutoff=stage_2_cutoff,
            output_dir=output_dir,
            **kwargs,
        )
        x_data_array.append(x_data)
    return x_data_array

def make_all_input_files(
    years=range(2005, 2021),
    stages=[1, 2],
    output_dir='test_input',
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
    make_all_y_input_files(
        years=years,
        output_dir=output_dir,
        **kwargs,
    )
    # Create x input files for each stage
    for stage in stages:
        print(f"Creating x input files for stage {stage}...")
        make_all_x_input_files(
            years=years,
            stage=stage,
            output_dir=output_dir,
            **kwargs,
        )
    print("Completed making all input files.")

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