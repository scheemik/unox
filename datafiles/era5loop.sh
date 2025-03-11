#!/bin/bash

#run download_era5.sh for several years
years="2004 2006 2007 2012"

for year in $years
do
  echo $year
  mkdir ${year}
  ./download_era5.sh $year
done

