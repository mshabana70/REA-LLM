#!/bin/bash

##Hardware reqs go here

##SBATCH --nodes=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
##SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:rtx8000:2
#SBATCH --time=2:00:00
#SBATCH --mem=250GB
#SBATCH --job-name=galactica-test
#SBATCH --mail-type=END
##SBATCH --mail-user=ms9761@nyu.edu
#SBATCH --output=slurm_%j.out

##commands go here

model="GeorgiaTechResearchInstitute/galactica-6.7b-evol-instruct-70k"
cache=/scratch/ms9761/rea-llm/data
volume=/scratch/ms9761/rea-llm/text-generation-inference_latest.sif
token_size=2048
token_memory=3000
#prefill_token=2048 # default 4096, must be <= max-batch-total-tokens
#batch_token=2048
HOST=0.0.0.0
PORT=8000
data_type=bfloat16

export CUDA_LAUNCH_BLOCK=1
export TORCH_USE_CUDA_DSA=1
singularity exec --nv $volume env
singularity exec --nv $volume text-generation-launcher --model-id $model --huggingface-hub-cache $cache --hostname $HOST --port $PORT --dtype $data_type --max-input-length $token_size --max-total-tokens $token_memory --disable-custom-kernels
