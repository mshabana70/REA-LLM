#!/bin/bash

##Hardware reqs go here

##SBATCH --nodes=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:rtx8000:2
#SBATCH --time=2:00:00
#SBATCH --mem=250GB
#SBATCH --job-name=mixtral-test
#SBATCH --mail-type=END
##SBATCH --mail-user=ms9761@nyu.edu
#SBATCH --output=slurm_%j.out

##commands go here

model="mistralai/Mixtral-8x7B-Instruct-v0.1"
cache=/scratch/ms9761/rea-llm/data
volume=/scratch/ms9761/rea-llm/vllm_latest.sif
token_size=4000
token_memory=6000
HOST=0.0.0.0
PORT=8000
TYPE=bfloat16

singularity exec --overlay /scratch/ms9761/rea-llm/llm-container.ext3:rw /scratch/work/public/singularity/cuda11.6.124-cudnn8.4.0.27-devel-ubuntu20.04.4.sif /bin/bash -c "source /ext3/env.sh; conda activate llama-env; python -u -m vllm.entrypoints.api_server --host $HOST --port $PORT --model $model --dtype $TYPE --download-dir $cache --tensor-parallel-size 2 --load-format safetensors"   
