#!/bin/bash
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=0:30:00
#SBATCH --mail-user=mikhail.schee@mail.utoronto.ca
#SBATCH --mail-type=ALL
#SBATCH --output=HPC_runs/%x/log_%j.txt				# %x = job_name, %j = job_number

# To be run on HPC.
# Submit this script to a HPC with `sbatch`. Note, by default the code will run 
# with updated versions of tensorflow and keras, which won't work on Mist. Use
# `-v 0` to run with the versions that are compatible with Mist.
# Takes in optional arguments:
#  $ sbatch HPC_GPU_slurm.sh -j <job name> 			Default: test_unet
#							 -i <config file>       Default: test_config
#							 -t <run type>			Default: test, other options: zfi_set
#                            -v <version>           Default: 1, use updates
#                            -c <cluster>           Default: trillium

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

bash HPC_slurm.sh -j $JOBNAME -i $CONFIG_FILE -t $TYPE -v $VERSION -c $CLUSTER