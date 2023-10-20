#!/bin/bash

##Hardware reqs go here

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:rtx8000:2
#SBATCH --time=1:00:00
#SBATCH --mem=256GB
#SBATCH --job-name=starcoder-test
#SBATCH --mail-type=END
##SBATCH --mail-user=ms9761@nyu.edu
#SBATCH --output=slurm_%j.out

##commands go here

module purge;

current_time=$(date "+%Y.%m.%d-%H.%M.%S")
filename=log-${current_time}.txt;

singularity exec --nv \
        --overlay /scratch/ms9761/rea-llm/llm-container.ext3:ro \
        /scratch/work/public/singularity/cuda11.6.124-cudnn8.4.0.27-devel-ubuntu20.04.4.sif\
        /bin/bash -c "source /ext3/env.sh; conda activate starcoder-env; python tgi-test.py > /scratch/ms9761/rea-llm/starcoder/logs/${filename}"


