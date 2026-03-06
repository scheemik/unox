#!/bin/bash

# To be run on HPC.
# Submit this script to a HPC with `sbatch`. Note, by default the code will run 
# with updated versions of tensorflow and keras, which won't work on Mist. Use
# `-v 0` to run with the versions that are compatible with Mist.
# Takes in optional arguments:
#	$ sbatch HPC_slurm.sh -j <job name> 				Default: test_unet
#                         -i <config file>              Default: no2_sample_input
#						  -t <run type>					Default: test, other options: zfi_set
#                         -v <version>                  Default: 1, use updates
#                         -c <cluster>                  Default: trillium

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

echo "===== Begin HPC_slurm.sh ====="
# Source parameters from file
source HPC_params.sh
###############################################################################
# Check which arguments were passed
if [ -z "$JOBNAME" ]
then
	JOBNAME="test_unet"
	echo "-j, No name specified, using JOBNAME=$JOBNAME"
else
	echo "-j, Name specified, using JOBNAME=$JOBNAME"
fi
SAVEDIR="HPC_runs/${JOBNAME}" #_${SLURM_JOB_ID}"
if [ -z "$CONFIG_FILE" ]
then
	CONFIG_FILE='sample_config'
	echo "-i, No input files specified, using CONFIG_FILE=$CONFIG_FILE"
else
	echo "-i, Input files specified, using CONFIG_FILE=$CONFIG_FILE"
fi
if [ -z "$TYPE" ]
then
	TYPE="test"
	echo "-t, No run type specified, using TYPE=$TYPE"
	CODEFILE='src/unox/HPC/run_model.py'
	echo "    Using CODEFILE=$CODEFILE"
elif [ "$TYPE" = "test" ]
then
	echo "-t, Run type specified, using TYPE=$TYPE"
	CODEFILE='src/unox/HPC/run_model.py'
	echo "    Using CODEFILE=$CODEFILE"
elif [ "$TYPE" = "zfi_set" ]
then
	echo "-t, Run type specified, using TYPE=$TYPE"
	CODEFILE='src/unox/HPC/run_model.py'
	echo "    Using CODEFILE=$CODEFILE"
	SAVEDIR="HPC_runs/_${JOBNAME}"
else
	echo "Invalid run type specified. Select from: "
	echo "'test', 'zfi_set'."
	exit 1
fi
if [ -z "$VERSION" ]
then
	VERSION=1
	echo "-v, No version specified, using VERSION=$VERSION"
fi
if [ -z "$CLUSTER" ]
then
    CLUSTER="trillium"
    echo "-c, No cluster specified, defaulting to $CLUSTER"
else
    echo "-c, Using cluster: $CLUSTER"
fi

echo ""
# Load modules and activate virtual environment
if [ "$CLUSTER" = "trillium" ]
then
	echo "Loading modules for Trillium HPC environment"
	if [ "$VERSION" = 0 ]
	then
		echo "-v $VERSION, using original code"
		module load StdEnv/2020 gcc/9.3.0 python/3.8.10 cuda/11.4
		ENVNAME="unoxTrillium"
		ENVDIR="/home/$HPC_USERNAME/.virtualenvs/$ENVNAME"
	elif [ "$VERSION" = 1 ]
	then
		echo "-v $VERSION, using updated code"
		module load StdEnv/2023 gcc/12.3 python/3.12.4 cuda/12.6 hdf5/1.14.2 netcdf/4.9.2 mpi4py/4.0.0
		ENVNAME="unoxTrilliumNC"
		ENVDIR="/home/$HPC_USERNAME/.virtualenvs/$ENVNAME"
	else
		echo "Version $VERSION not recognized, exiting"
		exit 1
	fi
	echo "Activating virtualenv from $ENVDIR/bin/activate"
	source $ENVDIR/bin/activate
elif [ "$CLUSTER" = "mist" ]
then
	echo "Loading modules for Mist HPC environment"
	if [ "$VERSION" = 0 ]
	then
		echo "-v $VERSION, using original code"
		module load MistEnv/2021a anaconda3/2021.05 
		source activate unetmist
		module load cuda/11.4.4
	else
		echo "Version $VERSION not recognized, exiting"
		exit 1
	fi
else
	echo "Cluster $CLUSTER not recognized, exiting"
	exit 1
fi
echo ""

# Check whether a directory exists for the job
if [ ! -d "$SAVEDIR" ]
then
	echo "Creating directory for job $SAVEDIR"
	mkdir -p $SAVEDIR
else
	echo "Directory for job $SAVEDIR already exists"
fi

export HDF5_USE_FILE_LOCKING=FALSE

echo ""
echo "Running $CODEFILE with savedir $SAVEDIR"
echo ""
python $CODEFILE $SAVEDIR $CONFIG_FILE $VERSION

# Remove all but the most recent `checkpt` file
CHKPT_DIR="$SAVEDIR/checkpts"
VAR=$(keep_most_recent_checkpoint $CHKPT_DIR)
echo "$VAR"

deactivate