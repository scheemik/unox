#!/bin/bash
# Author: Mikhail Schee
# 2026-01-12

# Edit this script so the parameters reference your own setup

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