#!/bin/bash
# Author: Mikhail Schee
# 2025-06-02

# To be run on Animus.
# Run this script to copy a file or directory from an HPC cluster to Animus.
# Takes in the following arguments:
#	$ bash HPC_to_animus.sh -f <filename>      Ex: test_unet_601760
#                           -j <HPC_job>       Whether to look for HPC job based on filename (default: False)
#                           -c <cluster>       HPC cluster to transfer from (default: trillium)
#                           -m <model>         Whether to copy model files (default: False)
#
# Note: Each file in list must be preceded by the -f flag. Ex:
#	$ bash HPC_to_animus.sh -f test_file1 -f test_file2

# Having a ":" after a flag means an option is required to invoke that flag
while getopts "f:jc:m" option;
do
	case $option
		in
		f) FILENAMES+=("$OPTARG");;
        j) HPC_JOB=j;;
        c) CLUSTER=${OPTARG};;
        m) MODEL=m;;
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
if [ "$HPC_JOB" = j ]
then
	DIR_PREFIX="/HPC_runs"
	echo "-j, Copying full HPC job directory for ${FILENAMES[*]} from $CLUSTER to Animus"
else
	DIR_PREFIX=""
fi
if [ "$MODEL" = m ]
then
	EXCLUDES="--exclude='*checkpts/*'"
	echo "-m, Copying model files for ${FILENAMES[*]} from $CLUSTER to Animus"
else
	EXCLUDES="--exclude='*checkpts/*' --exclude='*.h5' --exclude='*.keras'"
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

# If copying a job, copy the contents of the directory, with the specified exclusions
if [ "$HPC_JOB" = j ]; then
    # Copy job directories from HPC to Animus
    for FILE in "${FILENAMES[@]}"; do
        FILES=""
        # Check whether the corresponding directory exists on Animus
        if [ ! -d ".$DIR_PREFIX/$FILE" ]; then
            echo "Directory .$DIR_PREFIX/$FILE does not exist, creating it."
            mkdir -p .$DIR_PREFIX/$FILE
        fi
        # Copy the directory to local, excluding the specified patterns
        # in $EXCLUDES. Use tar over ssh to preserve directory structure
        # while allowing excludes
        ssh -i $IDENTITY_FILE $HPC_USERNAME@$REMOTE_SERVER "cd $PROJECT_DIR$DIR_PREFIX/$FILE && tar cf - $EXCLUDES ." | tar xf - -C .$DIR_PREFIX/$FILE
    done
else
    # Copy files or directories from HPC to Animus
    FILES=""
    for FILE in "${FILENAMES[@]}"; do
        FILES+="$PROJECT_DIR$DIR_PREFIX/$FILE "
    done
    echo $FILES
    scp -r -i $IDENTITY_FILE $HPC_USERNAME@$REMOTE_SERVER:"$FILES" .$DIR_PREFIX
fi

# Define function to combine predictions
check_to_combine_predictions() {
    local file=$1
    # Check whether a config file exists
    if [ -f ".$DIR_PREFIX/$file/input_config.json" ]; then
        THIS_CONFIG=".$DIR_PREFIX/$file/input_config.json"
        echo "Found $THIS_CONFIG"
    else
        THIS_CONFIG=""
        echo "Did not find .$DIR_PREFIX/$file/input_config.json, using sample_config.json"
    fi
    echo "Looking for .$DIR_PREFIX/$file/ENSEMBLE_SIZE.txt"
    if [ -f ".$DIR_PREFIX/$file/ENSEMBLE_SIZE.txt" ]; then
        echo "Found .$DIR_PREFIX/$file/ENSEMBLE_SIZE.txt"
        echo "    Combining predictions from ensemble run for $file"
        python src/unox/HPC/combine_predictions.py $file $THIS_CONFIG
    fi
}

# Check whether to combine predictions of an ensemble run
if [ "$HPC_JOB" = j ]; then
    # Copy job directories from HPC to Animus
    for FILE in "${FILENAMES[@]}"; do
        # Check whether there is a file called `ENSEMBLE_SIZE.txt` in the copied directory
        echo "Checking .$DIR_PREFIX/$FILE for ensemble predictions to combine..."
        check_to_combine_predictions $FILE
        # Check whether there is a file called `ENSEMBLE_SIZE.txt` in the each subdirectory
        for SUBDIR in .$DIR_PREFIX/$FILE/*/; do
            if [ -d "$SUBDIR" ]; then
                SUBDIR_NAME=$(basename "$SUBDIR")
                if [ "$SUBDIR_NAME" != "checkpts" ]; then
                    echo "Checking .$DIR_PREFIX/$FILE/$SUBDIR_NAME for ensemble predictions to combine..."
                    check_to_combine_predictions "$FILE/$SUBDIR_NAME"
                fi
            fi
        done
    done
fi

echo "Completed file transfer to Animus"