import os
import re
import sys

def find_function_in_file(file_path, function_name,pattern):
    """
    Search for a function in a given file and print its contents if found.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    # Pattern to match the function definition.
    # This is a simple pattern and might need adjustments to fit your exact requirements.
    pat =  pat = rf"{pattern}\s+{function_name}\s*\((.*?)\)\s*\{{(.*?)\}}"

    matches = re.findall(pat, content, re.DOTALL)

    if matches:
        print(f"Found in {file_path}:")
        for args, body in matches:
            print(f"{pattern} {function_name}({args}) {{\n{body}\n}}\n")
        return True
    return False

def search_directory_for_function(directory, function_name,pattern):
    """
    Walk through the directory and search each Java file for the function.
    """
    found = False
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                if find_function_in_file(file_path, function_name,pattern):
                    found = True
                    break
    if not found:
        print(f"Function {function_name} not found in any Java files in {directory}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python search_function.py <directory_path> <function_name>")
        sys.exit(1)

    directory_path = sys.argv[1]
    function_name = sys.argv[2]
    pattern = sys.argv[3]
    search_directory_for_function(directory_path, function_name,pattern)