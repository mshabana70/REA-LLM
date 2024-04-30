#!/bin/bash

#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:rtx8000:3
#SBATCH --time=10:00:00
#SBATCH --mem=150GB
#SBATCH --job-name=deepseek-33b-test
#SBATCH --mail-type=END
##SBATCH --mail-user=ms9761@nyu.edu
#SBATCH --output=slurm_%j.out

srun --exclusive --nodes 1 --ntasks 1 /scratch/ms9761/rea-llm/deepseek-33b/scripts/run-tgi.sh &

while true; do
    status=$(curl -s http://localhost:8000/ -w "%{http_code}")
    if [ "$status" == "200" ]; then
        echo "Server is up!"
        sh /scratch/ms9761/rea-llm/deepseek-33b/scripts/run-test.sh
        echo "running python request script"
        break
    else
        echo "Server is not up yet; status=$status"
        sleep 1
    fi
done

