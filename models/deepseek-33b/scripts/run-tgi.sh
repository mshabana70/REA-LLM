#!/bin/bash


model="deepseek-ai/deepseek-coder-33b-instruct"
cache=/scratch/ms9761/rea-llm/data
volume=/scratch/ms9761/rea-llm/text-generation-inference_latest.sif
token_size=4096
token_memory=6000
HOST=0.0.0.0
PORT=22000
access_token=$HF_TOKEN
export HUGGING_FACE_HUB_TOKEN=$access_token

singularity exec --nv --env HUGGING_FACE_HUB_TOKEN=$access_token $volume text-generation-server download-weights $model
singularity exec --nv $volume text-generation-launcher --model-id $model --huggingface-hub-cache $cache --hostname $HOST --port $PORT --max-input-length $token_size --max-total-tokens $token_memory --disable-custom-kernels
