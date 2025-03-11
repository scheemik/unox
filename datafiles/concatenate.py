"""
Regrid and resample, then concatenate all 12 months of each resampled ERA5 variable for each year. 
Output should be (365,56,120). Or 366 for leap years. Save to netcdf.
"""

import numpy as np
import netCDF4 as nc
import xarray as xr
import os
import sys

lons = np.load('lons.npy')  #lon and lat grid for Unet
lats = np.load('lats.npy')

# year = sys.argv[1]
for year in range(2006,2014):   #change to desired range
    print(year)

    path = '../../'+str(year)+'/'    #ERA5 data for the year
    print(path)
    for variable in ['u10','v10','blh','sp','skt','t2m','ssrd']: 
        datasets = []
        for month in range(1,13):
            filename = str(year)+'_'+str(month).zfill(2)+'_'+variable+'.nc'
            print(path+filename)
            data = xr.open_dataset(path+filename)  #open the dataset of the desired variable and month
            regridded = data.interp(latitude=lats, longitude=lons)  #regridded to coarser spatial resolution, time x 56 lat x 120 lon.
            daily_avg = regridded.resample(valid_time='d').mean()   #daily average of the variable. Dimensions (n_days, 56, 120) where n_days is the number of days in the month. Deal with February 29th later.
            datasets.append(daily_avg)   #put all the resampled/regridded months together
        fullyear =  xr.concat(datasets, dim='valid_time')    #concatenate all the months, keeping the datetime
        print(getattr(fullyear,variable).data.shape)  #should be (365,56,120)   
        fullyear.to_netcdf('ERA5concatenated/'+str(year)+variable+'.nc')  #save







