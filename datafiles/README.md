This directory contains data files and scripts to make the input files for the Unet model for estimating North American NOx emissions. 

Data sources:
- ERA5 meteorological variables: directories 2005-2021. Files within these directories are one month of one variable over the North American domain given by the bounds of (lats.npy,lons.npy), but at 2-hourly frequency and 0.25 degree resolution.
- TCR-2 NO2: directory TROPESS.
- TCR-2 NOx emissions: directory t106, currently only for the US. Data are not publicly available.
- EPA ground-based NO2 measurements: directory US_EPA, currently only for the US. Canadian data will need to come from ECCC. 

To download ERA5 data: 
download_era5.py [year] [month]: get all the variables for the specified month and year.
download_era5.sh [year]: run download_era5.py for all the months of the specified year.
era5_loop.sh: run download_era5.sh for several years (specified in the script).

ERA5 data are at 2h frequency and 0.25 degree resolution. The Unet model takes daily averages on the grid given by (lats.npy,lons.npy). To do the regridding and time averaging:
concatenate.py: regrid all the ERA5 files in data/high_res/emacdonald/[year]/ to the grid specified by (lats.npy,lons.npy), resample to daily averages, and concatenate the entire year for each variables. Save as ERA5concatenated/[year][variable].nc. These are now in the format needed to make input files for Unet (365,56,120). No longer need save_data.py or save_data.sh to do the resampling because concatenate.py now does both steps at the same time to avoid saving intermediate files.

To make the Unet files:
inputfiles.py: combines data from the above sources. X input files are of size (364,56,120,9), dimensions (time,lat,lon,n_variables). The variables are ordered as follows:
NO2, day t 
NO2, day t-1
u10, day t 
v10, day t 
blh, day t 
sp, day t 
skt, day t 
t2m, day t 
ssrd, day t 
Some of the variables are rescaled to make the orders of magnitude more similar. Day t starts on January 2nd so that day t-1 is January 1st. February 29th is dropped.
For stage 1, the NO2 fields come from TCR-2/TROPESS. For stage 2, the TCR-2 and EPA NO2 data are combined into a single variable.  
Y input files are of shape (364,56,120,1) where the last dimension is NOx emissions (the dependent variable). These are the same for both stages, but we use later years for stage 2.


