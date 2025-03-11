"""
Concatenate all 12 months of each resampled ERA5 variable for each year. Output should be (365,56,120)
"""

import numpy as np
import netCDF4 as nc
import xarray as xr
import os
import sys

# year = sys.argv[1]
for year in range(2006,2014):
# year = 2005

    print(year)

    path = 'ERA5resampled/'    #Where the months of regridded daily averages for each variable are
    for variable in ['u10','v10','blh','sp','skt','t2m','ssrd']: 
        #Files for all the months in order for the current variable
        filenames = [path+str(year)+'_'+str(month).zfill(2)+'_'+variable+'_resampled.nc' for month in np.arange(1,13,1)]
        # print(filenames)
        datasets = [xr.open_dataset(f) for f in filenames]  
        fullyear = xr.concat(datasets, dim='valid_time')    #concatenate all the months, keeping the datetime
        print(getattr(fullyear,variable).data.shape)  #should be (365,56,120)

        fullyear.to_netcdf('ERA5concatenated/'+str(year)+variable+'.nc')  #save




