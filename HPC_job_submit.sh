#!/bin/bash
# Author: Mikhail Schee
# 2025-03-27

# To be run on HPC.
# Run this script to submit a job to HPC. Note, by default the code will run 
# with updated versions of tensorflow and keras, which won't work on Mist. Use
# `-v 0` to run with the versions that are compatible with Mist.
# Takes in optional arguments:
#	$ bash HPC_job_submit.sh -j <job name> 			Default: test_unet
#							 -e <ensemble size>  	Default: 1
#							 -i <config file>       Default: sample_config
#							 -t <run type>			Default: test, other options: zfi_set
#                            -v <version>           Default: 1, use updates
#                            -c <cluster>           Default: trillium

# Current datetime
# DATETIME=`date +"%Y-%m-%d_%Hh%M"`

# Having a ":" after a flag means an option is required to invoke that flag
while getopts j:e:i:t:v:c: option
do
	case "${option}"
		in
		j) JOBNAME=${OPTARG};;
		e) ENSEMBLE_SIZE=${OPTARG};;
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
if [ -z "$ENSEMBLE_SIZE" ]
then
	ENSEMBLE_SIZE=1
	echo "-e, No ensemble size specified, using ENSEMBLE_SIZE=$ENSEMBLE_SIZE"
else
	echo "-e, Ensemble size specified, using ENSEMBLE_SIZE=$ENSEMBLE_SIZE"
    REG_EX='^[0-9]+$'
    # Make sure the ensemble size is a positive integer less than 100
    if [[ "$ENSEMBLE_SIZE" =~ $REG_EX ]] && (( $ENSEMBLE_SIZE > 0 && $ENSEMBLE_SIZE < 100 ))
    then
        echo "    Ensemble size is a valid integer from 1 to 99."
    else
        echo "    Ensemble size must be an integer from 1 to 99."
        echo "    Exiting..."
        exit 1
    fi
fi
# Format a new variable to pad ensemble size with zeros
ENS_SIZE=$(printf "%02d" $ENSEMBLE_SIZE)
if [ -z "$CONFIG_FILE" ]
then
	CONFIG_FILE='sample_config'
	echo "-i, No config file specified, using CONFIG_FILE=$CONFIG_FILE"
else
	echo "-i, Config files specified, using CONFIG_FILE=$CONFIG_FILE"
fi
# Check to see whether the configuration file exists
if [ ! -f "model_configs/$CONFIG_FILE.json" ]
then
	echo "    Configuration file model_configs/$CONFIG_FILE.json does not exist."
	echo "    Exiting..."
	exit 1
else
	echo "    Configuration file model_configs/$CONFIG_FILE.json found."
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
if [ -d "HPC_runs/$JOBNAME" ]
then
	if [ "$TYPE" = "zfi_set" ]
	then
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
			echo "Deleting directory HPC_runs/$JOBNAME"
			rm -rf HPC_runs/$JOBNAME
		else
			echo "Exiting without overwriting directory"
			exit 1
		fi
	fi
fi

###############################################################################
# Create and set up the directory for the job
if [ "$TYPE" = "zfi_set" ]; then
	# Run the following Python script to create the directory structure for the set of runs
	python src/unox/HPC/set_of_runs.py $JOBNAME $CONFIG_FILE $TYPE
	# Check for a "set" directory, which prepends an underscore
	if [ ! -d "HPC_runs/_$JOBNAME" ]; then
		echo "Directory for job HPC_runs/_$JOBNAME does not exist."
		echo "For set of runs jobs, please ensure that the run directory (HPC_runs/_$JOBNAME) is correctly created by `set_of_runs.py`."
		echo "Exiting..."
		exit 1
	fi
	# Create a file called SET_OF_RUNS.txt for reference
	SET_OF_RUNS_FILE="HPC_runs/_${JOBNAME}/SET_OF_RUNS.txt"
	touch $SET_OF_RUNS_FILE
	echo "True" > $SET_OF_RUNS_FILE
	# Loop across the subdirectories in the set directory
	for SUBDIR in HPC_runs/_$JOBNAME/*/; do
		# Check whether there is more than one ensemble member
		if [ "$ENSEMBLE_SIZE" == 1 ]; then
			# Make sure that `set_of_runs.py` copied the config file correctly
			CONFIG_FILE="${SUBDIR}input_config.json"
			if [ ! -f "$CONFIG_FILE" ]; then
				echo "No configuration file found in $SUBDIR."
				echo "For set of runs jobs, please ensure that `set_of_runs.py` gives each sub directory in HPC_runs/_$JOBNAME an input_config.json file."
				echo "Exiting..."
				exit 1
			fi
		else
			# Get just the subdirectory name
			SUBDIR_NAME=$(basename "$SUBDIR")
			echo "    Creating subdirectories /01_${SUBDIR_NAME} -- /${ENS_SIZE}_${SUBDIR_NAME}"
			for (( i=1; i<=$ENSEMBLE_SIZE; i++ ))
			do
				# Get the ensemble member number with leading zeros
				ENS_NUM=$(printf "%02d" $i)
				# Format the name of the ensemble member subdirectory
				ENS_DIR="HPC_runs/_${JOBNAME}/${SUBDIR_NAME}/${ENS_NUM}_${SUBDIR_NAME}"
				# Make the ensemble member subdirectory
				mkdir $ENS_DIR
				# Copy the configuration file ensemble member's directory
				cp "$SUBDIR/input_config.json" $ENS_DIR/input_config.json
			# Create a file called ENSEMBLE_SIZE.txt that contains the ensemble size for reference
			echo "$ENSEMBLE_SIZE" > "HPC_runs/_${JOBNAME}/${SUBDIR_NAME}/ENSEMBLE_SIZE.txt"
			done
		fi
	done
else
	echo "Creating directory for job $JOBNAME"
	mkdir HPC_runs/$JOBNAME
	# Check whether there is more than one ensemble member
	if [ "$ENSEMBLE_SIZE" -gt 1 ]; then
		echo "    Creating subdirectories /01_${JOBNAME} -- /${ENS_SIZE}_${JOBNAME}"
		for (( i=1; i<=$ENSEMBLE_SIZE; i++ ))
		do
			# Get the ensemble member number with leading zeros
			ENS_NUM=$(printf "%02d" $i)
			# Format the name of the ensemble member subdirectory
			ENS_DIR="HPC_runs/${JOBNAME}/${ENS_NUM}_${JOBNAME}"
			# Make the ensemble member subdirectory
			mkdir $ENS_DIR
			# Make sure the configuration files are copied to the job directory
			if [ ! -f "${ENS_DIR}/input_config.json" ]; then
				cp model_configs/$CONFIG_FILE.json $ENS_DIR/model_config.json
			fi
		done
		# Create a file called ENSEMBLE_SIZE.txt that contains the ensemble size for reference
		ENS_SIZE_FILE="HPC_runs/${JOBNAME}/ENSEMBLE_SIZE.txt"
		touch $ENS_SIZE_FILE
		echo "$ENSEMBLE_SIZE" > $ENS_SIZE_FILE
	else
		# Make sure the configuration files are copied to the job directory
		if [ ! -f "HPC_runs/$JOBNAME/input_config.json" ]; then
			cp model_configs/$CONFIG_FILE.json HPC_runs/$JOBNAME/model_config.json
		fi
	fi
fi

###############################################################################
# Check the email to use for notifications
source HPC_params.sh
if [ -z "$HPC_EMAIL" ]
then
	echo "No email specified for HPC notifications."
	echo "Please add your email to the \`HPC_GPU_slurm.sh\` script at the line with \`#SBATCH --mail-user=\`."
	echo "Exiting..."
	exit 1
else
	echo "Sending HPC notifications to email: $HPC_EMAIL"
fi

###############################################################################
# Submit job to queue
if [ "$TYPE" = "test" ]; then
	# Check whether there is more than one ensemble member
	if [ "$ENSEMBLE_SIZE" == 1 ]; then
		sbatch --job-name=$JOBNAME $LAUNCHER -j $JOBNAME -t $TYPE -v $VERSION -c $CLUSTER
	else
		for (( i=1; i<=$ENSEMBLE_SIZE; i++ ))
		do
			# Get the ensemble member number with leading zeros
			ENS_NUM=$(printf "%02d" $i)
			# Format the name of the ensemble member subdirectory
			ENS_DIR="${ENS_NUM}_${JOBNAME}"
			sbatch --job-name=$JOBNAME/$ENS_DIR $LAUNCHER -j $JOBNAME/$ENS_DIR -t $TYPE -v $VERSION -c $CLUSTER
		done
	fi
elif [ "$TYPE" = "zfi_set" ]; then
	# Loop across the subdirectories in the set directory
	for SUBDIR in HPC_runs/_$JOBNAME/*/; do
		# If it is a directory, continue
		if [ -d "$SUBDIR" ]; then
			# Check whether there is more than one ensemble member
			if [ "$ENSEMBLE_SIZE" == 1 ]; then
				# Get just the subdirectory name
				SUBDIR_NAME=$(basename "$SUBDIR")
				# Submit a job for each sub directory in the set
				sbatch --job-name=_$JOBNAME/$SUBDIR_NAME $LAUNCHER -j $JOBNAME/$SUBDIR_NAME -t $TYPE -v $VERSION -c $CLUSTER
			else
				# Get just the subdirectory name
				SUBDIR_NAME=$(basename "$SUBDIR")
				# Loop across ensemble members
				for (( i=1; i<=$ENSEMBLE_SIZE; i++ ))
				do
					# Get the ensemble member number with leading zeros
					ENS_NUM=$(printf "%02d" $i)
					# Format the name of the ensemble member subdirectory
					ENS_DIR="${ENS_NUM}_${SUBDIR_NAME}"
					# Submit a job for each ensemble member sub directory in the set
					sbatch --job-name=_$JOBNAME/$SUBDIR_NAME/$ENS_DIR $LAUNCHER -j $JOBNAME/$SUBDIR_NAME/$ENS_DIR -t $TYPE -v $VERSION -c $CLUSTER
				done
			fi
		fi
	done
fi