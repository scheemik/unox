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