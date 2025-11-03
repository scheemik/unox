#!/bin/bash
# Author: Mikhail Schee
# 2025-03-27

# Run this script to submit a job to HPC. Note, by default the code will run 
# with updated versions of tensorflow and keras, which won't work on Mist. Use
# `-v 0` to run with the versions that are compatible with Mist.
# Takes in optional arguments:
#	$ bash HPC_job_submit.sh -j <job name> 			Default: test_unet
#							 -i <config file>       Default: sample_config
#							 -t <run type>			Default: test, other options: zfi_set
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

echo "===== Begin HPC_job_submit.sh ====="
###############################################################################
# Check which arguments were passed
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
# Check to see whether the configuration file exists
if [ ! -f "inputfiles/_input_configs/$CONFIG_FILE.json" ]
then
	echo "    Configuration file inputfiles/_input_configs/$CONFIG_FILE.json does not exist."
	echo "    Exiting..."
	exit 1
else
	echo "    Configuration file inputfiles/_input_configs/$CONFIG_FILE.json found."
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
elif [ "$TYPE" = "zfi_set" ]
then
	echo "-t, Run type specified, using TYPE=$TYPE"
	LAUNCHER='HPC_GPU_slurm.sh'
else
	echo "Invalid run type specified. Select from: "
	echo "'test', 'zfi_set'."
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

###############################################################################
# Check to see whether a directory exists for the job
if [ ! -d "HPC_runs/$JOBNAME" ]
then
	if [ "$TYPE" = "zfi_set" ]; then
		python src/unox/HPC_scripts/set_of_runs.py $JOBNAME $CONFIG_FILE $TYPE
		# Check for a "set" directory, which prepends an underscore
		if [ ! -d "HPC_runs/_$JOBNAME" ]; then
			echo "Directory for job HPC_runs/_$JOBNAME does not exist."
			echo "For set of runs jobs, please ensure that the run directory (HPC_runs/_$JOBNAME) is correctly created by `set_of_runs.py`."
			echo "Exiting..."
			exit 1
		fi
	else
		echo "Creating directory for job $JOBNAME"
	mkdir HPC_runs/$JOBNAME
	fi
else
	if [ "$TYPE" = "zfi_set" ]; then
		echo "Directory for job HPC_runs/$JOBNAME already exists."
		echo "Choose a different name to avoid confusion."
		echo "Exiting..."
		exit 1
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

# Make sure the configuration files are copied to the job directory
if [ "$TYPE" = "test" ]; then
	if [ ! -f "HPC_runs/$JOBNAME/input_config.json" ]; then
		cp inputfiles/_input_configs/$CONFIG_FILE.json HPC_runs/$JOBNAME/input_config.json
	fi
elif [ "$TYPE" = "zfi_set" ]; then
	# Loop across the subdirectories in the set directory
	for SUBDIR in HPC_runs/_$JOBNAME/*/; do
		# Copy the configuration file to each sub directory in the set
		if [ ! -f "$SUBDIR/input_config.json" ]; then
			echo "No configuration file found in $SUBDIR."
			echo "For set of runs jobs, please ensure that `set_of_runs.py` gives each sub directory in HPC_runs/_$JOBNAME an input_config.json file."
			echo "Exiting..."
			exit 1
		fi
	done
fi

###############################################################################
# Submit job to queue
if [ "$TYPE" = "test" ]; then
	sbatch --job-name=$JOBNAME $LAUNCHER -j $JOBNAME -i $CONFIG_FILE -t $TYPE -v $VERSION -c $CLUSTER
elif [ "$TYPE" = "zfi_set" ]; then
	# Loop across the subdirectories in the set directory
	for SUBDIR in HPC_runs/_$JOBNAME/*/; do
		# If it is a directory, continue
		if [ -d "$SUBDIR" ]; then
			# Get just the subdirectory name
			SUBDIR_NAME=$(basename "$SUBDIR")
			# Submit a job for each sub directory in the set
			sbatch --job-name=$JOBNAME $LAUNCHER -j $JOBNAME/$SUBDIR_NAME -i $CONFIG_FILE -t $TYPE -v $VERSION -c $CLUSTER
		fi
	done
fi