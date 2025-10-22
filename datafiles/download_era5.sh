#!/bin/bash

# Launch with tmux and pipe the output to a log file:
# $ tmux
# $ conda activate uplt
# $ bash datafiles/download_era5.sh 2005 2020 > datafiles/download_era5_log_mine.txt 2>&1

#Download ERA5 data for all variables for every month in the given year
start_year=$1   #command line argument 
end_year=$2

# Be sure to activate conda environment before running this script

ERA5_DIR=~/unox/datafiles/era5_downloads/

months='01 02 03 04 05 06 07 08 09 10 11 12'

for ((year=start_year; year<=end_year; year++))
do
  echo "Year: ${year}"
  mkdir ${ERA5_DIR}${year}
  for month in $months
  do
    echo "Month: ${month}"
    # Get all the variables for the chosen year and month and save them as 20xx_mm_var.zip
    python ~/unox/datafiles/download_era5.py $year $month
    # Unzip all the zip files
    for f in ${ERA5_DIR}${year}/${year}*_${month}*.zip
    do
      echo ${f%.zip}
      unzip $f -d "${f%.zip}/"
    done
  done
done
