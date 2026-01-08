# Data files

This directory contains data files and scripts to make the input files for the Unet model for estimating North American NOx emissions. 

## Data sources summary:
- TCR-2 NOx emissions:
    - The surface NOx emissions used in the "y" input files for the Unet.
- ERA5 data:
    - 7 meteorological variables used in the "x" input files for the Unet plus the land-sea mask.
- TCR-2 NO2: directory TROPESS.
- EPA ground-based NO2 measurements: directory US_EPA, currently only for the US. Canadian data will need to come from ECCC. 

## TCR-2 NOx emissions

- Directory on Animus: `/data/high_res/emacdonald/unet/datafiles/t106/`
- Filename convention: `nox_20XX_t106_US.nc` 
    - where `20XX` is the year
- Contains the variable:
    - `nox`: Surface NOx emissions
- Latitude extent: 24.112 to 58.878
    - Resolution: 1.121483870967742 ± 0.0004997397866077013
- Longitude extent: -126.0 to -59.625
    - Resolution: 1.125
- Daily time frequency

Note: These data are not publicly available.

## ERA5 Data

- Directory on Animus: `/data/high_res/ERA5concatenated/`
- Filename convention: `20XX<var>.nc` 
    - where `20XX` is the year and `<var>` is one of the following variables:
        - `blh`: Boundary layer height
        - `lsm`: Land-sea mask
        - `skt`: Skin temperature
        - `sp`: Surface pressure
        - `ssrd`: Surface short-wave (solar) radiation downwards
        - `t2m`: 2 metre temperature
        - `u10`: 10 metre U wind component
        - `v10`: 10 metre V wind component
- Latitude extent: 11.78 to 73.46
    - Resolution: 1.121472716331482 ± 0.0004995913477614522
- Longitude extent: -174.4 to -40.5
    - Resolution: 1.125
- Daily time frequency

### Downloading ERA5 data

Start with the `era5_download.sh` script which accepts arguments for the start and end years to download. For example:
```console
bash datafiles/dera5_download.sh 2005 2020 > datafiles/era5_download_log.txt 2>&1
```
That will run the `era5_download.py` script for each month within those years and send the log output of each call to the file `datafiles/era5_download_log.txt`.

ERA5 data are at 2h frequency and 0.25 degree resolution. The Unet model takes daily averages on the grid given by (lats.npy,lons.npy).
Running the `era5_concatenate.py` script will find all the downloaded ERA5 files in `unox/datafiles/era5_downloads/` and concatenate them into one file for each year which are output to `unox/datafiles/ERA5concatenated/`. 
In that process, the ERA5 data are regridded to the the grid defined by the `lats.npy` and `lons.npy` files (I believe those values came from the `t106` files) and onto daily frequency. 
These are now in the format needed to make input files for Unet: (365,56,120), or (366,56,120) for leap years.

## TCR-2 NO2

- Directory on Animus: `emacdonald/unet/datafiles/TROPESS/`
- Filename convention: `TROPESS_reanalysis_2hr_no2_sfc_20XX.nc` 
    - where `20XX` is the year
- Contains the variable:
    - `no2`: Surface NOx emissions
- Latitude extent: 24.112 to 58.878
    - Resolution: 1.121483870967742 ± 0.0004997397866077013
- Longitude extent: -126.0 to -59.625
    - Resolution: 1.125
- Daily time frequency

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


