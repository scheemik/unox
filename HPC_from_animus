#!/bin/bash
# Author: Mikhail Schee
# 2025-09-08

# Run this script to copy files to an HPC cluster from Animus.
# To be run on Animus.
# Takes in the following arguments:
#	$ bash HPC_from_animus.sh -f <filename>      Ex: no2_sample_input
#                             -i <HPC_job>       Look for input file directory based on filename
#                             -c <cluster>       HPC cluster to transfer from (default: trillium)
#
# Note: Each file in list must be preceded by the -f flag. Ex:
#	$ bash HPC_from_animus.sh -f test_file1 -f test_file2

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
	DIR_PREFIX="/inputfiles"
	echo "-i, Copying full input file directory for ${FILENAMES[*]} to $CLUSTER from Animus"
else
	DIR_PREFIX=""
fi

###############################################################################

# Specify the username for the remote server
USERNAME="mschee"
if [ "$CLUSTER" = "trillium" ]; then
    # Specify the remote server address
    REMOTE_SERVER="trillium.alliancecan.ca"
    # Specify project directory
    PROJECT_DIR="/scratch/$USERNAME/Postdoc/unox"
elif [ "$CLUSTER" = "mist" ]; then
    # Specify the remote server address
    REMOTE_SERVER="mist.scinet.utoronto.ca"
    # Specify project directory
    PROJECT_DIR="/scratch/d/dylan/$USERNAME/Postdoc/unox"
else
    echo "Unknown cluster: $CLUSTER. Exiting."
    exit 1
fi
# Specify the identity file for SSH
IDENTITY_FILE="~/.ssh/id_ed25519"

# If copying a job, only copy the contents of `stage1_output` and 
# `stage2_output`. Also copy the `.txt` file with the same name
if [ "$INPUT_FILES" = i ]; then
    # Copy job directories from HPC to Animus
    for FILE in "${FILENAMES[@]}"; do
        FILES=""
        # Check whether the corresponding directory exists on Animus
        if [ ! -d ".$DIR_PREFIX/$FILE" ]; then
            echo "Directory .$DIR_PREFIX/$FILE does not exist on Animus, aborting."
            exit 1
        fi
        # Copy the entire input file directory
        FILES+=".$DIR_PREFIX/$FILE"
        # Copy the files over
        # echo $FILES
        scp -r -i $IDENTITY_FILE "$FILES" $USERNAME@$REMOTE_SERVER:$PROJECT_DIR$DIR_PREFIX/
    done
else
    # Copy files or directories from HPC to Animus
    FILES=""
    for FILE in "${FILENAMES[@]}"; do
        FILES+="$PROJECT_DIR$DIR_PREFIX/$FILE "
    done
    # echo $FILES
    scp -r -i $IDENTITY_FILE "$FILES" $USERNAME@$REMOTE_SERVER:$PROJECT_DIR$DIR_PREFIX/
fi