#!/bin/bash

#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:rtx8000:4
#SBATCH --time=8:00:00
#SBATCH --mem=200GB
#SBATCH --job-name=codellama-70b-test
#SBATCH --mail-type=END
##SBATCH --mail-user=ms9761@nyu.edu
#SBATCH --output=slurm_%j.out

echo "HELLO"
srun --exclusive --nodes 1 --ntasks 1 /scratch/ms9761/rea-llm/codellama-70b/scripts/run-tgi.sh &
echo "HELLO2"

while true; do
    status=$(curl -s http://localhost:8000/ -w "%{http_code}")
    if [ "$status" == "200" ]; then
        echo "Server is up!"
	sh /scratch/ms9761/rea-llm/codellama-70b/scripts/run-test.sh
	echo "running python request script"
        break
    else
        echo "Server is not up yet; status=$status"
        sleep 1
    fi
done

