#!/bin/bash
#SBATCH --ntasks-per-node=1
##SBATCH --cpus-per-task=4
#SBATCH --time=12:00:00
#SBATCH --mem=32GB
#SBATCH --job-name=tar_decompile-vast
#SBATCH --array=0-562%100
#SBATCH --mail-type=END
#SBATCH --mail-user=ds6934@nyu.edu
#SBATCH --output=slurm_logs/slurm_tar/slurm_%A_%a.out

# Calculate file indices for this task
START=$((SLURM_ARRAY_TASK_ID * 300))
END=$((START + 299))

## First we ensure a clean environment by purging the current one
module purge

# Load the JDK module
module load jdk/20.0.2

# Set the path to the JADX executable
JADX_PATH="/scratch/ds6934/tools/bin/jadx"

# Set the path to the APKs directory
APKS_DIR="/scratch/cg4053/downloads/"

# Set the path to the output directory
OUTPUT_DIR="/vast/ds6934/APK_DC/"

# Final Tarball directory
TAR_DIR="/vast/ds6934/APK_DC/Tarball/"

# Ensure TAR_DIR exists
mkdir -p "$TAR_DIR"

# Collect APK files into an array
APK_FILES=($(find "$APKS_DIR" -name "*.apk"))
TOTAL_FILES=${#APK_FILES[@]}

# Process only a subset of files based on the job array index
for ((i=START; i<=END && i<TOTAL_FILES; i++)); do
  APK=${APK_FILES[i]}
  filename=$(basename "$APK")
  filename_no_ext="${filename%.apk}"

  # Create a subdirectory for each decompiled APK
  mkdir -p "$OUTPUT_DIR/$filename_no_ext"

  # Decompile the APK using JADX
  "$JADX_PATH" -q -v -d "$OUTPUT_DIR/$filename_no_ext" "$APK"

  # Change directory to the output directory
  cd "$OUTPUT_DIR/$filename_no_ext"

  # Find .java and .xml files, archive them, and compress the archive
  find . '(' -name '*.java' -o -name '*.xml' ')' -print0 | tar --null --files-from=- -cf "${filename_no_ext}_decompiled.tar"
  
  # Use the full path to zstd
  /home/bd52/bin/zstd --rm "${filename_no_ext}_decompiled.tar"

  # Move the compressed tarball to ${TAR_DIR}
  if [ -f "${filename_no_ext}_decompiled.tar.zst" ]; then
    mv "${filename_no_ext}_decompiled.tar.zst" "$TAR_DIR"
    # Remove the decompiled APK directory
    rm -rf "$OUTPUT_DIR/$filename_no_ext"
  else
    echo "Error: Compressed file does not exist."
  fi

  # Return to the parent directory
  cd - 

done
