"""
Author: Evelyn Macdonald

save_data.py
Regrid and resample ERA5 datasets to daily averages on a 56 x 120 lat x lon grid.
"""

import numpy as np
import netCDF4 as nc
import pandas as pd
import xarray as xr
import os
import sys

year = sys.argv[1]   #for use with save_data.sh
# year = 2005

lons = np.load('lons.npy')  #lon and lat grid for Unet
lats = np.load('lats.npy')


path = str(year) + '/'   #directory of ERA5 files for the desired year. Each file is one variable for the specified month.


for filename in os.listdir(path):  
    print(path+filename)

    data = xr.open_dataset(path+filename)  #open the dataset of the desired variable and month
    # print(data.dims)

    regridded = data.interp(latitude=lats, longitude=lons)  #regridded to coarser spatial resolution, time x 56 lat x 120 lon.

    # daily_avg = regridded.groupby('valid_time.day').mean()  #This version causes problems later because it doesn't preserve datetime.
    daily_avg = regridded.resample(valid_time='d').mean()   #daily average of the variable. Dimensions (n_days, 56, 120) where n_days is the number of days in the month. February 29th may be a problem later.
    # print(daily_avg.dims)
    # print(daily_avg.valid_time)

    daily_avg.to_netcdf('ERA5resampled/'+filename.split('.nc')[0]+'_resampled.nc')



