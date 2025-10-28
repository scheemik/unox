#!/bin/bash

# Execute from the datafiles/ directory

ERA5_DIR="era5_downloads"
for year in {2005..2020}
do
  for f in ${ERA5_DIR}/${year}/*
  do 
    # echo $f
    # If any files contain "msk", replace with "lsm"
    if [[ $f == *"msk"* ]]; then
      new_f=${f//msk/lsm}
      mv "$f" "$new_f"
      echo "Renamed $f to $new_f"
    fi
  done 
done
