import subprocess
import os
import re
import sys

APK_path = '/scratch/ms9761/rea-llm/construct_json/app_files/apks/'
Tarball_path ='/scratch/ms9761/rea-llm/construct_json/app_files/tars/'

class CallGraph:
    apk_path = ''
    call_graph=[]

    def __init__(self,apk_path):
        self.apk_path = apk_path


    def parse_output(self,output):
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
        self.call_graph = entries
        return entries

    def run_soot_tutorial(self):
        """
        Runs the `RunSootTutorial` command on the given file and returns the output.
        """
        try:
            result = subprocess.run(["./RunSootTutorial", self.apk_path], capture_output=True, text=True)
            output = result.stdout
            return output
        except subprocess.CalledProcessError as e:
            print(f"Error running RunSootTutorial on {self.apk_path}: {e}")
            return None


    def get_call_graph(self):
        if not os.path.exists(self.apk_path):
            print(f"The file {self.apk_path} does not exist.")
            sys.exit(1)
        output = self.run_soot_tutorial()
        parsed_output = self.parse_output(output)
        if parsed_output:
            print(output)
        return self.call_graph
    
    def format_output_as_json(self, output_file, found_functions=None):
        """
        Formats the call graph output and found functions as JSON and writes it to the specified file.
        """
        output_data = {"raw": self.call_graph}

        if found_functions:
            output_data["functions"] = found_functions

        with open(output_file, 'w') as json_file:
            json.dump(output_data, json_file, indent=4)
        
        print(f"Output formatted and written to {output_file}.")


class Find_Func:
    de_apk_path = ''
    func_content = []
    directory = ''
    file_path = ''
    def __init__(self,de_apk_path,directory):
        self.de_apk_path = de_apk_path
        self.directory = directory

    def search_directory_for_function(self,function_name,pattern):

        """
        Walk through the directory and search each Java file for the function.
        """

        found = False
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.endswith(".java"):
                    self.file_path = os.path.join(root, file)
                    if self.find_function_in_file(self.file_path, function_name,pattern):
                        found = True
                        break
        if not found:
            print(f"Function {function_name} not found in any Java files in {self.directory}")



    def find_function_in_file(self,file_path, function_name,pattern):
        """
        Search for a function in a given file and print its contents if found.
        """
        result_string = ""

        with open(file_path, 'r') as file:
            content = file.read()
        pat =  pat = rf"{pattern}\s+{function_name}\s*\((.*?)\)\s*\{{(.*?)\}}"

        matches = re.findall(pat, content, re.DOTALL)

        if matches:
            print(f"Found in {file_path}:")
            for args, body in matches:
                self.func_content.append(f"{pattern} {function_name}({args}) {{\n{body}\n}}\n")
            return True
        return False



if __name__=='__main__':

    # if len(sys.argv) != 1:
    #     print("Usage: python Analyze_apk.py com.example.apk")
    #     sys.exit(1)

    # example usage: python Analyze_apk.py APK_path De_APK_path com.example.apk
    apk_name = sys.argv[1]
    # get tarball's name, the same with its original apk
    apk_base_name = apk_name[:-4]  # This removes the last 4 characters, '.apk'
    # Add _decompiled.tar.zst after the name
    tarball_name = apk_base_name + "_decompiled.tar.zst"

    APK_path = APK_path + str(apk_name)
    Tarball_path = Tarball_path + tarball_name

    callgraph = CallGraph(APK_path)
    apk_callgraph = callgraph.get_call_graph()

    # now iterate all entries in callgraph

    for entry in apk_callgraph:
        print(entry)
        print('----------------')
    
    # Example usage of find_function_in_file
    find_func = Find_Func(APK_path, directory)
    find_func.search_directory_for_function("function_name", "pattern")
    found_functions = find_func.func_content

    # Call the method with found functions
    if found_functions is None:
        print(f"No functions found in the {apk_base_name}.")
    callgraph.format_output_as_json(output_file, found_functions)



