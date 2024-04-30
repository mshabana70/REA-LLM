#!/bin/bash

##commands go here

model="mistralai/Mixtral-8x22B-Instruct-v0.1"
cache=/scratch/ms9761/rea-llm/data
volume=/scratch/ms9761/rea-llm/vllm-openai_latest.sif
token_size=4000
token_memory=6000
num_of_gpu=4
HOST=127.0.0.1
PORT=50000
access_token=$TOKEN
TYPE=half ## half => RTX8000, bfloat16 = A100

singularity \
    run --nv \
    --env HUGGING_FACE_HUB_TOKEN=$access_token \
    --bind /home/ms9761/tmp/ld.so.cache:/etc/ld.so.cache:ro \
    /scratch/ms9761/rea-llm/vllm-openai_latest.sif \
    --host $HOST --port $PORT --model $model --dtype $TYPE --download-dir $cache --tensor-parallel-size $num_of_gpu --load-format safetensors --trust-remote-code

exit
 
