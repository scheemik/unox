import numpy as np
import os
import xarray as xr
import pandas as pd
import json
import warnings

import unox.unox as unox
from unox.HPC.data0.paths import verify_path, remove_non_empty_directory, make_file_path
from unox.HPC.data0.dataset import uarray, get_years
from unox.HPC.data0.verify_dataset import verify_dataset, verify_var
from unox.HPC.data0.latlon import shift_lon_arr
import unox.data as udata
from unox.plot_format import pad_extent

# emiss  = Emissions (TCR-2 t106)
# chemra = Chemical Reanalysis (TROPESS TCR-2)
# insitu = Insitu data (USA EPA)
# met    = Meteorological data (ERA5 reanalysis)

# Define a dictionary of the variables to be used for each model variable
era5_vars_list = ['u10', 'v10', 'blh', 'sp', 'skt', 't2m', 'ssrd', 'lsm']
input_vars_dict = {
    'no2': {
        'y_var': 'nox',
        'chemra_var': 'no2',
        'met_vars': era5_vars_list,
        'x_vars': ['no2', 'no2_tm1'] + era5_vars_list,
        'data_sources': {
            'emissions_directory': '/data/high_res/emacdonald/unet/datafiles/t106',
            'emissions_file_prefix': 'nox_',
            'emissions_file_postfix': '_t106_US.nc',
            'chemra_directory': '/data/high_res/emacdonald/unet/datafiles/TROPESS',
            'chemra_file_prefix': 'TROPESS_reanalysis_2hr_no2_sfc_',
            'chemra_file_postfix': '.nc',
            'insitu_directory': '/data/high_res/US_EPA/NO2/daily_NO2',
            'insitu_file_prefix': 'daily_42602_',
            'insitu_file_postfix': '.csv',
            'met_directory': '/data/high_res/ERA5concatenated',
            'met_file_prefix': '',
            'met_file_postfix': '.nc',
        },
    },
    'co': {
        'y_var': 'EmisCO_Total',
        'chemra_var': 'SpeciesConcVV_CO',
        'met_vars': era5_vars_list,
        'x_vars': ['SpeciesConcVV_CO', 'SpeciesConcVV_CO_tm1'] + era5_vars_list,
        'data_sources': {
            'emissions_directory': '',
            'emissions_file_prefix': '',
            'emissions_file_postfix': '',
            'chemra_directory': '',
            'chemra_file_prefix': '',
            'chemra_file_postfix': '',
            'insitu_directory': '/data/high_res/US_EPA/CO/daily_CO',
            'insitu_file_prefix': 'daily_42101_',
            'insitu_file_postfix': '.csv',
            'met_directory': '/data/high_res/ERA5concatenated',
            'met_file_prefix': '',
            'met_file_postfix': '.nc',
        },
    }
}

@unox.time_this
def make_input_file(
    name,
    target_var='no2',
    start_date='2005-01-01',
    end_date='2020-12-31',
    stage_2=True,
    stage_2_cutoff=2013,
    nan_fill=0,
    **kwargs,
):
    """ Make an input file for the Unet model.

        Create a netCDF input file with corresponding metadata `.json` for the Unet model with the specified name and date range.
        The input file will use the parameters specified in the `input_vars_dict` for the target variable.

        Parameters
        ----------
        name : `str`
            The name of the input file to be created (without file extension).
        target_var : `str`, optional
            The target variable for which to create the input file. 
            Must be a key in `input_vars_dict`.
            Default is 'no2'.
        start_date :  `str`, `np.datetime64`, `None`, optional
            First date and time to include in the input file.
            Default is `2005-01-01`.
        end_date : `str`, `np.datetime64`, `None`, optional
            Last date and time to include in the input file.
            Default is `2020-12-31`.
        stage_2 : `bool`, optional
            Whether or not to make stage 2 in addition to stage 1 for the input.
            Default is True.
        stage_2_cutoff : `int`, optional
            Year after which input files will also be generated for stage 2. 
            Default is 2013.
        nan_fill : `float`, optional
            Value to fill NaNs in the dataset. 
            Default is `0`.
        **kwargs : `dict`, optional
            Additional keyword arguments to be passed to the `write_input_netcdf` function.
    """
    # Verify argument types
    if not isinstance(name, str):
        raise TypeError(f"(make_input_file) `name` must be a string. Got type: {type(name)}")
    if not isinstance(target_var, str):
        raise TypeError(f"(make_input_file) `target_var` must be a string. Got type: {type(target_var)}")
    if not isinstance(start_date, (np.datetime64, type(None))):
        try:
            start_date = np.datetime64(start_date)
        except:
            raise TypeError(f"(make_input_file) `start_date` must be a string, `np.datetime64`, or `None`. Got type: {type(start_date)}")
    if not isinstance(end_date, (np.datetime64, type(None))):
        try:
            end_date = np.datetime64(end_date)
        except:
            raise TypeError(f"(make_input_file) `end_date` must be a string, `np.datetime64`, or `None`. Got type: {type(end_date)}")
    if not isinstance(stage_2, bool):
        raise TypeError(f"(make_input_file) `stage_2` must be a boolean. Got type: {type(stage_2)}")
    if not isinstance(stage_2_cutoff, int):
        raise TypeError(f"(make_input_file) `stage_2_cutoff` must be an integer. Got type: {type(stage_2_cutoff)}")
    if not isinstance(nan_fill, (int, float)):
        raise TypeError(f"(make_input_file) `nan_fill` must be a number. Got type: {type(nan_fill)}")
    
    # Verify that the target variable is in the `input_vars_dict`
    input_vars = input_vars_dict.keys()
    if target_var not in input_vars:
        raise ValueError(f"(make_input_file) `target_var` must be one of the following: {input_vars}. Got: {target_var}")
    # Get the parameters for the target variable
    y_var = input_vars_dict[target_var]['y_var']
    chemra_var = input_vars_dict[target_var]['chemra_var']
    met_vars = input_vars_dict[target_var]['met_vars']
    x_vars = input_vars_dict[target_var]['x_vars']
    data_sources = input_vars_dict[target_var]['data_sources']

    # Using the start and end dates, make a list of years for which to find data files
    if isinstance(start_date, type(None)):
        start_date = np.datetime64('2005-01-01')
    if isinstance(end_date, type(None)):
        end_date = np.datetime64('2020-12-31')
    ## Note: The year from a `np.datetime64` will be the years since 1970
    start_year = start_date.astype('datetime64[Y]').astype(int) + 1970
    end_year = end_date.astype('datetime64[Y]').astype(int) + 1970
    years = list(range(start_year, end_year + 1))

    # Loading the latitude and longitude values ahead of time is necessary to make the processing of the chemical reanalysis dataset take significantly less time.
    # Get latitude and longitude values
    lats, lons = unox.load_lats_lons()
    # Get the extent of the lats and lons
    extent = udata.get_extent(lats=lats, lons=lons)
    # Pad the extent
    extent = pad_extent(extent, padding=0.1)

    # Initialize lists of all the necessary files
    emiss_files = []
    chemra_files = []
    insitu_files = []
    met_files = []

    # Verify that all necessary data files exist
    ## This assumes that the data has one file per year
    for year in years:
        # Check for the emissions file
        emiss_filepath = f"{data_sources['emissions_directory']}/{data_sources['emissions_file_prefix']}{year}{data_sources['emissions_file_postfix']}"
        verify_path(emiss_filepath)
        emiss_files.append(emiss_filepath)
        # Check for the chemical reanalysis file
        chemra_filepath = f"{data_sources['chemra_directory']}/{data_sources['chemra_file_prefix']}{year}{data_sources['chemra_file_postfix']}"
        verify_path(chemra_filepath)
        chemra_files.append(chemra_filepath)
        # Check for the insitu file
        insitu_filepath = f"{data_sources['insitu_directory']}/{data_sources['insitu_file_prefix']}{year}{data_sources['insitu_file_postfix']}"
        verify_path(insitu_filepath)
        insitu_files.append(insitu_filepath)
        # Check for the Meteorological files
        for met_var in met_vars:
            met_filepath = f"{data_sources['met_directory']}/{data_sources['met_file_prefix']}{year}{met_var}{data_sources['met_file_postfix']}"
            verify_path(met_filepath)
            met_files.append(met_filepath)
    
    # Create a blank dictionary in which to store the datasets
    ds_dictionary = {
        'ds_emiss': emiss_files,
        'ds_chemra': chemra_files,
        # 'ds_insitu': insitu_files,
        'ds_met': met_files,
    }
    # Create a blank dictionary in which to store the attributes
    # Note that these are strings rather than `None` type as `None` type is not valid in .json files
    attr_dictionary = {
        'ds_emiss': None,
        'ds_chemra': None,
        # 'ds_insitu': None,
        'ds_met': None,
    }
    # Load each dataset and add it to the dictionary
    for key, files in ds_dictionary.items():
        print(f"Loading {key}")
        # Check whether the chemical reanalysis is from TCR-2
        if 'TROPESS_reanalysis_2hr_no2_sfc_' in files[0]:
            # Add the result to the dictionary
            ds_dictionary[key] = process_TROPESS_chemra(
                key,
                files,
                years,
                extent,
                lats,
                lons,
                nan_fill,
            )
        else:
            # Open a multi-file dataset
            ds_dictionary[key] = xr.open_mfdataset(files)
        # Rename the ERA5 latitude and longitude coordinates
        if 'ERA5' in files[0]:
            ds_dictionary[key] = process_ERA5_met(
                ds_dictionary[key],
            )
        # Interpolate to latitude and longitude grid, resample to daily mean, and fill NaNs
        # Time how long this interpolation takes to process
        t1 = pd.Timestamp.now()
        ds_dictionary[key] = ds_dictionary[key].interp(lat=lats, lon=lons).resample(time='d').mean().fillna(nan_fill)
        t2 = pd.Timestamp.now()
        print(f"\tExecution time to interpolate {key}: {t2 - t1}")
        # Save the attributes from that dataset
        attr_dictionary[key] = ds_dictionary[key].attrs

    # Merge all datasets
    print("Merging datasets")
    ds_input = ds_dictionary['ds_emiss']
    for ds_type in ['chemra', 'met']:
        ds_input = ds_input.merge(ds_dictionary[f'ds_{ds_type}'], fill_value=nan_fill, combine_attrs='drop_conflicts')
    
    # Add the chemical reanalysis data for the previous day (t-1)
    if f"{chemra_var}_tm1" in x_vars:
        ds_input = add_tm1_var(ds_input, chemra_var)
    
    # Remove global attributes
    ds_input.attrs = {}

    # Create a dictionary of global attributes
    g_attr_dict={
        'name': name,
        'y_var': y_var,
        'x_vars': x_vars,
        'start_date': str(start_date),
        'end_date': str(end_date),
        'stage_2': stage_2,
        'stage_2_cutoff': stage_2_cutoff,
        'nan_fill': nan_fill,
        'attrs_emiss': attr_dictionary['ds_emiss'],
        'attrs_chemra': attr_dictionary['ds_chemra'],
        # 'attrs_insitu': attr_dictionary['ds_insitu'],
        'attrs_met': attr_dictionary['ds_met'],
    }

    # Set the global attributes
    ds_input = set_global_attrs(ds_input, g_attr_dict)

    # Save out the netcdf file
    ds_input = write_input_netcdf(
        ds_input,
        name,
        **kwargs,
    )
    # Get the attributes from the dataset in a dictionary
    attr_dict = ds_input.attrs
    # Assemble the filepath for the metadata file
    meta_filepath = f"inputfiles/{name}/{name}.json"
    # Make sure that filepath exists
    make_file_path(meta_filepath)
    # Save the dictionary as a metadata .json file
    with open(meta_filepath, 'w') as f:
        json.dump(attr_dict, f, indent=4)

    return ds_input

@unox.time_this
def process_TROPESS_chemra(
    key,
    files,
    years,
    extent,
    lats,
    lons,
    nan_fill,
):
    """ Process TROPESS chemical reanalysis files for input file creation.

        For each TROPESS file, shift the longitude values to match the convention, trim the lat-lon extent, drop unnecessary variables and attributes, resample to daily mean, and concatenate all years together.

        Parameters
        ----------
        key : `str`
            The key in the dataset dictionary corresponding to the chemical reanalysis data (e.g. 'ds_chemra').
        files : `list` of `str`
            List of filepaths for the chemical reanalysis data.
        years : `list` of `int`
            List of years corresponding to the chemical reanalysis files.
        extent : `list` of `float`
            List of latitude and longitude boundaries [lat_min, lat_max, lon_min, lon_max] for trimming the dataset.
        lats : `np.ndarray`
            Array of latitude values for the dataset.
        lons : `np.ndarray`
            Array of longitude values for the dataset.
        nan_fill : `float`
            Value to fill for NaNs in the dataset.
        
        Returns
        -------
        ds_chemra : `xarray.Dataset`
            The processed chemical reanalysis dataset with shifted longitudes, trimmed extent, dropped unnecessary variables and attributes, resampled to daily mean, and concatenated across all years.
    """
    if len(files) != len(years):
        raise ValueError(f"(make_input_file) Number of chemical reanalysis files does not match the number of years. \nNumber of files: {len(files)} \nNumber of years: {len(years)}")
    # Make a list in which to store each year's chemra dataset
    these_ds_chemra = []
    for i in range(len(years)):
        file = files[i]
        year = years[i]
        print(f"Processing {key} file {file}, year {year}")
        # Load the chemical reanalysis dataset
        this_ds_chemra = xr.open_dataset(file)
        # Change longitude coordinate convention to match other data
        this_ds_chemra = shift_lon_arr(this_ds_chemra)
        # Drop the `nv` dimension and the `bnds` variables
        if 'nv' in this_ds_chemra.dims:
            this_ds_chemra = this_ds_chemra.isel(nv=0).drop_vars(['time_bnds', 'lon_bnds', 'lat_bnds'])
        # For time, latitude, and longitude, drop the var+`_bnds` attributes
        for coord in ['time', 'lat', 'lon']:
            if 'bounds' in this_ds_chemra[coord].attrs:
                this_ds_chemra[coord].attrs.pop('bounds')
        # Trim the chemical reanalysis data to the extent of the lat/lon grid
        this_ds_chemra = this_ds_chemra.where(
            (this_ds_chemra.lat >= extent[0]) &
            (this_ds_chemra.lat <= extent[1]) &
            (this_ds_chemra.lon >= extent[2]) &
            (this_ds_chemra.lon <= extent[3]),
            drop=True,
        )
        # Resample the time to days
        this_ds_chemra = this_ds_chemra.resample(time='d').mean()
        # Find the number of days in the year
        ndays = len(this_ds_chemra.coords['time'])
        # Save the time attributes
        time_attrs = this_ds_chemra['time'].attrs
        # For an unexplained reason, the year in all TCR-2 files is always 2005.
        this_ds_chemra.coords['time'] = pd.date_range(f"{year}-01-01", periods=ndays)
        # Reapply the time attributes
        this_ds_chemra['time'].attrs = time_attrs
        these_ds_chemra.append(this_ds_chemra)
    # Concatenate the chemical reanalysis datasets for each year together
    ds_chemra = xr.concat(these_ds_chemra, dim='time')
    return ds_chemra

@unox.time_this
def process_ERA5_met(
    ds_met,
):
    """ Process ERA5 meteorological data for input file creation.

        Rename the latitude and longitude coordinates to match the other datasets and drop the `number` coordinate.

        Parameters
        ----------
        ds_met : `xarray.Dataset`
            The ERA5 meteorological dataset to be processed.
        
        Returns
        -------
        ds_met : `xarray.Dataset`
            The processed ERA5 meteorological dataset with renamed coordinates and dropped `number` coordinate.
    """
    # Rename the ERA5 latitude and longitude coordinates
    ds_met = ds_met.rename({'valid_time': 'time', 'latitude': 'lat', 'longitude': 'lon'})
    # Drop the `number` coordinate
    ds_met = ds_met.drop_vars('number')
    return ds_met

@unox.time_this
def add_tm1_var(
    xr_dataset,
    var,
    year=None,
):
    """ Add a (t-1) version of the given variable to the dataset.
    
        Add a version of the given variable which is shifted by one day (t-1) to the dataset, and drop January 1st from the time coordinate, if applicable.

        Parameters
        ----------
        xr_dataset : `xarray.Dataset`
            The dataset containing the variable to shifted.
        var : `str`
            The variable to be shifted.
        year : `int`, `None`, optional
            The year which xr_dataset covers (between 2005 and 2021).

        Returns
        -------
        xr_dataset : `xarray.Dataset`
            The dataset with the shifted variable added.
    """
    # Verify argument types
    if not isinstance(xr_dataset, xr.Dataset):
        raise TypeError(f"(add_tm1_var) `xr_dataset` must be a `xr.Dataset`. Got type: {type(xr_dataset)}")
    if not isinstance(var, str):
        raise TypeError(f"(add_tm1_var) `var` must be a string. Got type: {type(var)}")
    if not isinstance(year, (int, type(None))):
        raise TypeError(f"(add_tm1_var) `year` must be an integer or `None`. Got type: {type(year)}")

    # Verify the dataset
    xr_dataset = verify_dataset(xr_dataset)
    # Verify `var` is in the dataset
    verify_var(xr_dataset, var)

    # Note the variable attributes
    var_attrs = xr_dataset[var].attrs
    # Create name for t-1 variable
    var_tm1 = f'{var}_tm1'
    # Create a t-1 shifted version of the variable
    xr_dataset[var_tm1] = xr_dataset[var].shift(time=1)
    # Add shifted_from to the attributes
    var_attrs['shifted_from'] = var
    # Add (t-1) to the name in the attributes
    var_attrs['long_name'] = var_attrs.get('long_name', var) + ' (t-1)'
    # Check for stage 2 variable
    var_s2 = f'{var}_s2'
    if var_s2 in xr_dataset.data_vars:
        # Note the variable attributes
        var_s2_attrs = xr_dataset[var_s2].attrs
        # Create name for t-1 variable
        var_s2_tm1 = f'{var_s2}_tm1'
        # Create a t-1 shifted version of the variable
        xr_dataset[var_s2_tm1] = xr_dataset[var_s2].shift(time=1)
        # Add shifted_from to the attributes
        var_s2_attrs['shifted_from'] = var_s2
        # Add (t-1) to the name in the attributes
        var_s2_attrs['long_name'] = var_s2_attrs.get('long_name', var_s2) + ' (t-1)'
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

@unox.time_this
def write_input_netcdf(
    ds_input,
    name,
    g_attr_dict=None,
    overwrite_file=True,
    overwrite_data=True,
    sort=True,
    **kwargs,
):
    """ Write an xarray Dataset to a netcdf file, appending or overwriting as needed.

        Parameters
        ----------
        ds_input : `xarray.Dataset`
            The dataset to write to the netcdf file.
        output_filepath : `str`
            Path to the output netcdf file.
        g_attr_dict : `dict`, optional
            Dictionary of global attributes to add to the dataset if creating a new file.
        overwrite_file : `bool`, optional
            Whether to overwrite the existing netcdf file if it exists.
            Default is True.
        overwrite_data : `bool`, optional
            Whether to overwrite existing data in the netcdf file if there are overlapping times.
            Default is True.
        sort : `bool`, optional
            Whether to sort the xarray before writing to netcdf. Sorting takes a long time.
            Default is True.

        Returns
        -------
        ds_input : `xarray.Dataset`
            The dataset that was written to the netcdf file.
    """
    output_filepath = f"inputfiles/{name}/{name}.nc"
    # Check whether the netcdf file already exists
    if os.path.exists(output_filepath) and overwrite_file==False:
        # Load the existing netcdf file
        existing_ds = xr.load_dataset(output_filepath)
        # Verify the dataset
        try:
            existing_ds = verify_dataset(existing_ds)
            skip_existing = False
        except:
            print(f"Existing netcdf file at {output_filepath} is not a valid xarray Dataset. Overwriting with new dataset.")
            skip_existing = True
        if skip_existing == False:
            # Check if the existing dataset and the new one have the same lat/lon values
            existing_lats = existing_ds.coords['lat'].values
            existing_lons = existing_ds.coords['lon'].values
            new_lats = ds_input.coords['lat'].values
            new_lons = ds_input.coords['lon'].values
            if not np.array_equal(existing_lats, new_lats):
                raise ValueError(f"(write_input_netcdf) Latitude values of the existing netcdf file and the new data do not match. \nExisting lats: \n{existing_lats} \nNew lats: \n{new_lats}")
            if not np.array_equal(existing_lons, new_lons):
                raise ValueError(f"(write_input_netcdf) Longitude values of the existing netcdf file and the new data do not match. \nExisting lons: \n{existing_lons} \nNew lons: \n{new_lons}")
            # Get lists of variables from both datasets
            new_vars = list(ds_input.data_vars)
            existing_vars = list(existing_ds.data_vars)
            # Find the variables in common, if any
            shared_vars = set(new_vars) & set(existing_vars)
            if len(shared_vars) > 0:
                # Check whether any time values are already present in the existing dataset
                existing_times = set(existing_ds.coords['time'].values)
                new_times = set(ds_input.coords['time'].values)
                overlapping_times = existing_times.intersection(new_times)
                if len(overlapping_times) > 1:
                    # Get the first and last overlapping times
                    first_overlap = min(overlapping_times)
                    last_overlap = max(overlapping_times)
                    # Format them to YYYY-MM-DD
                    first_overlap = pd.to_datetime(str(first_overlap)).strftime('%Y-%m-%d')
                    last_overlap = pd.to_datetime(str(last_overlap)).strftime('%Y-%m-%d')
                if overlapping_times and overwrite_data==False:
                    raise ValueError(f"(write_input_netcdf) The new data overlaps with the existing file in {output_filepath} between {first_overlap} and {last_overlap}. To overwrite, set overwrite_data=True.")
                elif overlapping_times and overwrite_data==True:
                    print(f"Overwriting overlapping data in {output_filepath} for times between {first_overlap} and {last_overlap}.")
                    # Remove the overlapping times from the existing dataset
                    existing_ds = existing_ds.drop_sel(time=list(overlapping_times))
                # Concatenate the new data with the existing dataset along the time dimension
                ds_input = xr.concat([existing_ds, ds_input], dim='time')
            else:
                # Merge the datasets
                ds_input = xr.merge([existing_ds, ds_input])
            # Sort the dataset by time
            if sort:
                print("Sorting the dataset by time.")
                ds_input = ds_input.sortby('time')
    # Add a description
    ds_input.attrs['description'] = f"Input data for the Unet model."
    # Make sure the output directory exists
    make_file_path(output_filepath)
    # Save the netcdf file
    ds_input.to_netcdf(output_filepath)
    return ds_input

def set_global_attrs(
    xr_dataset,
    attr_dict,
):
    """ Add attributes to an xarray Dataset.

        Parameters
        ----------
        xr_dataset : `xarray.Dataset`
            The dataset to which attributes will be added.
        attr_dict : `dict`
            Dictionary of attributes to add to the dataset.

        Returns
        -------
        `xarray.Dataset`
            The dataset with added attributes.
    """
    # Verify the dataset
    xr_dataset = verify_dataset(xr_dataset)
    # Verify the attribute dictionary
    if not isinstance(attr_dict, dict):
        raise TypeError(f"(set_global_attrs) `attr_dict` must be a dictionary. Got type: {type(attr_dict)}")
    # Add each attribute to the dataset
    xr_dataset = xr_dataset.assign_attrs(attr_dict)
    # Certain data types cannot be saved in netcdf files
    # Convert the data types and save extra attributes to note the original types
    for key, value in attr_dict.items():
        # Convert boolean types to integer
        if isinstance(value, bool):
            value = int(value)
            xr_dataset.attrs[f'{key}_original_type'] = 'bool'
        elif isinstance(value, type({})):
            value = str(value)
            xr_dataset.attrs[f'{key}_original_type'] = 'dict'
        elif isinstance(value, type(None)):
            value = 'None'
            xr_dataset.attrs[f'{key}_original_type'] = 'NoneType'
        elif isinstance(value, (np.datetime64, pd.Timestamp)):
            value = str(value)
            xr_dataset.attrs[f'{key}_original_type'] = 'datetime'
        xr_dataset.attrs[key] = value
    # Update the modification date
    xr_dataset.attrs['modification_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    return xr_dataset

def set_var_attrs(
    xr_dataset,
    var,
    attr_dict,
):
    """ Add attributes to a variable in an xarray Dataset.

        Parameters
        ----------
        xr_dataset : `xarray.Dataset`
            The dataset containing the variable to which attributes will be added.
        var : `str`
            The variable to which attributes will be added.
        attr_dict : `dict`
            Dictionary of attributes to add to the variable.

        Returns
        -------
        `xarray.Dataset`
            The dataset with the variable having added attributes.
        
        Examples
        --------
        >>> ds = xr.Dataset(
        ...     {'var1': (('time', 'lat', 'lon'), np.random.rand(10, 5, 5))},
        ...     coords={
        ...         'time': pd.date_range('2019-01-01', periods=10),
        ...         'lat': np.linspace(-90, 90, 5),
        ...         'lon': np.linspace(-180, 180, 5)
        ...     },
        ... )
        >>> attr_dict = {'units': 'ppb', 'long_name': 'Variable 1'}
        >>> ds = set_var_attrs(ds, 'var1', attr_dict)
        >>> print(ds['var1'].attrs)
        {'units': 'ppb', 'long_name': 'Variable 1'}
    """
    # Verify argument types
    xr_dataset = verify_dataset(xr_dataset)
    if not isinstance(var, str):
        raise TypeError(f"(set_var_attrs) `var` must be a string. Got type: {type(var)}")
    if not isinstance(attr_dict, dict):
        raise TypeError(f"(set_var_attrs) `attr_dict` must be a dictionary. Got type: {type(attr_dict)}")

    # Verify `var` is in the dataset
    verify_var(xr_dataset, var)
    # Add each attribute to the variable
    for key, value in attr_dict.items():
        xr_dataset[var].attrs[key] = value
    return xr_dataset

###############################################################
# Can I delete what is below? Have all the functions been replaced by the above?

def x_or_y_var(
    var,
):
    """ Return whether the given variable is an x or y variable.

        Parameters
        ----------
        var : `str`
            The variable to check.

        Returns
        -------
        x_or_y : `str`
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
        raise TypeError(f"(x_or_y_var) `var` must be a string. Got type: {type(var)}")
    # Check if the variable is in the input_vars_dict
    for key in input_vars_dict.keys():
        if var in input_vars_dict[key]['x_vars']:
            return 'x'
        elif var in input_vars_dict[key]['y_vars']:
            return 'y'
    raise ValueError(f"(x_or_y_var) Variable '{var}' not recognized. Available variables in input_vars_dict: {input_vars_dict}")

def get_input_index(
    var,
):
    """ Get the index of the given variable in the input array.

        Parameters
        ----------
        var : `str`
            The variable to check.

        Returns
        -------
        index : `int`
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
        raise TypeError(f"(get_input_index) Variable must be a string. Got type: {type(var)}")
    # Check if the variable is in the input_vars_dict
    for key in input_vars_dict.keys():
        if var in input_vars_dict[key]['x_vars']:
            return input_vars_dict[key]['x_vars'].index(var)
        elif var in input_vars_dict[key]['y_vars']:
            return input_vars_dict[key]['y_vars'].index(var)
    raise ValueError(f"(get_input_index) Variable '{var}' not recognized. Available variables in input_vars_dict: {input_vars_dict}")

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
    """ Create a y input file for the Unet model for the given year.

        The array in the generated file will have these dimensions:
        - time: 364 (or 365 for leap years)
            - One day less than usual to allow for t-1 variable
        - lat: length depends on the latitude grid
        - lon: length depends on the longitude grid
        - var: 1 (a dummy dimension to match the x input files)

        Parameters
        ----------
        year : `int`
            The year for which to create the y input file (between 2005 and 2021).
        var : `str`, optional
            The variable to extract from the dataset. Default is 'nox'.
        emiss_dir : `str`, optional
            Directory where the emissions data are stored. 
            Default is '/data/high_res/emacdonald/unet/datafiles/t106'.
        emiss_pre : `str`, optional
            Prefix for the emissions input file name. Default is 'nox_'.
        emiss_post : `str`, optional
            Extension for the input file name. Default is '_t106_US.nc'.
        scale_factor : `float`, optional
            Factor by which to scale the data. Default is 1e12.
        nan_fill : `float`, optional
            Value to fill NaNs in the dataset. Default is 0.
        stage_2_cutoff : `int`, optional
            Year after which the data will also be saved in stage 2.
        output_dir : `str`, optional
            Directory inside `inputfiles/` where the output y input file will be saved.
            Default is `'test_input'`.
        write_this_year : `bool`, optional
            Whether to write the data for this year or just return the xarray without writing to file.
            Default is True.
        output_format : `str`, optional
            Whether to save netcdf files ('nc'), numpy arrays ('npy'), or 'both'.
            Default is 'nc'. Irrelevant if `write_this_year` is False.
        overwrite : `bool`, optional
            Whether to overwrite existing netcdf files. Default is True.
        **kwargs : `dict`, optional
            Additional keyword arguments (not used).

        Returns
        -------
        input_netcdf_xr : `xarray.Dataset`
            The y input data for the specified year.
        g_attr_dict : `dict`
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
            make_file_path(output_filepath)
            np.save(output_filepath, y_data)
            if year > stage_2_cutoff:
                # Save in stage 2 for years later than specified
                output_filepath_stage2 = f'inputfiles/{output_dir}/stage2/y/Y_{year}.npy'
                # Make sure the output directory exists
                make_file_path(output_filepath_stage2)
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

def scale_xr_var(
    xr_dataset,
    var,
    scale_factor,
):
    """ Scale a variable in an xarray Dataset by a given factor.

        Parameters
        ----------
        xr_dataset : `xarray.Dataset`
            The dataset containing the variable to be scaled.
        var : `str`
            The variable to be scaled.
        scale_factor : `float`
            The factor by which to scale the variable.

        Returns
        -------
        `xarray.Dataset`
            The dataset with the scaled variable.
    """
    # Verify the dataset
    xr_dataset = verify_dataset(xr_dataset)
    # Verify `var` is in the dataset
    verify_var(xr_dataset, var)
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
    """ Create an x input file for the Unet model for the given year and stage.

        The array in the file will have these dimensions:
        - time: 364 (or 365 for leap years)
            - One day less than usual to allow for t-1 variable
        - lat: length depends on the latitude grid
        - lon: length depends on the longitude grid
        - var: 9 variables (e.g., 'no2', 'u10', 'v10', etc.)

        Parameters
        ----------
        year : `int`
            The year for which to create the x input file.
        stage_2 : `bool`, optional
            Whether or not to make stage 2 in addition to stage 1 for the input.
            Default is True.
        data_dir : `str`, optional
            Directory where the NOx data are stored. 
            Default is '/data/high_res'.
        chemra_path : `str`, optional
            Path to the chemical reanalysis data files. 
            Default is 'emacdonald/unet/datafiles/TROPESS/TROPESS_reanalysis_2hr_no2_sfc_'.
        chemra_var : `str`, optional
            The variable to extract from the dataset. Default is 'no2'
        insitu_path : `str`, optional
            Path to the insitu data files. Default is 'US_EPA/NO2/daily_NO2/daily_42602_'.
        era5_path : `str`, optional
            Path to the ERA5 reanalysis data files. Default is 'ERA5concatenated'.
        scale_factors : `dict`, optional
            Scaling factors for the variables. Default is a dictionary with
            scaling factors for 'chemra', 'sp', 'ssrd', and 'blh'.
        stage_2_cutoff : `int`, optional
            Year after which input files will also be generated for stage 2. Default is 2013.
        output_dir : `str`, optional
            Directory inside `inputfiles/` where the output x input file will be saved.
            Default is `'test_input'`.
        write_this_year : `bool`, optional
            Whether to write the data for this year or just return the xarray without writing to file.
            Default is True.
        output_format : `str`, optional
            Whether to save netcdf files ('nc'), numpy arrays ('npy'), or 'both'.
            Default is 'nc'. Irrelevant if `write_this_year` is False.
        overwrite : `bool`, optional
            Whether to overwrite existing netcdf files. Default is True.
        **kwargs : `dict`, optional
            Additional keyword arguments (not used).

        Returns
        -------
        x_data : `xarray.Dataset`
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
        chemra = shift_lon_arr(chemra)
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
    # print('all_datavars:',all_datavars)
    # print('datavars:',datavars)
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
                make_file_path(output_filepath)
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
    """ Add stage 2 for the variable in an xarray Dataset using available insitu data.

        Given an xarray Dataset with reanalysis data, duplicate the specified variable and replace values of that duplicated variable when and where there is available insitu data in the provided filepath, to be used for stage 2 of training the unet.

        Parameters
        ----------
        xr_dataset : `xarray.Dataset`
            The dataset containing reanalysis data.
        insitu_filepath : `str`
            Path to the CSV file containing insitu data.
        var : `str`, optional
            The variable to replace in the dataset. Default is 'no2'.

        Returns
        -------
        `xarray.Dataset`
            The updated dataset with insitu data replacing the specified variable.
    """
    # Verify the dataset
    xr_dataset = verify_dataset(xr_dataset)
    # Make a new variable to store the stage 2 data, filled with insitu
    var_s2 = f'{var}_s2'
    # Make a deep copy so that changes to `var_s2` don't affect `var`
    xr_dataset[var_s2]= xr_dataset[var].copy(deep=True)
    # Save the variable attributes
    var_s2_attrs = xr_dataset[var_s2].attrs
    # Modify the long_name attribute to indicate stage 2
    var_s2_attrs['long_name'] = var_s2_attrs.get('long_name', var_s2) + ' Stage 2'
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
    """Create y input files for multiple years.

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
    """ Create x input files for multiple years and stages.

        Run the `make_x_input_file` function for each year and stage in the specified ranges.

        Parameters
        ----------
        years : `iterable`, optional
            Years for which to create x input files. Default is range(2005, 2021).
        stage_2 : `bool`, optional
            Whether or not to make stage 2 in addition to stage 1 for the input.
            Default is True.
        stage_2_cutoff : `int`, optional
            Year after which the data will also be saved in stage 2. Default is 2013.
        output_dir : `str`, optional
            Directory inside `inputfiles/` where the output x input files will be saved.
            Default is `'test_input'`.
        sort : `bool`, optional
            Whether to sort the xarray after making all x inputs. Sorting takes a long time.
            Default is True.
        **kwargs : `dict`, optional
            Additional keyword arguments to pass to the `make_x_input_file` function.

        Returns
        -------
        x_data_array : `list` of `xarray.Dataset`
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
    """ Create all input files for the Unet model.

        This function combines the creation of y input files and x input files for both stages.

        Parameters
        ----------
        output_dir : `str`, optional
            Directory inside `inputfiles/` where the output input files will be saved.
            Default is `'test_input'`.
        sort : `bool`, optional
            Whether to sort the xarray after making all inputs. Sorting takes a long time.
            Default is True.
        **kwargs : `dict`, optional
            Additional keyword arguments to pass to the `make_y_input_file` and 
            `make_x_input_file` functions.

        Returns
        -------
        input_netcdf_xr : `xarray.Dataset`
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
    """ Create a metadata file for the dataset in the given directory.

        Gather the metadata from the given dataset, format it, and output to a clear-text file that can be easily read.

        Parameters
        ----------
        input_set : `str`, `xr.Dataset`, `uarray`
            Directory inside `inputfiles/` where the dataset is found and 
            in which the metadata file will be saved, or the xarray Dataset
        output_dir : `str`, `None`, optional
            Directory inside `inputfiles/` where the metadata file will be saved.
            If None, the metadata file will not be saved. Default is None.
        g_attrs : `dict`, `None`, optional
            Global attributes to use for the metadata file.
        overwrite : `bool`, optional
            Whether to overwrite an existing metadata file. Default is True.

        Returns
        -------
        metadata_dict : `dict`
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
    # Verify argument types
    if isinstance(input_set, str):
        # Load the xr dataset from a uarray
        xr_dataset = uarray(input_set, is_input_set=True).xr
    elif isinstance(input_set, xr.Dataset):
        xr_dataset = input_set
    elif isinstance(input_set, uarray):
        xr_dataset = input_set.xr
    else:
        raise TypeError(f"(make_input_metadata_file) `input_set` must be a string, xarray.Dataset, or uarray. Got type: {type(input_set)}")
    if not isinstance(output_dir, (str, type(None))):
        raise TypeError(f"(make_input_metadata_file) `output_dir` must be a string or None. Got type: {type(output_dir)}")
    if not isinstance(g_attrs, (dict, type(None))):
        raise TypeError(f"(make_input_metadata_file) `g_attrs` must be a dict or None. Got type: {type(g_attrs)}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"(make_input_metadata_file) `overwrite` must be a bool. Got type: {type(overwrite)}")

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
            make_file_path(output_filepath)
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
    years = get_years(xr_dataset)
    # Check for global attributes
    if isinstance(g_attrs, type(None)):
        g_attrs = xr_dataset.attrs
    else:
        # Update the types of the given `g_attrs` to be compatible with JSON
        for key in g_attrs.keys():
            if isinstance(g_attrs[key], np.integer):
                g_attrs[key] = int(g_attrs[key])
            elif isinstance(g_attrs[key], np.floating):
                g_attrs[key] = float(g_attrs[key])
            elif isinstance(g_attrs[key], np.ndarray):
                g_attrs[key] = g_attrs[key].tolist()
            elif isinstance(g_attrs[key], (np.bool_, bool)):
                if g_attrs[key] == True:
                    g_attrs[key] = 'True'
                else:
                    g_attrs[key] = 'False'
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
        'x1_vars',
        'x2_vars',
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
    """ Create an input configuration file.
    
        Create the input configuration file for using input data with the Unet model.

        Parameters
        ----------
        config_name : `str`
            Name of the configuration file to be created.
        input_set : `str` or `xr.Dataset`, optional
            Directory inside `inputfiles/` where the dataset is found, or the xarray Dataset.
            Default is 'no2_sample_input'.
        grid_size : `list` of `int`, optional
            The number of grid cells to have in [latitude, longitude] when running the Unet model.
            Default is [56, 120].
        x_vars : `list` of `str`, optional
            List of variable names to be used as input features for the model.
            Default is a list of common meteorological and chemical variables.
        stage_2 : `bool`, optional
            Whether or not stage 2 should be run with the Unet model.
            Default is True.
        stage_2_cutoff : `int`, optional
            Year after which stage 2 data will be used.
            Default is 2013.
        lsm_vars : `list` of `str`, optional
            List of variable names that should use land-sea mask.
            Default is ['no2', 'no2_tm1'].
        zfi_vars : `list` of `str`, optional
            List of variable names that should use zero-fill mask.
            Default is ['t2m'].
        **kwargs : `dict`, optional

        Returns
        -------
        config_dict : `dict`
            The configuration dictionary that was saved to the json file.
    """
    # Verify argument types
    if not isinstance(config_name, str):
        raise TypeError(f"(make_input_config) `config_name` must be a string. Got type: {type(config_name)}")
    # Verify input_set is a string or xr.Dataset
    if isinstance(input_set, str):
        # Check whether the given input_set exists in 'inputfiles/'
        xr_path = f'inputfiles/{input_set}/{input_set}.nc'
        if not os.path.exists(xr_path):
            raise ValueError(f"(make_input_config) File {xr_path} does not exist.")
        # Load the dataset
        xr_dataset = xr.load_dataset(xr_path)
    elif isinstance(input_set, xr.Dataset):
        xr_dataset = input_set
    else:
        raise TypeError(f"(make_input_config) `input_set` must be a string or xarray.Dataset. Got type: {type(input_set)}")
    if not isinstance(grid_size, list):
        raise TypeError(f"(make_input_config) `grid_size` must be a list of integers. Got type: {type(grid_size)}")
    if not isinstance(x_vars, list):
        raise TypeError(f"(make_input_config) `x_vars` must be a list of strings. Got type: {type(x_vars)}")
    if not isinstance(stage_2, bool):
        raise TypeError(f"(make_input_config) `stage_2` must be a boolean. Got type: {type(stage_2)}")
    if not isinstance(stage_2_cutoff, int):
        raise TypeError(f"(make_input_config) `stage_2_cutoff` must be an integer. Got type: {type(stage_2_cutoff)}")
    if not isinstance(lsm_vars, list):
        raise TypeError(f"(make_input_config) `lsm_vars` must be a list of strings. Got type: {type(lsm_vars)}")
    if not isinstance(zfi_vars, list):
        raise TypeError(f"(make_input_config) `zfi_vars` must be a list of strings. Got type: {type(zfi_vars)}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"(make_input_config) `overwrite` must be a boolean. Got type: {type(overwrite)}")
    # Verify the dataset
    xr_dataset = verify_dataset(xr_dataset)
    # Verify that grid_size has exactly 2 integers
    if not len(grid_size) == 2:
        raise ValueError(f"(make_input_config) Expected `grid_size` to have a length of 2. Got length of {len(grid_size)}: {grid_size}")
    else:
        if isinstance(grid_size[0], int):
            n_lats = grid_size[0]
        else:
            raise TypeError(f"(make_input_config) Number of latitudes in `grid_size` must be an integer. Got type: {type(grid_size[0])}")
        if isinstance(grid_size[1], int):
            n_lons = grid_size[1]
        else:
            raise TypeError(f"(make_input_config) Number of longitudes in `grid_size` must be an integer. Got type: {type(grid_size[1])}")
    # Verify that `grid_size` is not larger than the lat-lon grid in xr_dataset
    xr_n_lats = xr_dataset.sizes['lat']
    xr_n_lons = xr_dataset.sizes['lon']
    if n_lats > xr_n_lats:
        raise ValueError(f"(make_input_config) Requested length of latitude grid ({n_lats}) cannot exceed length of latitude dimension in the given netcdf ({xr_n_lats}).")
    if n_lons > xr_n_lons:
        raise ValueError(f"(make_input_config) Requested length of longitude grid ({n_lons}) cannot exceed length of longitude dimension in the given netcdf ({xr_n_lons}).")
    # Verify that all x_vars are in the dataset
    for var in x_vars:
        verify_var(xr_dataset, var)
    # Verify that stage 2 exists in the dataset
    if not 2 in xr_dataset.attrs.get('stages', []):
        stage_2 = False
        print('Stage 2 not found in dataset. Setting stage_2 to False in configuration.')
    # Verify that stage_2_cutoff is a year that exists in the dataset
    years = get_years(xr_dataset)
    if stage_2_cutoff not in years:
        raise ValueError(f"(make_input_config) `stage_2_cutoff` {stage_2_cutoff} not found in dataset years: {years}")
    # Verify that the lsm_vars are in the dataset
    for var in lsm_vars:
        verify_var(xr_dataset, var)
    # Verify that the zfi_vars are in the dataset
    for var in zfi_vars:
        verify_var(xr_dataset, var)
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

def copy_input_files(
    source_input_set,
    output_dir,
    keep_vars='all',
    start_date=None,
    end_date=None,
    overwrite=True,
    **kwargs,
):
    """ Copy an input set to a new location.

        Create a copy of the input netCDF and `input_metadata.json` file from the specified source in a new directory, optionally filtering the netCDF to only include specified variables and date range.

        Parameters
        ----------
        source_input_set : `str`
            Name of the source input set located in `inputfiles/`.
        output_dir : `str`
            Name of the output directory inside `inputfiles/` where the new input set will be copied to.
        keep_vars : `list` of `str` or `all`, optional
            List of variable names to keep in the copied netCDF. If `all`, all variables are kept.
            Default is `all`.
        start_date : `str`, `None`, or `np.datetime64`, optional
            Date from which to start the copied data. If None, the start date equals that of the original file.
            Expected format is 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DD'.
            Default is None.
        end_date : `str`, `None`, or `np.datetime64`, optional
            Date at which to end the copied data. If None, the end date equals that of the original file.
            Expected format is 'YYYY-MM-DDTHH:MM:SS' or 'YYYY-MM-DD'.
            Default is None.
        **kwargs : `dict`, optional

        Returns
        -------
        new_xr_dataset : `xarray.Dataset`
            The copied and filtered xarray Dataset that is saved to the new location.
    """ 
    # Verify argument types
    if not isinstance(source_input_set, str):
        raise TypeError(f"(copy_input_files) `source_input_set` must be a string. Got type: {type(source_input_set)}")
    if not isinstance(output_dir, str):
        raise TypeError(f"(copy_input_files) `output_dir` must be a string. Got type: {type(output_dir)}")
    if not isinstance(keep_vars, list) and not keep_vars == 'all':
        if isinstance(keep_vars, str):
            # Turn `keep_vars` into a list if it's a single string
            keep_vars = [keep_vars]
        else:
            raise TypeError(f"(copy_input_files) `keep_vars` must be a list of strings or 'all'. Got type: {type(keep_vars)}")
    if not (isinstance(start_date, (str, type(None), np.datetime64))):
        raise TypeError(f"(copy_input_files) `start_date` must be a string, None, or np.datetime64. Got type: {type(start_date)}")
    if not (isinstance(end_date, (str, type(None), np.datetime64))):
        raise TypeError(f"(copy_input_files) `end_date` must be a string, None, or np.datetime64. Got type: {type(end_date)}")
    # Verify that the source and output directories are not the same
    if source_input_set == output_dir:
        raise ValueError(f"(copy_input_files) `source_input_set` and `output_dir` cannot be the same. Both are '{source_input_set}'.")

    # Check whether the output directory already exists
    try:
        verify_path(f"inputfiles/{output_dir}/")
    except FileNotFoundError as e:
        assert True, f"(copy_input_files) Output directory 'inputfiles/{output_dir}/' does not exist. Creating it."
    else:
        if overwrite == False:
            # Ask whether to overwrite the existing directory
            overwrite = unox.interpret_user_input(input(f"Output directory 'inputfiles/{output_dir}/' already exists. Overwrite? (y/n)"))
            if not overwrite:
                print('Aborting input file copy.')
                return
        print(f"Overwriting existing input files in {output_dir}")
        remove_non_empty_directory(f"inputfiles/{output_dir}/")
    # Make the output directory
    make_file_path(f"inputfiles/{output_dir}/")
    
    # Load the source dataset as a `uarray`
    source_uarr = uarray(source_input_set, is_input_set=True)

    # Check whether to filter variables
    if keep_vars != 'all':
        # Verify that all variables in `keep_vars` are in the source dataset
        for var in keep_vars:
            verify_var(source_uarr.xr, var)
        # Drop variables not in `keep_vars`
        vars_to_drop = [var for var in source_uarr.xr.data_vars if var not in keep_vars]
        source_uarr.xr = source_uarr.xr.drop_vars(vars_to_drop)
        # Update the variable list attributes
        for var_list_attr in ['x_vars', 'x1_vars', 'x2_vars']:
            if var_list_attr in source_uarr.xr.attrs:
                filtered_var_list = [var for var in source_uarr.xr.attrs[var_list_attr] if var in keep_vars]
                source_uarr.xr.attrs[var_list_attr] = filtered_var_list
        if 'y_var' in source_uarr.xr.attrs:
            if source_uarr.xr.attrs['y_var'] not in keep_vars:
                source_uarr.xr.attrs['y_var'] = 'None'
    # Check whether to filter dates
    if not isinstance(start_date, type(None)) or not isinstance(end_date, type(None)):
        # Convert start_date and end_date to strings of YYYY-MM-DD if they are np.datetime64
        if isinstance(start_date, np.datetime64):
            start_date = str(pd.to_datetime(start_date).date())
        elif isinstance(start_date, type(None)):
            this_start = source_uarr.xr['time'].values[0]
            start_date = f"{this_start.year:04d}-{this_start.month:02d}-{this_start.day:02d}"
        if isinstance(end_date, np.datetime64):
            end_date = str(pd.to_datetime(end_date).date())
        elif isinstance(end_date, type(None)):
            this_end = source_uarr.xr['time'].values[-1]
            end_date = f"{this_end.year:04d}-{this_end.month:02d}-{this_end.day:02d}"
        # Verify that `start_date` is before `end_date`
        if start_date >= end_date:
            raise ValueError(f"(copy_input_files) `start_date` must be before `end_date`. Got start_date: {start_date}, end_date: {end_date}.")
        # Select the date range
        source_uarr.xr = source_uarr.xr.sel(time=slice(start_date, end_date), drop=True)
    
    # Update the modification time attribute
    source_uarr.xr.attrs['modification_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

    # Write out results
    if not isinstance(output_dir, type(None)):
        # Write the new dataset to the output directory
        source_uarr.xr.to_netcdf(f"inputfiles/{output_dir}/{output_dir}.nc")
        # Create metadata file
        meta_dict = make_input_metadata_file(
            source_uarr.xr,
            output_dir=output_dir,
            g_attrs=source_uarr.xr.attrs,
        )

    return source_uarr