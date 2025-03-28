#!/bin/bash
# Author: Mikhail Schee
# 2025-03-27

# Run this script to submit a job to Mist. 
# Takes in optional arguments:
#	$ bash HPC_job_submit.sh -j <job name> 			Default: current datetime
#							 -t <test run>			Default: True, run test_unet.sh

# Current datetime
# DATETIME=`date +"%Y-%m-%d_%Hh%M"`

# Having a ":" after a flag means an option is required to invoke that flag
while getopts j:t option
do
	case "${option}"
		in
		j) JOBNAME=${OPTARG};;
		t) TEST=t;;
	esac
done

# check to see if arguments were passed
if [ -z "$JOBNAME" ]
then
	JOBNAME="test_unet"
	echo "-j, No name specified, using JOBNAME=$JOBNAME"
else
	echo "-j, Name specified, using JOBNAME=$JOBNAME"
fi
if [ "$TEST" = t ]
then
	LAUNCHER="test_unet.sh"
	echo "-t, Test run specified, using LAUNCHER=$LAUNCHER"
else
	echo "No LAUNCHER specified, exiting"
	exit 1
fi

###############################################################################
# Submit job to queue
# sbatch --job-name=$JOBNAME $LAUNCHER -j $JOBNAME