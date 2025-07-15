#!/bin/bash
# This script will download, sort, and unzip US EPA data for the specified years and species.

# Usage: ./download_US_EPA_data.sh <species> <start_year> <end_year>

# Takes in optional arguments:
#	$ bash download_US_EPA_data.sh -s <species>         Default: NO2
#                                  -b <begin_year>      Default: 2005
#                                  -e <end_year>        Default: 2020
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

# Check to see if input arguments are set, otherwise set defaults
if [ -z "$SPECIES" ]; then
    SPECIES="NO2"
else
    # Check to make sure the species are valid
    VALID_SPECIES=("O3" "SO2" "CO" "NO2")
    if [[ ! " ${VALID_SPECIES[@]} " =~ " ${SPECIES} " ]]; then
        echo "Invalid species, $SPECIES. Valid options are: ${VALID_SPECIES[*]}"
        exit 1
    fi
fi
if [ -z "$START_YEAR" ]; then
    START_YEAR=2005
else
    # Check to make sure the start year is between 1980-2024
    if [[ ! "$START_YEAR" =~ ^[0-9]{4}$ ]] || [ "$START_YEAR" -lt 1980 ] || [ "$START_YEAR" -gt 2024 ]; then
        echo "Invalid start year, $START_YEAR. Must be between 1980 and 2024."
        exit 1
    fi
fi
if [ -z "$END_YEAR" ]; then
    END_YEAR=2020
else
    # Check to make sure the end year is between 1980-2024
    if [[ ! "$END_YEAR" =~ ^[0-9]{4}$ ]] || [ "$END_YEAR" -lt 1980 ] || [ "$END_YEAR" -gt 2024 ]; then
        echo "Invalid end year, $END_YEAR. Must be between 1980 and 2024."
        exit 1
    fi
fi
if [ -z "$FREQUENCY" ]; then
    FREQUENCY="daily"
else
    # Check to make sure the frequency is valid
    if [[ "$FREQUENCY" != "daily" && "$FREQUENCY" != "hourly" ]]; then
        echo "Invalid frequency, $FREQUENCY. Valid options are: daily, hourly"
        exit 1
    fi
fi

echo "Downloading US EPA data for species: $SPECIES from $START_YEAR to $END_YEAR"

# Create the data directory if it doesn't exist
DATA_DIR="/data/high_res/US_EPA"
mkdir -p "$DATA_DIR"
# Create the species directory if it doesn't exist
SPECIES_DIR="$DATA_DIR/$SPECIES"
mkdir -p "$SPECIES_DIR"

# Get the ID number based on species
case "$SPECIES" in
    "O3") ID="44201" ;;
    "SO2") ID="42401" ;;
    "CO") ID="42101" ;;
    "NO2") ID="42602" ;;
    *) echo "Invalid species: $SPECIES"; exit 1 ;;
esac

# Loop through the years and download the data
for YEAR in $(seq $START_YEAR $END_YEAR); do
    # Construct the URL
    URL="https://aqs.epa.gov/aqsweb/airdata/${FREQUENCY}_${ID}_${YEAR}.zip"
    # Download the file
    wget -q --show-progress "$URL" -O "$SPECIES_DIR/${FREQUENCY}_${ID}_${YEAR}.zip"
    
    # Check if the download was successful
    if [ $? -ne 0 ]; then
        echo "Failed to download data for year: $YEAR"
        continue
    fi
    
    # Unzip the file
    unzip -o "$SPECIES_DIR/${FREQUENCY}_${ID}_${YEAR}.zip" -d "$SPECIES_DIR"
    
    # Remove the zip file after extraction
    rm "$SPECIES_DIR/${FREQUENCY}_${ID}_${YEAR}.zip"
done