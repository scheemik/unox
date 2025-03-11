#!/bin/bash

year=$1
#month=$2

#mkdir ${year}_${month}/
mkdir ${year}

months='01 02 03 04 05 06 07 08 09 10 11 12'
# months='04'

for month in $months
do
  echo $month
  python download_era5.py $year $month  #get all the variables for the chosen year and month and save them as 20xx_mm_var.zip

  for f in ${year}*_${month}*.zip
  do
  echo "${year}"
#  unzip "$f" -d "${year}/${f%.zip}"
  echo ${year}/${f%.zip}/
  unzip $f -d "${year}/${f%.zip}/" 
#  unzip $f > "${year}/${f%.zip}.nc"
  done

done

#for f in 2013_??_*.zip; do unzip "$f" > 2013/"${f%.zip}.nc"; done
