#!/bin/bash
# Author: Daniel Sequeira
# Date : 31 July 2025
# Merge daily CO files to Yearly files

START_YEAR=2001
END_YEAR=2021


# TITLE="HEMCO_diagnostics"
# EXT=".nc"
TITLE="GEOSChem.SpeciesConc"
EXT=".nc4"

for YEAR in $(seq $START_YEAR $END_YEAR); do
    # Construct the filename
    FILENAME="/home/dsequeira/unox/datafiles/${TITLE}_merged/${TITLE}_${YEAR}.nc"
    echo $FILENAME
    # Construct input string
    INPUT="/users/jk/20/dbj/ESSDA/GC_v14.1.1/gc_2x25_47L_merra2_tagCO/OutputDir/${TITLE}.${YEAR}*${EXT}"
    # ls $INPUT
    # Call to cdo
    cdo mergetime $INPUT $FILENAME
done
