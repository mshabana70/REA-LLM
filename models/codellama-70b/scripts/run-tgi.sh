#!/bin/bash

##commands go here

model="meta-llama/CodeLlama-70b-Instruct-hf"
cache=/scratch/ms9761/rea-llm/data
volume=/scratch/ms9761/rea-llm/text-generation-inference_latest.sif
token_size=4000
token_memory=6000
HOST=0.0.0.0
PORT=8000
access_token=$TOKEN
export HUGGING_FACE_HUB_TOKEN=$access_token

#singularity exec --nv $volume text-generation-server download-weights $model
singularity exec --nv $volume text-generation-launcher --model-id $model --huggingface-hub-cache $cache --hostname $HOST --port $PORT --max-input-length $token_size --max-total-tokens $token_memory --disable-custom-kernels
