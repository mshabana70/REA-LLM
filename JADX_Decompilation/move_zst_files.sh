#!/bin/bash

#SBATCH --job-name=move_zst_-vast
#SBATCH --mail-type=END
#SBATCH --mail-user=ds6934@nyu.edu

# Define the source directory where to look for .zst files
# Use . for the current directory or specify a path
SOURCE_DIR="/scratch/ds6934"

# Define the target directory where the .zst files will be moved
TARGET_DIR="/vast/ds6934/APK_DC/Tarball"

# Check if the target directory exists, create if it does not
if [ ! -d "$TARGET_DIR" ]; then
  echo "Target directory $TARGET_DIR does not exist, creating it."
  mkdir -p "$TARGET_DIR"
fi

# Find and move .zst files to the target directory
find "$SOURCE_DIR" -type f -name '*.zst' -exec mv {} "$TARGET_DIR" \;

echo "Move operation completed."


