#!/bin/bash
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=3:00:00
#SBATCH --mail-user=mikhail.schee@mail.utoronto.ca
#SBATCH --mail-type=ALL
#SBATCH --output=HPC_runs/%x/log_%x_%j.txt				# %x = job_name, %j = job_number

# Submit this script to a HPC with `sbatch`. Note, by default the code will run 
# with updated versions of tensorflow and keras, which won't work on Mist. Use
# `-v 0` to run with the versions that are compatible with Mist.
# Takes in optional arguments:
#	$ sbatch test_unet.sh -j <job name> 				 Default: test_unet
#                         -i <inputfiles>                Default: no2_sample_input
#                         -v <version>                   Default: 1, use updates
#                         -c <cluster>                   Default: trillium

# Having a ":" after a flag means an option is required to invoke that flag
while getopts j:i:v:c: option
do
	case "${option}"
		in
		j) JOBNAME=${OPTARG};;
		i) INPUTFILES=${OPTARG};;
		v) VERSION=${OPTARG};;
		c) CLUSTER=${OPTARG};;
	esac
done

CODEFILE='test_unet.py'

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

# Load modules and activate virtual environment
if [ "$CLUSTER" = "trillium" ]
then
	echo "Loading modules for Trillium HPC environment"
	echo ""
	if [ "$VERSION" = 0 ]
	then
		echo "-v $VERSION, using original code"
		module load StdEnv/2020 gcc/9.3.0 python/3.8.10 cuda/11.4
		ENVDIR="/home/mschee/.virtualenvs/unoxTrillium"
	elif [ "$VERSION" = 1 ]
	then
		echo "-v $VERSION, using updated code"
		module load StdEnv/2023 gcc/12.3 python/3.12.4 cuda/12.6
		ENVDIR="/home/mschee/.virtualenvs/unoxTrilliumNew"
	else
		echo "Version $VERSION not recognized, exiting"
		exit 1
	fi
	echo ""
	echo "Activating virtualenv from $ENVDIR/bin/activate"
	source $ENVDIR/bin/activate
elif [ "$CLUSTER" = "mist" ]
then
	echo "Loading modules for Mist HPC environment"
	echo ""
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

# source /home/mschee/.virtualenvs/unoxTrillium/bin/activate
# source /home/mschee/.virtualenvs/unoxTrilliumNew/bin/activate

# Mist module environment
# module load MistEnv/2021a
# module load anaconda3/2021.05 
# source activate unetmist
# module load cuda/11.4.4 

# Ignore these
# module load anaconda3/2021.05 cuda/11.4.4 gcc/10.3.0 openblas/0.3.15 openmpi/4.1.1+ucx-1.10.0 hdf5/1.10.7

SAVEDIR="HPC_runs/${JOBNAME}" #_${SLURM_JOB_ID}"
# Check whether a directory exists for the job
if [ ! -d "$SAVEDIR" ]
then
	echo "Creating directory for job $JOBNAME"
	mkdir -p $SAVEDIR
else
	echo "Directory for job $SAVEDIR already exists"
fi

echo ""
echo "Running $CODEFILE with savedir $SAVEDIR"
echo ""
python $CODEFILE $SAVEDIR $INPUTFILES $VERSION