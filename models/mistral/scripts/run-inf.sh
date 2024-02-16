#!/bin/bash

##SBATCH --nodes=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:rtx8000:4
#SBATCH --time=2:00:00
#SBATCH --mem=250GB
#SBATCH --job-name=mixtral-test
#SBATCH --mail-type=END
##SBATCH --mail-user=ms9761@nyu.edu
#SBATCH --output=slurm_%j.out

echo "HELLO"
srun --exclusive --nodes 1 --ntasks 1 /scratch/ms9761/rea-llm/mistral/scripts/run-vllm.sh &
echo "HELLO2"

while true; do
    status=$(curl -s http://0.0.0.0:8000/v1 -w "%{http_code}")
    if [ "$status" == "200" ]; then
        echo "Server is up!"
	sh /scratch/ms9761/rea-llm/mistral/scripts/run-test.sh
	echo "running python request script"
        break
    else
        echo "Server is not up yet; status=$status"
        sleep 1
    fi
done

