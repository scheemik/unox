"""
Create the input files for the Unet model.
"""

import numpy as np
import os
import netCDF4 as nc
import pandas as pd
import xarray as xr
from datetime import timedelta
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
    datasets = []   #will contain a dataset for each day
    
    in1 = tcr2.no2.where((tcr2.lat >= np.min(lats)),drop=True)  #select a smaller domain
    in2 = in1.where((in1.lon <= np.max(lons)),drop=True)  
    
    # stacked = in2.stack(d=['lat','lon'])   #stack lat and lon of 2d data to make it the same shape as epa

    for i in range(len(k)):     
        newgroup = g.get_group((k[i]),)    #ith day
        garray = newgroup.to_numpy()
        garray=garray.swapaxes(0,1)   #(lat,lon,no2) array for one day 
        lt = garray[0]
        ln = garray[1]
        values = garray[2]
        year = in2.sel(indexers={'time':k[i]})  #day not year
           
        # newpoints = year.sel({'lat':lt,'lon':ln},method='nearest',tolerance=1.125)   #points in the truncated tcr2 data that are close to EPA stations
        # year[newpoints] = values
        for j in range(len(lt)):
            # for h in range(len(ln)):
            pt = year.sel({'lat':lt[j],'lon':ln[j]},method='nearest',tolerance=1.125)  #tolerance: grid cell size
            tcr2.no2.loc[{'time':k[i],'lon':pt.lon,'lat':pt.lat}] = values[j]
    return tcr2    



        # in2.sel(indexers={'lat':lt,'lon':ln},tolerance=0.1,method='nearest').plot()


'''
    for i in range(len(k)):       #loop through all the groups
        newgroup = g.get_group((k[i]),)    #ith day
        garray = newgroup.to_numpy()
        garray=garray.swapaxes(0,1)   #(lat,lon,no2) array for one day 
        lt = np.concatenate([garray[0],stacked.lat])
        ln = np.concatenate([garray[1],stacked.lon])
        values = np.concatenate([garray[2],stacked[i]])   #NO2

        points = np.array([ln,lt]).swapaxes(0,1)    #shape (big number,2)        xi = tuple(np.meshgrid(lons,lats))
        grid = scipy.interpolate.griddata(points,values,xi,'linear',fill_value=np.nan,rescale=True)

        # tarray = tcr2.no2[i].stack(d=['lat','lon'])    #tcr2 values 
        # if i == 0:
        #     print(tarray.lat.shape)
        # print(np.where(values==np.nan))  #never
        # matrix = np.zeros([len(ln),len(lt)])    #2D array where the no2 values will go
        # matrix.fill(np.nan)   #puts nans everywhere, which seems to make sense except it messes up Unet I think
        # np.fill_diagonal(matrix,values)   #put the no2 data in the array
        # ds = xr.Dataset({'no2': (("lat", "lon"),matrix,),},coords={'lat':lt,'lon':ln,'time':k[i]})    #empty xarray Dataset with lat and lon values
        # for j in range(len(values)):     #loop through the no2 data
        #     blankds.no2.loc[lt[j],ln[j]] = values[j]   #basically a diagonal matrix. Slower version of fill_diagonal above
        # print(i,blankds.sel(lat=~blankds.indexes['lon'].duplicated()))
        # ds = ds.drop_duplicates(...)    #drops all the duplicate values. 
        # datasets.append(ds)
    # datasets.append(tcr2)
    plt.figure()
    plt.scatter(ln,lt,c=values)
    plt.figure()
    plt.pcolormesh(lons,lats,grid)
    plt.colorbar()
    # plt.scatter(ln,lt,values)
    # plt.scatter(ln[0:len(garray[1])],lt[0:len(garray[1])],values[0:len(garray[2])])
    # plt.xlim(-150,-50)
    # plt.ylim(15,75)
    # print(df)
    # bigds = xr.concat(datasets,dim='time')#.fillna(0)
    # print(bigds)
    # plt.figure()
    # bigds.sortby(['lat','lon']).no2[0].plot(vmin=0)
    # b = bigds.interp(lat=tcr2.lat,lon=tcr2.lon).sortby(['lat','lon'])
    # plt.figure()
    # b.no2[0].plot()
    # plt.xlim(-150,-50)
    # plt.ylim(16,75)
    # print(bigds.lat.data,bigds.lon.data)
    # print(np.max(bigds.no2.data))
    # print(np.where(np.isnan(bigds.no2.data)==True))  #still no nans
    # tc = tcr2.interp(lat=bigds.lat,lon=bigds.lon)
    plt.figure()
    tcr2.sortby(['lat','lon']).no2[-1].plot(vmax=20)
    # plt.colorbar()
    plt.xlim(-170,-40)
    plt.ylim(10,75)
    # plt.figure()
    # tc.no2[0].plot()
    # plt.show()
'''


def yinput(year, datadir='t106'):
    """
    Create a y input file for Unet. Stage 1 and 2 are the same but for different years.
    year: between 2005 and 2021
    datadir: where the NOx data are stored. 
    """
    nox = xr.load_dataset(datadir+'/nox_'+str(year)+'_t106_US.nc')*1e12   #load data and rescale
    print(np.max(nox.nox))
    nox = nox.interp(lat=lats, lon=lons).resample(time='d').mean().fillna(0)  #(365,56,120). Remove nans so the model doesn't output nans everywhere
    # print(nox.nox)
    # print(np.nanmax(nox.nox))
    exp = nox.expand_dims('var',-1)  #add a dimension of size 1 to the end to make it the right shape
    
    print(exp.nox.as_numpy().shape)
    np.save('inputfiles/stage1/y/Y_'+str(year),exp.nox[1::])  #skip the first day because of the t-1 thing
    if year > 2013:   #also save in stage 2 for later years
        np.save('inputfiles/stage2/y/Y_'+str(year),exp.nox[1::])  #skip the first day because of the t-1 thing



# yinput(2005)
for year in range(2006, 2021):
    yinput(year)

def xinput(year,stage):  
    datasets = []
    tcr2 = xr.load_dataset('TROPESS/TROPESS_reanalysis_2hr_no2_sfc_'+str(year)+'.nc')  #TCR-2 NO2 data
    tcr2.coords['lon']=(tcr2.coords['lon']+180)%360 - 180   #change longitude coordinate convention to match other data
    
    tcr2 = tcr2.resample(time='d').mean()/1000   #resample and rescale
    ndays = len(tcr2.coords['time'])  #number of days in the year
    tcr2.coords['time'] = pd.date_range(str(year)+'-01-01',periods=ndays)  #fix the year because it's always 2005 in the files for some reason

    if stage == 2:  #combine EPA and TCR2 data
        tcr2 = make2d('US_EPA/daily_42602_'+str(year)+'.csv',tcr2)
        # print(epa.no2[0].sortby(['lat','lon']))

        # print(np.max(epa.no2.data))
        # epa = pd.read_csv('US_EPA/daily_42602_'+str(year)+'.csv',parse_dates={'time':['Date Local']}, 
        #           index_col=['time'],usecols=['Date Local','Latitude','Longitude','Arithmetic Mean']).to_xarray()
        # epa = epa.rename({'Latitude':'lat','Longitude':'lon','Arithmetic Mean':'no2_g'})
        # epa = epa.assign_coords({'lat':epa.lat,'lon':epa.lon})
        # print(epa)
        # tcr2 = xr.merge([epa,tcr2],join='inner',combine_attrs='drop',compat='no_conflicts',fill_value=0)    #combine the TCR-2 and EPA data into one variable
        # tcr2 = xr.concat([epa,tcr2],dim=['lat'],data_vars=['no2'],create_index_for_new_dim=False)
        # tcr2 = tcr2[['time','lat','lon','no2']]  #the problem is concat/merge. Try regrid then merge then regrid again?
        # tcr2 = xr.merge([epa.no2,tcr2.no2],join='outer')#.fillna(0)  
        # plt.figure()
        # tcr2.sortby(['lat','lon']).no2[0].plot(vmin=0,vmax=20,xlim=[-150,-50],ylim=[15,70])

        # lat_ext = np.concatenate([epa.lat,tcr2.lat])
        # lon_exp = np.concatenate([epa.lon,tcr2.lon])
        
        # newds = xr.Dataset({'no2':(("lat", "lon"),matrix,),},coords={'lat':lt,'lon':ln,'time':k[i]}) 
        
        # tcr2 = xr.combine_nested([tcr2,epa],concat_dim='lat')
        # print(tcr2)
        # print(np.where(np.isnan(tcr2.no2.data)==True))
    
    tcr2 = tcr2.interp(lat=lats,lon=lons)   #regrid
    plt.figure()
    tcr2.sortby(['lat','lon']).no2[0].plot()
    # print(tcr2.no2)

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

    # print(np.max(x.no2.data))
    # print(np.where(np.isnan(x.no2)==True))
    x = x.convert_calendar('noleap')   #get rid of February 29th

    x['sp'] = x['sp']/100000    #make orders of magnitude more similar. Might want to play around with this
    x['ssrd'] = x['ssrd']/1000000
    x['blh'] = x['blh']/1000
    x = x[['time','lat','lon',*list(x.data_vars)]]    #reorder dimensions; there's probably a smoother way

    #maybe the dimension/coordinate names are the issue somehow? Currently the numpy array has nans 

    datavars = list(x.data_vars)
    print(datavars)
    xnp = np.ndarray([364,56,120,len(datavars)])   #empty numpy array to put the data in
    for i in range(len(datavars)):
        # print(np.max(x[datavars[i]].data))   #nan
        xnp[:,:,:,i] = x[datavars[i]]#.data     #put it in the numpy array
        # print(np.max(xnp[0,:,:,i]))   #nan for no2 fields

    # print(xnp[0,:,:,0])
    np.save('inputfiles/stage'+str(stage)+'/x/X_'+str(year), xnp)

    return xnp

# xnp = xinput(2015,2)
# print(xnp.shape)


# for year in range(2016,2021):  # Stage 2 is later years but with added surface NOx in Y.
#     print(year)
#     xnp = xinput(year,2)
#     print(xnp.shape)
