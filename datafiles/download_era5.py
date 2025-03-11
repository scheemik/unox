'''
Code for downloading ERA5 data for the given month and year, for the Unet North American domain.
Can be run with download_era5.sh for multiple months and era5loop.sh for multiple years.
You will need to register at https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download
and accept the license. Data can be downloaded directly from their website, or through the cdsapi using this script.
To use the script, you need a .cdsapirc in your $HOME directory that contains the following two lines:
url: https://cds.climate.copernicus.eu/api
key: [your API token from your CDS profile]
'''

import cdsapi
import sys

#year and month are command line arguments
#files are huge so it's easier to do one month of one variable per file
year = sys.argv[1]
print(year)

month = sys.argv[2]
print(month)

#variable short and long names
variable_names = {"u10":"10m_u_component_of_wind", "v10":"10m_v_component_of_wind", "t2m":"2m_temperature", "sp":"surface_pressure",
                     "skt":"skin_temperature", "ssrd":"surface_solar_radiation_downwards", "blh":"boundary_layer_height"}


for v in variable_names:
    variable = [variable_names[v]]
    print(variable)
    savename = year+'_'+month+'_'+v+'.zip'   #directory where data will be saved
    print(savename)

    #code copied from the CDS download website, generalized to be loopable
    dataset = "reanalysis-era5-single-levels"
    request = {
        "product_type": ["reanalysis"],
        "variable": variable,
        "year": [year],
        "month": [month],
        "day": [
            "01", "02", "03",
            "04", "05", "06",
            "07", "08", "09",
            "10", "11", "12",
            "13", "14", "15",
            "16", "17", "18",
            "19", "20", "21",
            "22", "23", "24",
            "25", "26", "27",
            "28", "29", "30",
            "31"
        ],
        "time": [
            "00:00", "01:00", "02:00",
            "03:00", "04:00", "05:00",
            "06:00", "07:00", "08:00",
            "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00",
            "15:00", "16:00", "17:00",
            "18:00", "19:00", "20:00",
            "21:00", "22:00", "23:00"
        ],
        "data_format": "netcdf",
        "download_format": "zip",    #changing this to "unarchived" might make things easier, but then have to change savename above
        "area": [75, -175, 11, -39]  #[north, west, south, east]
    }



    target = savename   #where data will be stored
    client = cdsapi.Client()
    client.retrieve(dataset, request, target)
