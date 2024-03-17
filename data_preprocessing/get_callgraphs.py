import subprocess
import os
import sys

def run_soot_tutorial(file_path):
    """
    Runs the `RunSootTutorial` command on the given file and returns the output.
    """
    try:
        result = subprocess.run(["./RunSootTutorial", file_path], capture_output=True, text=True)
        output = result.stdout
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error running RunSootTutorial on {file_path}: {e}")
        return None

def parse_output(output):
    """
    Parses the output from the `RunSootTutorial` command and returns a list of entry-points
    and their invokes.
    """
    entries = []
    if output:
        current_entry = {}
        for line in output.split('\n'):
            if line.startswith("Entry-point:"):
                if current_entry:
                    entries.append(current_entry)
                    current_entry = {}
                current_entry['entry_point'] = line
            elif line.startswith("  invokes"):
                if 'invokes' not in current_entry:
                    current_entry['invokes'] = []
                current_entry['invokes'].append(line)
        if current_entry:
            entries.append(current_entry)
        print(entries)
    return entries

# def walk_and_run_soot(target_folder):
#     """
#     Walks through the target folder, runs `RunSootTutorial` on each file, and collects the results.
#     """
#     all_results = []
#     for root, dirs, files in os.walk(target_folder):
#         print("Scanning all files!")
#         for file in files:
#             file_path = os.path.join(root, file)
#             print(file_path)
#             output = run_soot_tutorial(file_path)
#             parsed_output = parse_output(output)
#             if parsed_output:
#                 all_results.extend(parsed_output)

#     return all_results

if __name__=='__main__':
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        sys.exit(1)
    output = run_soot_tutorial(file_path)
    parsed_output = parse_output(output)
    if parsed_output:
        print(output)

# Example usage:
# target_folder = "/scratch/cg4053/CallGraph/"
# results = walk_and_run_soot(target_folder)
# print(results)