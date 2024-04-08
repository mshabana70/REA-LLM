import os
import shutil
import random

def copy_random_apks(source_directory, destination_path, num_apks=10):
    # Get list of all files in the source directory
    all_files = os.listdir(source_directory)
    # Filter only APK files
    apk_files = [file for file in all_files if file.endswith(".apk")]

    # Ensure destination directory exists, create if it doesn't
    os.makedirs(destination_path, exist_ok=True)

    # Shuffle the list of APKs
    random.shuffle(apk_files)

    # Copy the specified number of APKs to the destination path
    for apk_file in apk_files[:num_apks]:
        source_file = os.path.join(source_directory, apk_file)
        destination_file = os.path.join(destination_path, apk_file)
        shutil.copy(source_file, destination_file)
        print(f"Copied {apk_file} to {destination_path}")
    
    return apk_files[:num_apks]

def find_and_copy_tarballs(apk_files, tarball_directory, destination_directory):
    # Get list of all files in the tarball directory
    all_tarball_files = os.listdir(tarball_directory)
    # Filter only tarball files
    tarball_files = [file for file in all_tarball_files if file.endswith(".tar.zst")]

    # Ensure destination directory for tarball files exists, create if it doesn't
    os.makedirs(destination_directory, exist_ok=True)

    # Search for corresponding tarball files for copied APKs
    for apk_file in apk_files:
        apk_name_without_extension = os.path.splitext(apk_file)[0]
        corresponding_tarball = apk_name_without_extension + "_decompiled.tar.zst"
        if corresponding_tarball in tarball_files:
            source_tarball = os.path.join(tarball_directory, corresponding_tarball)
            destination_tarball = os.path.join(destination_directory, corresponding_tarball)
            shutil.copy(source_tarball, destination_tarball)
            print(f"Copied {corresponding_tarball} to {destination_directory}")

def check_directory_contents(apk_directory, tarball_directory):
    # Get list of all files in the APK directory
    apk_files = set(os.listdir(apk_directory))
    # Get list of all files in the tarball directory
    tarball_files = set(os.listdir(tarball_directory))

    # Remove any files in the APK directory that don't have corresponding tarballs
    for apk_file in apk_files.copy():
        apk_name_without_extension = os.path.splitext(apk_file)[0]
        corresponding_tarball = apk_name_without_extension + "_decompiled.tar.zst"
        if corresponding_tarball not in tarball_files:
            apk_files.remove(apk_file)
            print(f"Removed {apk_file} from {apk_directory} as there is no corresponding tarball")

    # Remove any files in the tarball directory that don't have corresponding APKs
    for tarball_file in tarball_files.copy():
        apk_name = os.path.splitext(tarball_file)[0] + ".apk"
        if apk_name not in apk_files:
            tarball_files.remove(tarball_file)
            print(f"Removed {tarball_file} from {tarball_directory} as there is no corresponding APK")


if __name__ == "__main__":
    source_directory = "/scratch/cg4053/downloads/"  
    destination_path = "/scratch/ms9761/rea-llm/construct_json/app_files/apks/"  
    num_apks = 10  # Number of APKs to copy, change as needed
    apk_files = copy_random_apks(source_directory, destination_path, num_apks)
    
    tarball_directory = "/scratch/ds6934/APK_DC/Tarball_DC/"  
    destination_tarball_directory = "/scratch/ms9761/rea-llm/construct_json/app_files/tars/"  
    find_and_copy_tarballs(apk_files, tarball_directory, destination_tarball_directory)

    # Check directory contents
    check_directory_contents(destination_path, destination_tarball_directory)

