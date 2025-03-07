#!/bin/bash
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=3:00:00
#SBATCH --job-name test_unet

module load MistEnv/2021a
module load anaconda3/2021.05 
source activate unetmist
module load cuda/11.4.4 

savedir="test_unet_${SLURM_JOB_ID}"
mkdir $savedir
 
python test_unet.py $savedir
