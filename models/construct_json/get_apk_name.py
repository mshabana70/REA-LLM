import os

apks = []
def list_directories(path):
    # Check if the provided path is a directory
    if not os.path.isdir(path):
        print("Provided path is not a directory.")
        return

    # Iterate through the items in the directory
    for item in os.listdir(path):
        # Construct the full path
        full_path = os.path.join(path, item)

        # Check if the item is a directory and print its name
        if os.path.isdir(full_path):
            print(item)
            apks.append(item)
    

# Path to the directory
directory_path = '/scratch/ds6934/APK_Test_DC/maltest'

# List the directories
list_directories(directory_path)
with open("all_apks.txt","w") as f:
    for i in apks:
        f.write(str(i)+"\n")
    
