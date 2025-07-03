import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import xarray as xr

import unox.unox as unox

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
    # Verify path
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
        output_filepath = os.path.join(outputdir, f"stage1/y/Y_{year}.npy")
        np.save(output_filepath, y_data)
        if year > stage_2_cutoff:
            # Save in stage 2 for years later than specified
            output_filepath_stage2 = os.path.join(outputdir, f"stage2/y/Y_{year}.npy")
            np.save(output_filepath_stage2, y_data)
        # Output message
        print(f"Created Y input file for {var} in {year}, saved to {output_filepath}")
    return np.array(y_data)

