#!/bin/bash
# Author: Daniel Sequeira
# Date : 31 July 2025
# Merge daily CO files to Yearly files using cdo version 2.0.4
# This can take several hours to run on animus

START_YEAR=2001
END_YEAR=2021
COPATH="/users/jk/20/dbj/ESSDA/GC_v14.1.1/gc_2x25_47L_merra2_tagCO/OutputDir"

# Confirm that the `datafiles` directory exists
if [ ! -d "datafiles" ]; then
    echo "Directory `./datafiles` does not exist. Are you in the correct path?"
    exit 1
fi

# Create a function which takes in a title and extension
# and merges all files with that title and extension
merge_CO_files() {
    local TITLE=$1
    local EXT=$2
    # Create output directory if it doesn't exist
    if [ ! -d "./datafiles/${TITLE}_merged" ]; then
        mkdir -p "./datafiles/${TITLE}_merged"
    fi
    for YEAR in $(seq $START_YEAR $END_YEAR); do
        # Construct the filename
        FILENAME="./datafiles/${TITLE}_merged/${TITLE}_${YEAR}.nc"
        echo "Creating ${FILENAME}"
        # Construct input string
        INPUT="${COPATH}/${TITLE}.${YEAR}*${EXT}"
        # Call to cdo
        cdo mergetime $INPUT $FILENAME
    done
}

# Call the function with desired title and extension
merge_CO_files "HEMCO_diagnostics" ".nc"
merge_CO_files "GEOSChem.SpeciesConc" ".nc4"

# Note, when running this script, expect a lot of warnings like:
# Warning (scan_hybrid_formulaterms): NetCDF: Variable not found - hyai
# Warning (scan_hybrid_formulaterms): NetCDF: Variable not found - hybi
