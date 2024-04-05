#!/bin/bash

#SBATCH --ntasks-per-node=2
##SBATCH --cpus-per-task=2
#SBATCH --time=1:00:00
#SBATCH --mem=200GB
#SBATCH --job-name=remove-tar
#SBATCH --mail-type=END
#SBATCH --mail-user=ds6934@nyu.edu

## First we ensure a clean environment by purging the current one
module purge

# Directory to be deleted
DIR_TO_DELETE="/vast/ds6934/APK_DC"

echo "Starting deletion of $DIR_TO_DELETE"

# Check if the directory exists
if [ -d "$DIR_TO_DELETE" ]; then
    # Use rm command to delete the directory and its contents
    rm -rf "$DIR_TO_DELETE"
    echo "$DIR_TO_DELETE has been deleted."
else
    echo "$DIR_TO_DELETE does not exist."
fi


echo "Deletion process completed."
