#!/bin/bash
# Author: Mikhail Schee
# 2025-03-27

# Run this script to submit a job to HPC. Note, by default the code will run 
# with updated versions of tensorflow and keras, which won't work on Mist. Use
# `-v 0` to run with the versions that are compatible with Mist.
# Takes in optional arguments:
#	$ bash HPC_job_submit.sh -j <job name> 			Default: current datetime
#							 -i <inputfiles>        Default: no2_sample_input
#							 -t <test run>			Default: True, run test_unet.sh
#                            -v <version>           Default: 1, use updates
#                            -c <cluster>           Default: trillium

# Current datetime
# DATETIME=`date +"%Y-%m-%d_%Hh%M"`

# Having a ":" after a flag means an option is required to invoke that flag
while getopts j:i:tv:c: option
do
	case "${option}"
		in
		j) JOBNAME=${OPTARG};;
		i) INPUTFILES=${OPTARG};;
		t) TEST=t;;
		v) VERSION=${OPTARG};;
		c) CLUSTER=${OPTARG};;
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
if [ -z "$INPUTFILES" ]
then
	INPUTFILES=1
	echo "-i, No input files specified, using INPUTFILES=$INPUTFILES"
else
	echo "-i, Input files specified, using INPUTFILES=$INPUTFILES"
fi
if [ "$TEST" = t ]
then
	LAUNCHER="test_unet.sh"
	echo "-t, Test run specified, using LAUNCHER=$LAUNCHER"
else
	echo "No LAUNCHER specified, exiting"
	exit 1
fi
if [ -z "$VERSION" ]
then
	VERSION=1
	echo "-v, No version specified, using VERSION=$VERSION"
else
	echo "-v, Version specified, using VERSION=$VERSION"
fi
if [ -z "$CLUSTER" ]
then
    CLUSTER="trillium"
    echo "-c, No cluster specified, defaulting to $CLUSTER"
else
    echo "-c, Using cluster: $CLUSTER"
fi

# Check to see whether a directory exists for the job
if [ ! -d "HPC_runs/$JOBNAME" ]
then
	echo "Creating directory for job $JOBNAME"
	mkdir HPC_runs/$JOBNAME
else
	echo "Directory for job HPC_runs/$JOBNAME already exists"
	echo "Would you like to overwrite it? (y/n)"
	read -r answer
	if [[ "$answer" == "y" || "$answer" == "Y" ]]
	then
		echo "Overwriting directory HPC_runs/$JOBNAME"
		rm -rf HPC_runs/$JOBNAME
		mkdir HPC_runs/$JOBNAME
	else
		echo "Exiting without overwriting directory"
		exit 1
	fi
fi

###############################################################################
# Submit job to queue
sbatch --job-name=$JOBNAME $LAUNCHER -j $JOBNAME -i $INPUTFILES -v $VERSION -c $CLUSTER