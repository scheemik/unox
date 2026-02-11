#!/bin/bash
# Author: Mikhail Schee
# 2026-01-12

# Edit this script so the parameters reference your own setup

# The email to use for sending HPC job notifications
# Read the `HPC_slurm.sh` script to find the email address
# Go line-by-line until you find `#SBATCH --mail-user`
SCRIPT="HPC_GPU_slurm.sh"
while read -r line; do
    if [[ $line == \#SBATCH\ --mail-user=* ]]; then
        HPC_EMAIL="${line#*=}"
        break
    fi
done < "$SCRIPT"

# The username on the HPC cluster
HPC_USERNAME="mschee"

###############################################################################
# Trillium parameters

# The variables TRIL_SCRATCH and TRIL_PROJ_DIR should combine to form the full
# path to the `unox` directory in your Trillium scratch space.
TRIL_SCRATCH="/scratch/$HPC_USERNAME"
TRIL_PROJ_DIR="Postdoc/unox"
# This is the name of the identify file for SSH connections to Trillium
# NOTE: This file is located on Animus
TRIL_IDENTITY_FILE="~/.ssh/id_ed25519"

###############################################################################
# Mist parameters

# The variables MIST_SCRATCH and MIST_PROJ_DIR should combine to form the full
# path to the `unox` directory in your Mist scratch space.
MIST_SCRATCH="/scratch/d/dylan/$HPC_USERNAME"
MIST_PROJ_DIR="Postdoc/unox"
# This is the name of the identify file for SSH connections to Mist
# NOTE: This file is located on Animus
MIST_IDENTITY_FILE="~/.ssh/id_ed25519"

###############################################################################
# Function to find the modify dates of `checkpt` files and 
# only keep the most recent one
keep_most_recent_checkpoint() {
    # Expects file path like "HPC_runs/_test_ens_zfi2/test_ens_zfi2_skt/01_test_ens_zfi2_skt/checkpts"
    local dir=$1
    # Check whether a config file exists
    if [ ! -d $dir ]; then
        echo "$dir is not a directory"
    else
        # Set a variable to record the most recent time
        MOST_RECENT_TIME=0
        # Set a variable to record the most recent file
        MOST_RECENT_FILE="None"
        # Loop through all the files in this directory
        for FILE in "$dir"/*; do
            # Check whether it is a checkpoint file
            if [[ "$FILE" == *"checkpt"* ]]; then
                # Get the modification date in seconds since epoch
                THIS_TIME=$(stat --format="%Y" $FILE)
                # Check whether this is more recent than the last file
                if [[ $THIS_TIME > $MOST_RECENT_TIME ]]; then
                    # Set the new values
                    MOST_RECENT_TIME=$THIS_TIME
                    MOST_RECENT_FILE=$FILE
                fi
            fi
        done
        # Loop through all the files in this directory again
        for FILE in "$dir"/*; do
            # Check whether it is the most recent file
            if [[ "$FILE" != "$MOST_RECENT_FILE" ]]; then
                # Remove that file, if not the most recent
                rm $FILE
            fi
        done
        echo $MOST_RECENT_FILE
    fi
}