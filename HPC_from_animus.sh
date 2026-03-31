#!/bin/bash
# Author: Mikhail Schee
# 2025-09-08

# To be run on Animus.
# Run this script to copy files to an HPC cluster from Animus.
# Takes in the following arguments:
#	$ bash HPC_from_animus.sh -f <filename>      Ex: no2_sample_input
#                             -i <inputfile>     Look for input file directory based on filename
#                             -c <cluster>       HPC cluster to transfer from (default: trillium)
#
# Note: Each file in list must be preceded by the -f flag. Ex:
#	$ bash HPC_from_animus.sh -f test_file1 -f test_file2
#
# Note: To transfer inputfile, specify the input file name in the -f flag. Ex:
#	$ bash HPC_from_animus.sh -f no2_sample_input -i

# Having a ":" after a flag means an option is required to invoke that flag
while getopts "f:ic:" option;
do
	case $option
		in
		f) FILENAMES+=("$OPTARG");;
        i) INPUT_FILES=i;;
        c) CLUSTER=${OPTARG}
	esac
done
shift $((OPTIND -1))

# check to see if arguments were passed
if [ -z "$FILENAMES" ]
then
	echo "-f, No files specified, exiting"
	exit 1
fi
if [ -z "$CLUSTER" ]
then
    CLUSTER="trillium"
    echo "-c, No cluster specified, defaulting to $CLUSTER"
else
    echo "-c, Copying from $CLUSTER"
fi
if [ "$INPUT_FILES" = i ]
then
	DIR_PREFIX="inputfiles"
	echo "-i, Copying full input file directory for ${FILENAMES[*]} to $CLUSTER from Animus"
else
	DIR_PREFIX=""
fi

###############################################################################

# Source parameters from file
source HPC_params.sh

# Determine remote server and project directory based on chosen cluster
if [ "$CLUSTER" = "trillium" ]; then
    # Specify the remote server address
    REMOTE_SERVER="trillium.alliancecan.ca"
    # Specify project directory
    PROJECT_DIR="$TRIL_SCRATCH/$TRIL_PROJ_DIR"
    # Specify the identity file for SSH
    IDENTITY_FILE="$TRIL_IDENTITY_FILE"
elif [ "$CLUSTER" = "mist" ]; then
    # Specify the remote server address
    REMOTE_SERVER="mist.scinet.utoronto.ca"
    # Specify project directory
    PROJECT_DIR="$MIST_SCRATCH/$MIST_PROJ_DIR"
    # Specify the identity file for SSH
    IDENTITY_FILE="$MIST_IDENTITY_FILE"
else
    echo "Unknown cluster: $CLUSTER. Exiting."
    exit 1
fi

# Copy files or directories from Animus to HPC
for FILE in "${FILENAMES[@]}"; do
    if [ "$INPUT_FILES" = i ]; then
        # Check whether the corresponding directory exists on Animus
        if [ ! -d "$DIR_PREFIX/$FILE" ]; then
            echo "Directory $DIR_PREFIX/$FILE does not exist on Animus, aborting."
            exit 1
        fi
        FILE="$DIR_PREFIX/$FILE/"
    fi
    scp -r -i $IDENTITY_FILE "$FILE" $HPC_USERNAME@$REMOTE_SERVER:$PROJECT_DIR/$FILE
done