#!/bin/bash

module purge;

current_time=$(date "+%Y.%m.%d-%H.%M.%S")
filename=log-${current_time}.txt;


echo "HELLO FROM PYTHON"
singularity exec --nv \
        --overlay /scratch/ms9761/rea-llm/llm-container.ext3:ro \
        /scratch/work/public/singularity/cuda11.6.124-cudnn8.4.0.27-devel-ubuntu20.04.4.sif\
        /bin/bash -c "source /ext3/env.sh; conda activate llama-env; python /scratch/ms9761/rea-llm/mixtral/src/recurse.py > /scratch/ms9761/rea-llm/mixtral/logs/${filename}"





