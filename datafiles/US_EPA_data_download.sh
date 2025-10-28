#!/bin/bash
# Author: Mikhail Schee
# Date: 2025-07-15
# This script will download, sort, and unzip US EPA data for the specified years and species.

# Usage: ./download_US_EPA_data.sh <species> <start_year> <end_year>

# Takes in optional arguments:
#	$ bash download_US_EPA_data.sh -s <species>         Default: NO2
#                                  -b <begin_year>      Default: 1980
#                                  -e <end_year>        Default: 2024
#                                  -f <frequency>       Default: daily

# Having a ":" after a flag means an option is required to invoke that flag
while getopts s:b:e:f: option
do
	case "${option}"
		in
		s) SPECIES=${OPTARG};;
        b) START_YEAR=${OPTARG};;
        e) END_YEAR=${OPTARG};;
        f) FREQUENCY=${OPTARG};;
	esac
done

VALID_SPECIES=("O3" "SO2" "CO" "NO2" 
               "PM25FRM" "PM25nFRM" "PM10" "PMc" 
               "PM25SPEC" "PM10SPEC" "WIND" "TEMP" 
               "PRESS" "RH_and_DP" "HAPs" "VOCs" 
               "NONOxNOy" "LEAD")

# Check to see if input arguments are set, otherwise set defaults
if [ -z "$SPECIES" ]; then
    SPECIES="all"
else
    # Check to make sure the species are valid
    if [[ ! " ${VALID_SPECIES[@]} " =~ " ${SPECIES} " ]] && [ ! "${SPECIES}" == "all" ]; then
        echo "Invalid species, $SPECIES. Valid options are: ${VALID_SPECIES[*]} or all."
        exit 1
    fi
fi
if [ -z "$START_YEAR" ]; then
    START_YEAR=1980
else
    # Check to make sure the start year is between 1980-2024
    if [[ ! "$START_YEAR" =~ ^[0-9]{4}$ ]] || [ "$START_YEAR" -lt 1980 ] || [ "$START_YEAR" -gt 2024 ]; then
        echo "Invalid start year, $START_YEAR. Must be between 1980 and 2024."
        exit 1
    fi
fi
if [ -z "$END_YEAR" ]; then
    END_YEAR=2024
else
    # Check to make sure the end year is between 1980-2024
    if [[ ! "$END_YEAR" =~ ^[0-9]{4}$ ]] || [ "$END_YEAR" -lt 1980 ] || [ "$END_YEAR" -gt 2024 ]; then
        echo "Invalid end year, $END_YEAR. Must be between 1980 and 2024."
        exit 1
    fi
fi
if [ -z "$FREQUENCY" ]; then
    FREQUENCY="both"  # Default to both daily and hourly
else
    # Check to make sure the frequency is valid
    if [[ "$FREQUENCY" != "daily" && "$FREQUENCY" != "hourly" && "$FREQUENCY" != "both" ]]; then
        echo "Invalid frequency, $FREQUENCY. Valid options are: daily, hourly, or both."
        exit 1
    fi
fi

# Set the local directory in which the data will be stored
DATA_DIR="/data/high_res/US_EPA"

# Function to download and unzip one set of US EPA data
download_US_EPA_data() {
    local SPECIES=$1
    local START_YEAR=$2
    local END_YEAR=$3
    local FREQUENCY=$4

    echo "Downloading $FREQUENCY US EPA data for species: $SPECIES from $START_YEAR to $END_YEAR"

    # Create the data directory if it doesn't exist
    mkdir -p "$DATA_DIR"
    # Create the species directory if it doesn't exist
    SPECIES_DIR="$DATA_DIR/$SPECIES"
    mkdir -p "$SPECIES_DIR"
    # Create the freqency directory if it doesn't exist
    FREQUENCY_DIR="$SPECIES_DIR/${FREQUENCY}_${SPECIES}"
    mkdir -p "$FREQUENCY_DIR"

    # Get the ID number based on species
    case "$SPECIES" in
        # Criteria gases
        "O3") ID="44201" ;;
        "SO2") ID="42401" ;;
        "CO") ID="42101" ;;
        "NO2") ID="42602" ;;
        # Particulate matter
        "PM25FRM") ID="88101" ;;
        "PM25nFRM") ID="88502" ;;
        "PM10") ID="81102" ;;
        "PMc") ID="86101" ;;
        "PM25SPEC") ID="SPEC" ;;
        "PM10SPEC") ID="PM10SPEC" ;;
        # Meteorological
        "WIND") ID="WIND" ;;
        "TEMP") ID="TEMP" ;;
        "PRESS") ID="PRESS" ;;
        "RH_and_DP") ID="RH_DP" ;;
        # Toxics, Percoursors, and Lead
        "HAPs") ID="HAPS" ;;
        "VOCs") ID="VOCS" ;;
        "NONOxNOy") ID="NONOxNOy" ;;
        "LEAD") ID="LEAD" ;;
        *) echo "Invalid species: $SPECIES"; exit 1 ;;
    esac

    # Loop through the years and download the data
    for YEAR in $(seq $START_YEAR $END_YEAR); do
        # Construct the file name
        FILENAME="${FREQUENCY}_${ID}_${YEAR}"
        # Check if the csv or zip file already exists locally
        if [ -f "$FREQUENCY_DIR/$FILENAME.csv" ] || [ -f "$FREQUENCY_DIR/$FILENAME.zip" ]; then
            echo "File $FILENAME already exists, skipping download."
            continue
        else
            # Construct the URL
            URL="https://aqs.epa.gov/aqsweb/airdata/${FILENAME}.zip"
            # Download the file
            wget -q --show-progress "$URL" -O "$FREQUENCY_DIR/${FILENAME}.zip"
            
            # Check if the download was successful
            if [ $? -ne 0 ]; then
                echo "Failed to download data for year: $YEAR"
                continue
            fi
            
            # Unzip the file
            # unzip -o "$FREQUENCY_DIR/${FILENAME}.zip" -d "$FREQUENCY_DIR"
            
            # Remove the zip file after extraction
            # rm "$FREQUENCY_DIR/${FILENAME}.zip"
        fi
    done
}

# If downloading for all species, loop through each species
if [ "$SPECIES" == "all" ]; then
    # If downloading both daily and hourly data
    if [ "$FREQUENCY" == "both" ]; then
        for SPECIES in "${VALID_SPECIES[@]}"; do
            download_US_EPA_data "$SPECIES" "$START_YEAR" "$END_YEAR" "daily"
            download_US_EPA_data "$SPECIES" "$START_YEAR" "$END_YEAR" "hourly"
        done
    else
        for SPECIES in "${VALID_SPECIES[@]}"; do
            download_US_EPA_data "$SPECIES" "$START_YEAR" "$END_YEAR" "$FREQUENCY"
        done
    fi
else
    # If downloading both daily and hourly data
    if [ "$FREQUENCY" == "both" ]; then
        download_US_EPA_data "$SPECIES" "$START_YEAR" "$END_YEAR" "daily"
        download_US_EPA_data "$SPECIES" "$START_YEAR" "$END_YEAR" "hourly"
    else
        # Otherwise, just download for the specified species
        download_US_EPA_data "$SPECIES" "$START_YEAR" "$END_YEAR" "$FREQUENCY"
    fi
fi