"""
Create the input files for the Unet model. 
"""

import numpy as np
import os
import netCDF4 as nc
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import scipy

lons = np.load('lons.npy')  #lon and lat grid for Unet
lats = np.load('lats.npy')

def make2d(csvfile,tcr2):
    """
    Takes EPA data from a csv file and combines them with TCR-2 data for stage 2 training. 
    This is achieved by replacing TCR-2 NO2 values with EPA data at gridpoints where they're available. 
    """
    epa = pd.read_csv(csvfile,parse_dates={'Date':['Date Local']},index_col=['Date'],
        usecols=['Date Local','Latitude','Longitude','Arithmetic Mean'])   #daily EPA NO2 data
    g = epa.groupby(['Date'])    #one group for each day of data in the giant csv file
    k = [key for key in g.groups.keys()]   #group names, which are the dates
    
    in1 = tcr2.no2.where((tcr2.lat >= np.min(lats)),drop=True)  #select a smaller domain
    in2 = in1.where((in1.lon <= np.max(lons)),drop=True)  
    
    for i in range(len(k)):     
        newgroup = g.get_group((k[i]),)    #ith day
        garray = newgroup.to_numpy()
        garray=garray.swapaxes(0,1)   #(lat,lon,no2) array for one day 
        lt = garray[0]
        ln = garray[1]
        values = garray[2]   #NO2 data
        day = in2.sel(indexers={'time':k[i]})  
           
        for j in range(len(lt)):
            pt = day.sel({'lat':lt[j],'lon':ln[j]},method='nearest',tolerance=1.125)  #tolerance: grid cell size
            tcr2.no2.loc[{'time':k[i],'lon':pt.lon,'lat':pt.lat}] = values[j]
    return tcr2    


def yinput(year, datadir='t106'):
    """
    Create a y input file for Unet. Stage 1 and 2 are the same but for different years.
    year: between 2005 and 2021
    datadir: where the NOx data are stored. 
    """
    nox = xr.load_dataset(datadir+'/nox_'+str(year)+'_t106_US.nc')*1e12   #load data and rescale
    nox = nox.interp(lat=lats, lon=lons).resample(time='d').mean().fillna(0)  #(365,56,120). Remove nans so the model doesn't output nans everywhere
    exp = nox.expand_dims('var',-1)  #add a dimension of size 1 to the end to make it the right shape
    print(exp.nox.as_numpy().shape)
    np.save('inputfiles/stage1/y/Y_'+str(year),exp.nox[1::])  #skip the first day because of the t-1 thing
    if year > 2013:   #also save in stage 2 for later years
        np.save('inputfiles/stage2/y/Y_'+str(year),exp.nox[1::])  #skip the first day because of the t-1 thing

# yinput(2005)

def xinput(year,stage):  
    datasets = []
    tcr2 = xr.load_dataset('TROPESS/TROPESS_reanalysis_2hr_no2_sfc_'+str(year)+'.nc')  #TCR-2 NO2 data
    tcr2.coords['lon']=(tcr2.coords['lon']+180)%360 - 180   #change longitude coordinate convention to match other data
    
    tcr2 = tcr2.resample(time='d').mean()/1000   #resample and rescale
    ndays = len(tcr2.coords['time'])  #number of days in the year
    tcr2.coords['time'] = pd.date_range(str(year)+'-01-01',periods=ndays)  #fix the year because it's always 2005 in the files for some reason

    if stage == 2:  #combine EPA and TCR2 data
        tcr2 = make2d('US_EPA/daily_42602_'+str(year)+'.csv',tcr2)
    
    tcr2 = tcr2.interp(lat=lats,lon=lons)   #regrid
    plt.figure()
    tcr2.sortby(['lat','lon']).no2[0].plot()

    datasets.append(tcr2.no2[1::])   #day t, starting from the second day
    previousday = tcr2.copy()        #day t-1
    previousday.coords['time'] = (previousday.coords['time'] + 1).dt.ceil('D')   #fix rounding
    previousday = previousday.rename({'no2':'no2_tm1'})

    datasets.append(previousday.no2_tm1[:-1])   #day t-1

    for variable in ['u10','v10','blh','sp','skt','t2m','ssrd']:
        newvar = xr.load_dataset('ERA5concatenated/'+str(year)+variable+'.nc')
        newvar = newvar.rename({'valid_time':'time','latitude':'lat','longitude':'lon'})  #to match other datasets
        datasets.append(getattr(newvar,variable)[1::])
        
    x = xr.merge(datasets)   #put all the variables together in a dataset
    x = x.convert_calendar('noleap')   #get rid of February 29th

    x['sp'] = x['sp']/100000    #make orders of magnitude more similar. Might want to play around with this
    x['ssrd'] = x['ssrd']/1000000
    x['blh'] = x['blh']/1000
    x = x[['time','lat','lon',*list(x.data_vars)]]    #reorder dimensions; there's probably a smoother way

    datavars = list(x.data_vars)
    print(datavars)
    xnp = np.ndarray([364,56,120,len(datavars)])   #empty numpy array to put the data in
    for i in range(len(datavars)):
        xnp[:,:,:,i] = x[datavars[i]]    #put it in the numpy array

    np.save('inputfiles/stage'+str(stage)+'/x/X_'+str(year), xnp)

    return xnp

xnp = xinput(2015,2)
# print(xnp.shape)


# for year in range(2016,2021):  # Stage 2 is later years but with added surface NOx in Y.
#     print(year)
#     xnp = xinput(year,2)
#     print(xnp.shape)
