#!/bin/bash


for year in {2008..2021}
do
  cd $year
  for f in */
  do 
    echo $f
    echo $f*nc
    cp $f*nc "${f%/}.nc"
  done 
  cd ..
done


#  unzip "$f" -d "${year}/${f%.zip}"
#  echo ${year}/${f%.zip}/
#  unzip $f -d "${year}/${f%.zip}/" 
#  unzip $f > "${year}/${f%.zip}.nc"


#for f in 2013_??_*.zip; do unzip "$f" > 2013/"${f%.zip}.nc"; done
