#!/bin/bash
# Author: Mikhail Schee
# 2025-06-02

# Run this script to copy a file or directory from Mist to Animus.
# Takes in the following arguments:
#	$ bash HPC_mist_to_animus.sh -f <filename>      Ex: test_unet_601760
#                                -j <HPC_job>       Look for HPC job based on filename
#
# Note: Each file in list must be preceded by the -f flag. Ex:
#	$ bash HPC_mist_to_animus.sh -f test_file1 -f test_file2

# Having a ":" after a flag means an option is required to invoke that flag
while getopts "f:j" option;
do
	case $option
		in
		f) FILENAMES+=("$OPTARG");;
        j) HPC_JOB=j
	esac
done
shift $((OPTIND -1))

# check to see if arguments were passed
if [ -z "$FILENAMES" ]
then
	echo "-f, No files specified, exiting"
	exit 1
fi
if [ "$HPC_JOB" = j ]
then
	DIR_PREFIX="/HPC_runs"
    EXCLUDE_FLAG="!(.h5)"
	echo "-j, Copying full HPC job directory for ${FILENAMES[*]} from Mist to Animus"
else
	DIR_PREFIX=""
    EXCLUDE_FLAG=""
fi

###############################################################################

# Specify the remote server address
REMOTE_SERVER="mist.scinet.utoronto.ca"
# Specify the username for the remote server
USERNAME="mschee"
# Specify project directory
PROJECT_DIR="/scratch/d/dylan/$USERNAME/Postdoc/unox"
# Specify the identity file for SSH
IDENTITY_FILE="~/.ssh/id_ed25519"

# If copying a job, only copy the contents of `stage1_output` and 
# `stage2_output`. Also copy the `.txt` file with the same name
if [ "$HPC_JOB" = j ]; then
    # Copy job directories from Mist to Animus
    for FILE in "${FILENAMES[@]}"; do
        FILES=""
        # Check whether the corresponding directory exists on Animus
        if [ ! -d ".$DIR_PREFIX/$FILE" ]; then
            echo "Directory .$DIR_PREFIX/$FILE does not exist, creating it."
            mkdir -p .$DIR_PREFIX/$FILE
        fi
        # Copy just the log (.txt) file and the files in `stage1_output` and `stage2_output`
        FILES+="$PROJECT_DIR$DIR_PREFIX/$FILE/*.txt "
        FILES+="$PROJECT_DIR$DIR_PREFIX/$FILE/stage1_output/ "
        FILES+="$PROJECT_DIR$DIR_PREFIX/$FILE/stage2_output/ "
        # Copy the files over
        scp -r -i $IDENTITY_FILE $USERNAME@$REMOTE_SERVER:"$FILES" .$DIR_PREFIX/$FILE
    done
else
    # Copy files or directories from Mist to Animus
    FILES=""
    for FILE in "${FILENAMES[@]}"; do
        FILES+="$PROJECT_DIR$DIR_PREFIX/$FILE "
    done
    echo $FILES
    scp -r -i $IDENTITY_FILE $USERNAME@$REMOTE_SERVER:"$FILES" .$DIR_PREFIX
fi