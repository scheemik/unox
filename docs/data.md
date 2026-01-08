<a id='top'></a>
# Data

Data from various sources are used in this project as input to the U-net model and for validation.
Descriptions of each data source are found below.

## Contents

- [Data sources](#data_sources)
    - [TCR-2 NOₓ emissions](#tcr-2_nox)
        - The surface NOₓ emissions used in the "y" input files for the U-net.
    - [TCR-2 NO₂ surface data](#tcr2-no2)
        - Surface NO₂ concentrations used in the "x" input files for the U-net.
    - [ERA5 meteorological data](#era5)
        - 7 meteorological variables used in the "x" input files for the U-net, plus the land-sea mask.
        - [Download ERA5 data](#download_era5)
    - [USA EPA Air Quality data](#us_epa)
        - Ground-based NO₂ measurements used to supplement the TCR-2 NO₂ surface data in the "x" input files for stage 2 of the U-net.
    - Potential future data: ECCC Air Quality data
        - Currently using ground-based measurements only over the USA. Adding data from ECCC will provide coverage for Canada in the "x" input files for stage 2 of the U-net.
- [Creating input files for the U-net model](#make_input_files)

---
<a id='data_sources'></a>
[back to top](#top)

## Data sources

The `datafiles` directory contains data files and scripts to make the input files for the U-net model for estimating North American NOₓ emissions. 
These scripts pull from data files kept in shared directories on Animus, usually within `/data/high_res/`. 
In the descriptions below, the contents and usage of each data source are described as well as how to obtain the data, if they are publicly available. 

<a id='tcr-2_nox'></a>
[back to top](#top)

### TCR-2 (Tropospheric Chemistry Reanalysis v2) NOₓ emissions

- Directory on Animus: `/data/high_res/emacdonald/unet/datafiles/t106/`
- Filename convention: `nox_20XX_t106_US.nc` 
    - where `20XX` is the year
- Contains the variable:
    - `nox`: Surface NOₓ emissions
- Latitude extent: 24.112 to 58.878
    - Resolution: 1.121483870967742 ± 0.0004997397866077013
- Longitude extent: -126.0 to -59.625
    - Resolution: 1.125
- Grid size: 32 x 60
- Daily time frequency
- Example file: `datafiles/sample_data/nox_2019_t106_US.nc`
    - There also exists `datafiles/sample_data/TROPESS_reanalysis_mon_emi_nox_anth_2021.nc` however, while this sample file has the same latitude-longitude grid as the one above, it has been down-sampled to monthly frequency to allow for quick testing.

Note: These data are not publicly available.

<a id='tcr-2_no2'></a>
[back to top](#top)

### TCR-2 (Tropospheric Chemistry Reanalysis v2) NO₂

- Directory on Animus: `/data/high_res/emacdonald/unet/datafiles/TROPESS/`
- Institution: Jet Propulsion Laboratory
- Filename convention: `TROPESS_reanalysis_2hr_no2_sfc_20XX.nc` 
    - where `20XX` is the year
- Contains the variable:
    - `no2`: TROPESS Chemical Reanalysis Surface NO₂ 2-Hourly 2-Dimensional Product
<!-- - Latitude extent: 24.112 to 58.878 -->
- Latitude extent: -89.14 to 89.14
    - Resolution: 1.121483870967742 ± 0.0004997397866077013
<!-- - Longitude extent: -126.0 to -59.625 -->
- Longitude extent: 0 to 358.9
    - Resolution: 1.125
- Grid size: 160 x 320
- 2-hour time frequency

TO BE ADDED: Instructions on how to download these files.

<a id='era5'></a>
[back to top](#top)

### ERA5 Data

- Directory on Animus: `/data/high_res/ERA5concatenated/`
- Institution: European Centre for Medium-Range Weather Forecasts
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
- Grid size: 56 x 120
- Daily time frequency
- Example file: `datafiles/sample_data/2019_u10.nc` 

<a id='download_era5'></a>
[back to top](#top)

#### Downloading ERA5 data

The ERA5 data files described above have already been downloaded to `/data/high_res/ERA5concatenated/` on Animus. 
However, if you ever need to re-download these files, to obtain a different geographical region for example, follow the instructions below.

The extent, time frame, and variables for which to download ERA5 data are defined in the `era5_download.py` Python script.
Any of these can be modified from their defaults by:
- Extent
    - The `era5_download.py` Python script calls the variable `DEFAULT_EXTENT` from `unox/data.py`, where the default values can be changed.
- Time frame
    - The years over which to run the `era5_download.py` Python script are defined by the input arguments to the `era5_download.sh` Bash script, see below.
- Variables
    - Modify the list of variables in the `variable_names` dictionary in the `era5_download.py` Python script. The keys (short names) are arbitrary, used to rename the files once downloaded, however the values (long names) must be valid variable names within ERA5. To check what the long name of a variable is, go to the [Climate Data Store page](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download) for this data, select the variables of interest from the list, scroll down to the "Corresponding API request," and copy the "variable" list. The code under "Corresponding API request" is what was used to create the `era5_download.py` Python script.

To start the download, use the `era5_download.sh` Bash script which accepts arguments for the start and end years to download. 
For example:
```console
username@animus-c:~/unox$ bash datafiles/era5_download.sh 2005 2020 > datafiles/era5_download_log.txt 2>&1
```
That will run the `era5_download.py` script for each month within those years (2005--2020) and send the log output of each call to the file `datafiles/era5_download_log.txt`.

When downloaded, the ERA5 data are at 2-hour frequency and 0.25 degree resolution. The U-net model takes daily averages on the grid given by (`datafiles/lats.npy`, `datafiles/lons.npy`).
Running the `era5_concatenate.py` script will find all the downloaded ERA5 files in `unox/datafiles/era5_downloads/` and concatenate them into one file for each year which are output to `unox/datafiles/ERA5concatenated/`. 
As this process takes a long time, I recommend launching a `tmux` session before starting so that any network interruption between your local machine and Animus won't stop the script from running. Be sure to activate the `conda` environment _after_ lauching `tmux`.
```console
username@animus-c:~/unox$ tmux
username@animus-c:~/unox$ conda activate uplt
(uplt) username@animus-c:~/unox$ python datafiles/era5_concatenate.py
Creating directory: /home/mschee/unox/datafiles/ERA5concatenated
era5_dirs: ['2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']
Processing year directory: 2005
        Processing variable: u10 for year 2005
        Opening file: /home/mschee/unox/datafiles/era5_downloads/2005/2005_01_u10/data_stream-oper_stepType-instant.nc
        Opening file: /home/mschee/unox/datafiles/era5_downloads/2005/2005_02_u10/data_stream-oper_stepType-instant.nc
        ...
        Opening file: /home/mschee/unox/datafiles/era5_downloads/2006/2006_12_u10/data_stream-oper_stepType-instant.nc
        Frozen({'valid_time': 365, 'latitude': 56, 'longitude': 120})
        Processing variable: lsm for year 2006
        Opening file: /home/mschee/unox/datafiles/era5_downloads/2006/2006_01_lsm/data_stream-oper_stepType-instant.nc
        ...
Processing year directory: 2007
        Processing variable: u10 for year 2007
        Opening file: /home/mschee/unox/datafiles/era5_downloads/2007/2007_01_u10/data_stream-oper_stepType-instant.nc
        ...
Processing year directory: 2020
        Processing variable: u10 for year 2020
        Opening file: /home/mschee/unox/datafiles/era5_downloads/2020/2020_01_u10/data_stream-oper_stepType-instant.nc
        ...
        Opening file: /home/mschee/unox/datafiles/era5_downloads/2020/2020_12_u10/data_stream-oper_stepType-instant.nc
        Frozen({'valid_time': 366, 'latitude': 56, 'longitude': 120})
        Processing variable: lsm for year 2020
        Opening file: /home/mschee/unox/datafiles/era5_downloads/2020/2020_01_lsm/data_stream-oper_stepType-instant.nc
        ...
        Opening file: /home/mschee/unox/datafiles/era5_downloads/2020/2020_12_lsm/data_stream-oper_stepType-instant.nc
        Frozen({'valid_time': 366, 'latitude': 56, 'longitude': 120})
```
While running the `era5_concatenate.py` script, the ERA5 data are regridded to the the grid defined by the `lats.npy` and `lons.npy` files (I believe those values came from the `t106` files) and to a daily frequency. 
These are now in the format needed to make input files for U-net: (365,56,120), or (366,56,120) for leap years.

To close the `tmux` session when done, simply run the `exit` command.

<a id='us_epa'></a>
[back to top](#top)

### USA EPA Air Quality data

- Directory on Animus: `/data/high_res/US_EPA/`
- Institution: United States of America Environmental Protection Agency
- Filename convention: `<species>/<frequency>_<species>/<frequency>_42602_20XX.csv` 
    - where `20XX` is the year, and `<frequency>` is either `daily` or `hourly`, and `<species>` is one of the ID's listed in the `case` block for `$SPECIES` in the `datafiles/US_EPA_data_download.sh` script
- Latitude extent: 18.198712 to 64.84569
    - Resolution: 0.10229600438596492 ± 0.7920890308379249
- Longitude extent: -159.36624 to -66.052237
    - Resolution: 0.20463597149122806 ± 1.216681660681876
- Grid size: 56 x 120
- Daily time frequency
- Example file: `datafiles/sample_data/daily_42602_2019.csv`
    - 42602 is the ID for NO₂
    - Note: The latitude and longitude extents and resolutions were calculated solely on this example file.

<a id='download_us_epa'></a>
[back to top](#top)

#### Downloading USA EPA Air Quality data

Air Quality data are currently available from the US EPA's Air Data site. 
The data products used in this study were found on the [Pre-Generated Data Files](https://aqs.epa.gov/aqsweb/airdata/download_files.html#Daily) page, which lists the files available for each species and each year.
While each file can be downloaded individually from this page, I have created the `datafiles/US_EPA_data_download.sh` script to automate that process, downloading the data into the `/data/high_res/US_EPA/` directory on Animus. 

That script takes in the following arguments, all of which are optional:
- `-s`: Species
    - Default: `NO2`
    - Can choose `all` to download every species listed.
- `-b`: Begin year
    - Default: `1980`
- `-e`: End year
    - Default: `2024`
- `-f`: Frequency
    - Default: `daily`
    - Other options: `hourly` or `both`

To run the script and download exactly the same NO₂ data as is currently in the `/data/high_res/US_EPA/` directory on Animus, this script can be run without specifying any of the arguments.
As an example, the code below will download data for CO between 2000 and 2005 at an hourly frequency:

```console
username@animus-c:~/unox$ bash datafiles/US_EPA_data_download.sh -s CO -b 2000 -e 2005 -f hourly
Downloading hourly US EPA data for species: CO from 2000 to 2005
...
```

---
<a id='make_input_files'></a>
[back to top](#top)

## Creating input files for the U-net model

To make the U-net files:
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
Y input files are of shape (364,56,120,1) where the last dimension is NOₓ emissions (the dependent variable). These are the same for both stages, but we use later years for stage 2.


