#!/bin/bash

#regrid and resample several years of ERA5 data 
#need to redo 2007

for year in {2006..2013}
do
  echo $year
  python save_data.py $year
done

