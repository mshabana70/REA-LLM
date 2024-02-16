#!/bin/bash

##commands go here

model="mistralai/Mixtral-8x7B-Instruct-v0.1"
#model="mistralai/Mistral-7B-Instruct-v0.2"
cache=/scratch/ms9761/rea-llm/data
volume=/scratch/ms9761/rea-llm/vllm-openai_latest.sif
token_size=4000
token_memory=6000
HOST=0.0.0.0
PORT=8000
TYPE=float16


singularity exec --nv --bind /home/ms9761/tmp/ld.so.cache:/etc/ld.so.cache:ro --env LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/.singularity.d/libs:/usr/local/cuda-12.1/compat $volume /bin/bash -c "python3 -u -m vllm.entrypoints.api_server --host $HOST --port $PORT --model $model --dtype $TYPE --download-dir $cache --tensor-parallel-size 4 --load-format safetensors" 
