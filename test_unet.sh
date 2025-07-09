#!/bin/bash
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=3:00:00
#SBATCH --mail-user=mikhail.schee@mail.utoronto.ca
#SBATCH --mail-type=ALL
#SBATCH --output=HPC_runs/%x/log_%x_%j.txt				# %x = job_name, %j = job_number

# Submit this script to a HPC with `sbatch`
# Takes in optional arguments:
#	$ sbatch test_unet.sh -j <job name> 				 Default: test_unet

# Having a ":" after a flag means an option is required to invoke that flag
while getopts j: option
do
	case "${option}"
		in
		j) JOBNAME=${OPTARG};;
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

module load MistEnv/2021a
module load anaconda3/2021.05 
source activate unetmist
module load cuda/11.4.4 
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
 
python test_unet.py $SAVEDIR