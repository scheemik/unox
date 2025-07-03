import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import xarray as xr
import pandas as pd

import unox.unox as unox
import unox.data as udata

def make_y_input_file(year,
                      var='nox',
                      datadir='/data/high_res/emacdonald/unet/datafiles/t106',
                      fileprefix='nox_',
                      fileextension='_t106_US.nc',
                      scale_factor=1e12,
                      nan_fill=0,
                      stage_2_cutoff=2013,
                      outputdir='inputfiles/'):
    """
    Create a y input file for the Unet model for the given year.

    The array in the file will have these dimensions:
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
    datadir : str, optional
        Directory where the NOx data are stored. 
        Default is '/data/high_res/emacdonald/unet/datafiles/t106'.
    fileprefix : str, optional
        Prefix for the input file name. Default is 'nox_'.
    fileextension : str, optional
        Extension for the input file name. Default is '_t106_US.nc'.
    scale_factor : float, optional
        Factor by which to scale the data. Default is 1e12.
    nan_fill : float, optional
        Value to fill NaNs in the dataset. Default is 0.
    stage_2_cutoff : int, optional
        Year after which the data will also be saved in stage 2.
    outputdir : str, optional
        Directory where the output y input file will be saved.
        Default is 'inputfiles/'.

    Returns
    -------
    y_data : numpy.ndarray
        The y input data for the specified year, scaled and processed.
    """
    # Assemble file path
    filepath = os.path.join(datadir, f"{fileprefix}{year}{fileextension}")
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
    if not isinstance(outputdir, type(None)):
        # Assemble the file path
        output_filepath = os.path.join(outputdir, f"stage1/y/Y_{year}.npy")
        np.save(output_filepath, y_data)
        if year > stage_2_cutoff:
            # Save in stage 2 for years later than specified
            output_filepath_stage2 = os.path.join(outputdir, f"stage2/y/Y_{year}.npy")
            np.save(output_filepath_stage2, y_data)
        # Output message
        print(f"Created Y input file for {var} in {year}, saved to {output_filepath}")
    return np.array(y_data)

def make_x_input_file(year,
                      stage,
                      datadir='/data/high_res/emacdonald/unet/datafiles/',
                      scale_factor=1000,
                      outputdir='inputfiles/'):
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
    datadir : str, optional
        Directory where the NOx data are stored. Default is '/data/high_res/emacdonald/unet/datafiles/t106'.
    outputdir : str, optional
        Directory where the output x input file will be saved. Default is 'inputfiles/'.

    Returns
    -------
    x_data : xarray.Dataset
        The x input data for the specified year and stage.
    """
    # Assemble the file path for the TCR-2 NO2 data
    tcr2_filepath = os.path.join(datadir, f'TROPESS/TROPESS_reanalysis_2hr_no2_sfc_{year}.nc')
    # Verify the path
    tcr2_filepath = unox.verify_path(tcr2_filepath)
    # Load TCR-2 NO2 data
    tcr2 = xr.load_dataset(tcr2_filepath)
    # Change longitude coordinate convention to match other data
    tcr2.coords['lon'] = (tcr2.coords['lon'] + 180) % 360 - 180  
    # tcr2.coords['lon'] = udata.shift_lon(tcr2.coords['lon'])  
    # Resample and rescale
    tcr2 = tcr2.resample(time='d').mean() / scale_factor
    # Find the number of days in the year
    ndays = len(tcr2.coords['time'])
    # Fix the time coordinate to match the year
    ## For an unexplained reason, the year in all TCR-2 files is always 2005.
    tcr2.coords['time'] = pd.date_range(f"{year}-01-01", periods=ndays)
    
    # Combine EPA and TCR-2 data for stage 2
    if stage == 2:
        # Assemble the file path for the EPA NO2 data
        epa_filepath = os.path.join(datadir, f'US_EPA/daily_42602_{year}.csv')
        # Verify the path
        epa_filepath = unox.verify_path(epa_filepath)
        # Combine EPA data with TCR-2 data
        tcr2 = make_2d_input(epa_filepath, tcr2)
    
    # Interpolate to latitude and longitude grid
    lats, lons = unox.load_lats_lons()
    tcr2 = tcr2.interp(lat=lats, lon=lons)
    
    # Plotting (optional)
    # plt.figure()
    # tcr2.sortby(['lat', 'lon']).no2[0].plot()
    
    # Start a list to hold datasets
    datasets = []
    # Add the TCR-2 NO2 data for day t (starting from the second day)
    datasets.append(tcr2.no2[1::])

    # Get the time-shifted variable (day t-1)
    previousday = tcr2.copy()
    # Fix rounding
    previousday.coords['time'] = (previousday.coords['time'] + 1).dt.ceil('D')
    # Rename t-1 variable
    previousday = previousday.rename({'no2': 'no2_tm1'})
    # Add the TCR-2 NO2 data for the previous day (t-1)
    datasets.append(previousday.no2_tm1[:-1])  # day t-1

    # Add the other variables from the ERA5 dataset
    for variable in ['u10', 'v10', 'blh', 'sp', 'skt', 't2m', 'ssrd']:
        # Assemble the file path for the ERA5 variable
        era5_var_filepath = os.path.join(datadir, f'ERA5concatenated/{year}{variable}.nc')
        # Verify the path
        era5_var_filepath = unox.verify_path(era5_var_filepath)
        # Load the ERA5 variable dataset
        # Note: The variable name in the dataset is assumed to be the same as `variable`
        newvar = xr.load_dataset(era5_var_filepath)
        # Rename coordinates to match the other datasets
        newvar = newvar.rename({'valid_time': 'time', 'latitude': 'lat', 'longitude': 'lon'})
        # Add the variable data to the datasets list, skipping the first day
        datasets.append(getattr(newvar, variable)[1:])
    
    # Merge all datasets into a single xarray Dataset
    x_data = xr.merge(datasets)
    # Convert calendar to 'noleap' to remove February 29th
    x_data = x_data.convert_calendar('noleap')

    # Scale some variables to make orders of magnitude more similar
    x_data['sp'] = x_data['sp'] / 100000  # Scale surface pressure
    x_data['ssrd'] = x_data['ssrd'] / 1000000  # Scale surface solar radiation
    x_data['blh'] = x_data['blh'] / 1000  # Scale boundary layer height
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
    if not isinstance(outputdir, type(None)):
        # Assemble the file path
        output_filepath = os.path.join(outputdir, f'stage{stage}/x/X_{year}.npy')
        np.save(output_filepath, xnp)
        # Output message
        print(f"Created X input file for stage {stage} in {year}, saved to {output_filepath}")
    return xnp