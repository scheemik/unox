<a id='top'></a>
# Data

Data from various sources are used in this project as input to the U-net model and for validation.
Descriptions of each data source are found below.
This guide assumes you have followed the instructions on the {doc}`Installation <installation>` page.

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
        - [Downloading USA EPA Air Quality data](#download_us_epa)
    - Potential future data: ECCC Air Quality data
        - Currently using ground-based measurements only over the USA. Adding data from ECCC will provide coverage for Canada in the "x" input files for stage 2 of the U-net.
- [Input files for the U-net model](#input_files)
    - [Input file structure](#input_file_structure)
    - [Creating input files](#make_input_files)

---
<a id='data_sources'></a>
[back to top](#top)

## Data sources

The `datafiles` directory contains data files and scripts to make the input files for the U-net model for estimating North American NOₓ emissions. 
These scripts pull from data files kept in shared directories **<ins>on Animus</ins>**, usually within `/data/high_res/`. 
In the descriptions below, the contents and usage of each data source are described as well as how to obtain the data, if they are publicly available. 
When listing the latitude and longitude resolutions, a "±" symbol indicates that the resolution is irregular.
That is, the value before the symbol is the average difference in values while the value after the symbol is the standard deviation of the difference in values.
For example, the [TCR-2 NOₓ emissions](#tcr-2_nox) latitude values have an average resolution of 1.121483870967742 with a standard deviation of 0.0004997397866077013.

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
**<ins>Only run this if the data is no longer on Animus in</ins>** `/data/high_res/`:
```console
username@animus-c:~/unox$ bash datafiles/era5_download.sh 2005 2020 > datafiles/era5_download_log.txt 2>&1
```
That will run the `era5_download.py` script for each month within those years (2005--2020) and send the log output of each call to the file `datafiles/era5_download_log.txt`.

When downloaded, the ERA5 data are at 2-hour frequency and 0.25 degree resolution. The U-net model takes daily averages on the grid given by (`datafiles/lats.npy`, `datafiles/lons.npy`).
Running the `era5_concatenate.py` script will find all the downloaded ERA5 files in `unox/datafiles/era5_downloads/` and concatenate them into one file for each year which are output to `unox/datafiles/ERA5concatenated/`. 
As this process takes a long time, I recommend launching a `tmux` session before starting so that any network interruption between your local machine and Animus won't stop the script from running. Be sure to activate the `conda` environment **<ins>on Animus</ins>** _after_ lauching `tmux`.
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

Note that the USA EPA Air Quality Data is provided in `.csv` format where each (I should check whether I remove zero values from the list of differences in lat/lon before calculating the average and standard deviation)

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
As an example, the code below will download data for CO between 2000 and 2005 at an hourly frequency. **<ins>Only do this if the data is no longer on  in</ins>** `/data/high_res/`.

```console
username@animus-c:~/unox$ bash datafiles/US_EPA_data_download.sh -s CO -b 2000 -e 2005 -f hourly
Downloading hourly US EPA data for species: CO from 2000 to 2005
...
```

---
<a id='input_files'></a>
[back to top](#top)

## Input files for the U-net model

When running the U-net model, the input data are loaded from a netCDF input file. 
These files are created to have a consistent structure, with data from all the above sources interpolated onto a common grid in space and time. 
You will generally only need to create new input files when investigating a new geographic area, a different species, or adding new variables.
The process of creating new input files can take some time. 
However, the model run configuration files (discussed in the {doc}`Workflow <../docs_dev/workflow>` guide) can be used to specify exactly what data are pulled from the input netCDF files for a particular run. 
Therefore, after spending the time to create an input file, you should be able to try many different kinds of model runs by modifying the configuration file.

<a id='input_file_structure'></a>
[back to top](#top)

### Input file structure

The input files are netCDFs. 
Using `xarray` you can look at the structure of such a file by opening it.
Below is a text representation of the output. 
However, if the below python commands are executed in a Jupyter Notebook cell **<ins>on Animus</ins>**, the structure becomes interactive, allowing for more exploration (see {doc}`Analysis <../analysis>`).

```python
import xarray as xr

xr.open_dataset('inputfiles/no2_2019_JFM/no2_2019_JFM.nc')
```
```console
<xarray.Dataset> Size: 62MB
Dimensions:     (time: 89, lat: 56, lon: 120, var: 1)
Coordinates:
  * lat         (lat) float32 224B 11.78 12.9 14.02 15.14 ... 71.21 72.34 73.46
  * lon         (lon) float32 480B -174.4 -173.2 -172.1 ... -42.75 -41.62 -40.5
  * time        (time) object 712B 2019-01-02 00:00:00 ... 2019-03-31 00:00:00
Dimensions without coordinates: var
Data variables: (13/13)
    nox         (time, lat, lon, var) float64 5MB ...
    no2         (time, lat, lon) float64 5MB ...
    no2_tm1     (time, lat, lon) float64 5MB ...
    u10         (time, lat, lon) float64 5MB ...
    v10         (time, lat, lon) float64 5MB ...
    blh         (time, lat, lon) float64 5MB ...
    sp          (time, lat, lon) float64 5MB ...
    skt         (time, lat, lon) float64 5MB ...
    t2m         (time, lat, lon) float64 5MB ...
    ssrd        (time, lat, lon) float64 5MB ...
    lsm         (time, lat, lon) float64 5MB ...
    no2_s2      (time, lat, lon) float64 5MB ...
    no2_s2_tm1  (time, lat, lon) float64 5MB ...
Attributes: (13/17)
    description:        Input data for the Unet model. Data for each year is ...
    y_var:              nox
    emiss_dir:          /data/high_res/emacdonald/unet/datafiles/t106
    emiss_pre:          nox_
    emiss_post:         _t106_US.nc
    nan_fill:           0
    ...                 ...
    x1_vars:            ['no2', 'no2_tm1', 'u10', 'v10', 'blh', 'sp', 'skt', 't2m', 'ssrd']
    x2_vars:            ['no2_s2', 'no2_s2_tm1', 'u10', 'v10', 'blh', 'sp', 'skt', 't2m', 'ssrd']
    data_dir:           /data/high_res
    chemra_path:        emacdonald/unet/datafiles/TROPESS/TROPESS_reanalysis_...
    insitu_path:        US_EPA/NO2/daily_NO2/daily_42602_
    era5_path:          ERA5concatenated
    stages:             [1 2]
```

In the attributes, it is indicated which variables are "y" and which are "x".
- "y" variable
    - The variable which the model is trying to emulate, the "target" variable.
    - In this case, `y_var` is `nox`.
    - Note that this variable has an extra `var` dimension. This is a dummy dimension to ensure that the "y" variable data has the same number of dimensions as the "x" variables when bundled together.
- "x" variables
    - The variables which the model combines in particular ways to create a mapping to the target "y" variable. 
    - Ideally, none of these variables should be dependent on each other.

The input file contains two lists of "x" variables: `x1_vars` and `x2_vars`. 
These correspond to the "x" variables used in Stage 1 and Stage 2 of the training. 
In Stage 1, the ground-based data is not used, only chemical data from reanalyses. 
In Stage 2, the pre-trained model from Stage 1 is retrained on input data which is supplemented with ground-based data.
For the case above, the chemical data from reanalyses that is used in Stage 1 is `no2`. 
When training in Stage 2, the model is given `no2_s2` which is the same as `no2` except for locations and times for which ground-based data is available.

There is also the variable `no2_tm1`.
This represents the `no2` at "T-minus 1 day", that is, the value of `no2` at the same location the day before. 
It is for this reason that the dataset does not start on January 1st, where the value of `no2_tm1` would be from December 31st of the previous year. 
Therefore, the dataset starts on January 2nd where the value of `no2_tm1` is the value of `no2` from January 1st.
The variable `no2_s2_tm1` is the equivalent of `no2_tm1` for Stage 2. 

Overall, for Stage 1 or 2, the number of "x" variables is equal to the number of ERA5 meteorological variables (of which there are 7 currently) plus 2 (one for `no2` and one for `no2_tm1`).

The data in the input netCDF were originally stored as separate `.npy` files, each one containing a Numpy array of either the "x" or "y" data for a particular year for a particular stage.
These contained no metadata, and so it became difficult to document which input files covered which geographical regions and contained which variables.
I reconfigured the files to be in netCDF format so that the metadata is readily accessible and easily readable by both human and machine. 

<a id='make_input_files'></a>
[back to top](#top)

### Creating input files

To create an input netCDF, use the `make_all_input_files()` function from the `input` module.
This function has no required arguments, however it is a good idea to pass in `output_dir`, the name of the subdirectory that will be created under the `inputfiles` directory where the netCDF and corresponding `input_metadata.json` file are stored. 
The `input_metadata.json` file contains a dictionary that is build in the process of creating the input file which contains an overview of what the netCDF contains.
If you are working with multiple different input files, the `input_metadata.json` files offer a quick way to check which file you might want to use, whether it might span a different set of years, contain a different set of variables, or use different data sources.

By default, the `make_all_input_files()` function will add all the data from 2005 through 2020 from the data sources described above associated with NOₓ, including variables for Stage 2 training. 
However, you can pass keyword arguments to change the behavior in many ways.

Note that it takes a long time, approximately an hour **<ins>on Animus</ins>**, to create an input netCDF, as can be seen by the timing information in the output below.
This is largely due to the process of creating the Stage 2 data variables which involves a nested for-loop. 
Because there is presently little need to create many input files rapidly, I have not optimized this part of the code. 

```python
from unox.input import make_all_input_files

make_all_input_files(
    output_dir='no2_2005-2020',
)
```
```console
Note: It may take around an hour to generate all input files.
Creating y input data...
	Creating y input data for nox in 2005...
	Creating y input data for nox in 2006...
	Creating y input data for nox in 2007...
	Creating y input data for nox in 2008...
	Creating y input data for nox in 2009...
	Creating y input data for nox in 2010...
	Creating y input data for nox in 2011...
	Creating y input data for nox in 2012...
	Creating y input data for nox in 2013...
	Creating y input data for nox in 2014...
	Creating y input data for nox in 2015...
	Creating y input data for nox in 2016...
	Creating y input data for nox in 2017...
	Creating y input data for nox in 2018...
	Creating y input data for nox in 2019...
	Creating y input data for nox in 2020...
Concatenating the y datasets
Saving y inputs to inputfiles/no2_2005-2020/no2_2005-2020.nc
Creating x input data...
	Creating x input file for 2005...
	Creating x input file for 2006...
	Creating x input file for 2007...
	Creating x input file for 2008...
	Creating x input file for 2009...
	Creating x input file for 2010...
	Creating x input file for 2011...
	Creating x input file for 2012...
	Creating x input file for 2013...
	Creating x input file for 2014...
	Adding stage 2 data for no2 in 2014
	Function 'fill_w_insitu' execution time: 0:06:42.550980
	Creating x input file for 2015...
	Adding stage 2 data for no2 in 2015
	Function 'fill_w_insitu' execution time: 0:06:58.153890
	Creating x input file for 2016...
	Adding stage 2 data for no2 in 2016
	Function 'fill_w_insitu' execution time: 0:07:04.098303
	Creating x input file for 2017...
	Adding stage 2 data for no2 in 2017
	Function 'fill_w_insitu' execution time: 0:06:56.500722
	Creating x input file for 2018...
	Adding stage 2 data for no2 in 2018
	Function 'fill_w_insitu' execution time: 0:07:04.373900
	Creating x input file for 2019...
	Adding stage 2 data for no2 in 2019
	Function 'fill_w_insitu' execution time: 0:07:05.905807
	Creating x input file for 2020...
	Adding stage 2 data for no2 in 2020
	Function 'fill_w_insitu' execution time: 0:07:14.309329
Concatenating the x datasets
Saving x inputs to inputfiles/no2_2005-2020/no2_2005-2020.nc
Sorting the dataset by time.
Sorting the y data by time.
Completed making all input files.
	Function 'make_all_input_files' execution time: 1:10:13.798157
```

Note that, in the process of making an input file, all instances of February 29th are dropped using the method `convert_calendar('noleap')`.
This is to make the years all the same length.

Once an input file has been created, you can now go through the {doc}`Workflow <../docs_dev/workflow>` of setting up a run on Animus, transferring that to Trillium, running the U-net model, and bringing the result back to Animus for analysis.