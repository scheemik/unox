#!/bin/bash
# Author: Mikhail Schee
# 2025-03-27

# Run this script to submit a job to HPC. Note, by default the code will run 
# with updated versions of tensorflow and keras, which won't work on Mist. Use
# `-v 0` to run with the versions that are compatible with Mist.
# Takes in optional arguments:
#	$ bash HPC_job_submit.sh -j <job name> 			Default: test_unet
#							 -i <config file>       Default: sample_config
#							 -t <run type>			Default: test, other options: pred
#                            -v <version>           Default: 1, use updates
#                            -c <cluster>           Default: trillium

# Current datetime
# DATETIME=`date +"%Y-%m-%d_%Hh%M"`

# Having a ":" after a flag means an option is required to invoke that flag
while getopts j:i:t:v:c: option
do
	case "${option}"
		in
		j) JOBNAME=${OPTARG};;
		i) CONFIG_FILE=${OPTARG};;
		t) TYPE=${OPTARG};;
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
if [ -z "$CONFIG_FILE" ]
then
	CONFIG_FILE='sample_config'
	echo "-i, No config file specified, using CONFIG_FILE=$CONFIG_FILE"
else
	echo "-i, Config files specified, using CONFIG_FILE=$CONFIG_FILE"
fi
if [ -z "$TYPE" ]
then
	TYPE="test"
	echo "-t, No run type specified, using TYPE=$TYPE"
	LAUNCHER='HPC_GPU_slurm.sh'
elif [ "$TYPE" = "test" ] 
then
	echo "-t, Run type specified, using TYPE=$TYPE"
	LAUNCHER='HPC_GPU_slurm.sh'
elif [ "$TYPE" = "pred" ]
then
	echo "-t, Run type specified, using TYPE=$TYPE"
	LAUNCHER='HPC_CPU_slurm.sh'
else
	echo "Invalid run type specified. Use 'test' or 'pred'."
	exit 1
fi
echo "    Using LAUNCHER=$LAUNCHER"
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

# Check to see whether the configuration file exists
if [ ! -f "inputfiles/_input_configs/$CONFIG_FILE.json" ]
then
	echo "Configuration file inputfiles/_input_configs/$CONFIG_FILE.json does not exist."
	echo "Exiting..."
	exit 1
else
	echo "Configuration file inputfiles/_input_configs/$CONFIG_FILE.json found."
fi
# Check to see whether a directory exists for the job
if [ ! -d "HPC_runs/$JOBNAME" ]
then
	if [ "$TYPE" = "pred" ]; then
		echo "For prediction jobs, please ensure that the run directory (HPC_runs/$JOBNAME) already exist."
		echo "Exiting..."
		exit 1
	fi
	echo "Creating directory for job $JOBNAME"
	mkdir HPC_runs/$JOBNAME
else
	if [ "$TYPE" = "pred" ]; then
		echo "Directory for job HPC_runs/$JOBNAME exists"
		echo "Proceeding..."
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
fi

###############################################################################
# Submit job to queue
sbatch --job-name=$JOBNAME $LAUNCHER -j $JOBNAME -i $CONFIG_FILE -t $TYPE -v $VERSION -c $CLUSTER