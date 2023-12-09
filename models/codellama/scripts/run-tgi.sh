#!/bin/bash

##Hardware reqs go here

##SBATCH --nodes=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
##SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:rtx8000:1
#SBATCH --time=2:00:00
#SBATCH --mem=150GB
#SBATCH --job-name=codellama-test
#SBATCH --mail-type=END
##SBATCH --mail-user=ms9761@nyu.edu
#SBATCH --output=slurm_%j.out

##commands go here

model="codellama/CodeLlama-7b-Instruct-hf"
cache=/scratch/ms9761/rea-llm/data
volume=/scratch/ms9761/rea-llm/text-generation-inference_latest.sif
token_size=4000
token_memory=6000
HOST=0.0.0.0
PORT=8000

singularity exec --nv $volume text-generation-server download-weights codellama/CodeLlama-7b-Instruct-hf
singularity exec --nv $volume text-generation-launcher --model-id $model --huggingface-hub-cache $cache --hostname $HOST --port $PORT --max-input-length $token_size --max-total-tokens $token_memory --disable-custom-kernels
