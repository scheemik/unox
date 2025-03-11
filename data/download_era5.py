import cdsapi
import sys

year = sys.argv[1]
print(year)
#variable_short = sys.argv[2]
#print(variable_short)
#savename = year+variable_short+'.zip'

month = sys.argv[2]
print(month)


variable_names = {"u10":"10m_u_component_of_wind", "v10":"10m_v_component_of_wind", "t2m":"2m_temperature", "ps":"surface_pressure",
                     "tsk":"skin_temperature", "srd":"surface_solar_radiation_downwards", "blh":"boundary_layer_height"}
#variable = [variable_names[variable_short]]
# variable = [variable_names[v] for v in variable_names]

#for v in variable_names:
for v in variable_names:
    variable = [variable_names[v]]
    print(variable)
    savename = year+'_'+month+'_'+v+'.zip'
    print(savename)

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
        "download_format": "zip",
        "area": [75, -175, 11, -39]  #[north, west, south, east]
    }



    target = savename
    client = cdsapi.Client()
    client.retrieve(dataset, request, target)
