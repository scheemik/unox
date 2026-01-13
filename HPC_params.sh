#!/bin/bash
# Author: Mikhail Schee
# 2026-01-12

# Edit this script so the parameters reference your own setup

# The email to use for sending HPC job notifications
# Read the `HPC_slurm.sh` script to find the email address
# line-by-line until you find `#SBATCH --mail-user`
SCRIPT="HPC_slurm.sh"
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

TRIL_SCRATCH="/scratch/$HPC_USERNAME"
TRIL_PROJ_DIR="Postdoc/unox"
TRIL_IDENTITY_FILE="~/.ssh/id_ed25519"

###############################################################################
# Mist parameters

MIST_SCRATCH="/scratch/d/dylan/$HPC_USERNAME"
MIST_PROJ_DIR="Postdoc/unox"
MIST_IDENTITY_FILE="~/.ssh/id_ed25519"