#!/bin/bash

##SBATCH --nodes=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:4
#SBATCH --constraint="a100|h100"
#SBATCH --time=8:00:00
#SBATCH --mem=369GB
#SBATCH --job-name=mix22
#SBATCH --mail-type=END
##SBATCH --mail-user=ms9761@nyu.edu
#SBATCH --output=slurm_%j.out

echo "HELLO"
/scratch/ms9761/rea-llm/mixtral-22B/scripts/run-vllm.sh &
echo "HELLO2"

while true; do
    status=$(curl -s -o /dev/null http://localhost:50000/v1/models/ -w "%{http_code}")
    if [ "$status" == "307" ]; then
        echo "Server is up!"
	sh /scratch/ms9761/rea-llm/mixtral-22B/scripts/run-test.sh
	echo "running python request script"
        break
    else
        echo "Server is not up yet; status=$status"
        sleep 1
    fi
done

