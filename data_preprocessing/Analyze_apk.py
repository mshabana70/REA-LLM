import subprocess
import os
import re
import sys
from treesitter import find_function_body
import json
import time

APK_path = '/scratch/ms9761/rea-llm/construct_json/app_files/apks/'
Tarball_path ='/scratch/ms9761/rea-llm/construct_json/app_files/tars/'
Base_dir = '/scratch/cg4053/soot_tur/SootStarterCode/intermediate/'
Result_dir = '/scratch/ms9761/rea-llm/construct_json/app_files/results/'
#Result_dir = '/scratch/cg4053/soot_tur/SootStarterCode/results/'
unzip_path = ''
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
                    current_entry['children'] = []
                elif line.startswith("  invokes"):
                    # if 'invokes' not in current_entry:
                    clean_line = line.replace('  invokes ', '', 1)
                    current_entry['children'].append(clean_line)
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
            print("!!!!!!!!!!!!!!!!!!!")
            print(str(output))
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

class Find_Func:
    de_apk_path = ''
    func_content = ''
    directory = ''
    file_path = ''
    pattern = ''
    return_type = ''
    method_name = ''
    class_path = ''
    invoke_class_path = ''
    invoke_method_name = ''
    def __init__(self,de_apk_path,directory):
        self.de_apk_path = de_apk_path
        self.directory = directory
    
    def unzip_tar_zst(self):
        """
        Unzips a .tar.zst file into a specified output folder.

        :param file_path: Path to the .tar.zst file.
        :param output_folder: Directory where the contents should be extracted.
        """
        # Ensure the output directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Command to decompress and extract the .tar.zst file
        cmd = ['tar', '--use-compress-program=unzstd', '-xf', self.de_apk_path, '-C', self.directory]

        try:
            # Execute the command
            subprocess.check_call(cmd)
            print(f"File {self.de_apk_path} successfully decompressed and extracted to {self.directory}")
        except subprocess.CalledProcessError as e:
            # Handle errors during the subprocess execution
            print(f"An error occurred while decompressing {self.de_apk_path}: {e}")

    def parse_entry(self,Entrypoint):
        pattern = r"Entry-point: <(.*?): (\w+) (\w+\(.*?\))>"

        # Use re.search to find a match
        match = re.search(pattern, Entrypoint)
        class_path = ''
        method_name = ''
        return_type = ''
        # Extract the class path, return type, and method name if a match is found
        if match:
            raw_class_path = match.group(1)
            resource_path = unzip_path+"/sources/"
            
            class_path = os.path.join(resource_path, raw_class_path.replace(".", "/") + ".java")
            # print("raw_class_path =" + str(raw_class_path))
            # print("class_path =" + str(class_path))
            return_type = match.group(2)
            method_name = match.group(3)
            # print("method_name=" + method_name)
            # print("return_type=" + return_type)
        else:
            print("No match found: " + str(Entrypoint))
            return (0,0,0,)
        return (class_path, return_type, method_name)
    
    def parse_invokes(self, Invokes):
        print("INVOKES = ============")
        print(Invokes)
        pattern = r'<([\w.$]+):\s*([\w.$]+)\s+([\w$]+)\((.*?)\)>'

        # Perform the search
        match = re.search(pattern, Invokes)
        invoke_class_path = ''
        invoke_method_name = ''
        # Extract components if a match is found
        if match:
            invoke_class_path = match.group(1)
            invoke_method_name = match.group(3)

        return (invoke_class_path,invoke_method_name )
            
  
    def find_function_in_file(self,method_name, class_path):
        """
        Search for a method in a given file and print its contents if found, based on access modifiers.
        """
        content = ''
        if class_path != '':
            try:
                with open(class_path, 'r') as file:
                    content = file.read()
            except FileNotFoundError as e:
                print(f"Error: {e}")
                return None   
        method = re.sub(r'\(.*\)', '', method_name)
        func_body = find_function_body(content, method)
        return func_body
    
    def iterate_callgraph(self, apk_callgraph):
        # now iterate all entries in callgraph/
        out_data = {
            'raw': apk_callgraph,
            'functions': {}
        }
        for entry in apk_callgraph:
            entry_point_name = entry['entry_point']
            class_path, return_type, method_name = self.parse_entry(entry['entry_point'])

            if class_path != 0:
                content = self.find_function_in_file(method_name,class_path)
                outline = str(return_type)+'  '+str(method_name)+'  '+str(content)
                if 'children' in entry:
                    list_of_children = entry['children']
                    for child in list_of_children:
                        invoke_class_path,invoke_method_name = self.parse_invokes(child)
                        resource_path = unzip_path+"/sources/"
                        invoke_class_path = os.path.join(resource_path, invoke_class_path.replace(".", "/") + ".java")
                        try:
                            invoke_content = self.find_function_in_file(invoke_method_name,invoke_class_path)
                            invokes_outline = '  '+str(invoke_method_name)+'  '+str(invoke_content)
                            out_data['functions'][child] = {"code": invokes_outline, "parent": entry_point_name}
                        except:
                            
                            continue
                else:
                    list_of_children = []
                out_data['functions'][entry_point_name] = {"code": outline, "children": list_of_children}
            else:
                continue
        
        return out_data

    def write_to_json(self, out_data, apk_base_name):
        json_path = Result_dir + apk_base_name.replace(".", "_") + '.json'
        with open(json_path, 'w') as json_file:
            json.dump(out_data, json_file, indent=4)
            

if __name__=='__main__':

    # if len(sys.argv) != 1:
    #     print("Usage: python Analyze_apk.py com.example.apk")
    #     sys.exit(1)

    # example usage: python Analyze_apk.py APK_path De_APK_path com.example.apk
    directory = False

    if "/" in sys.argv[1]:
        directory = True
    else:
        apk_name = sys.argv[1]
        # get tarball's name, the same with its original apk
        apk_base_name = apk_name[:-4]  # This removes the last 4 characters, '.apk'
        # Add _decompiled.tar.zst after the name
        tarball_name = apk_base_name + "_decompiled.tar.zst"

    # if the input is a directory
    if directory:
        APK_path = sys.argv[1] + '/'
        num_files = len(os.listdir(APK_path))
        num_files_analyzed = 0
        # parse the apk path for all apk files
        for file in os.listdir(APK_path):
            if file.endswith(".apk"):
                print(f"Analyzing {file}...")
                apk_name = file
                apk_base_name = apk_name[:-4]
                tarball_name = apk_name + "_decompiled.tar.zst"

                # Define paths for the apk, tarball, and unzip directory
                apk_file_path = APK_path + str(apk_name)
                unzip_path = Base_dir + apk_base_name 
                Tarball_path = Tarball_path + tarball_name

                # Create a CallGraph object and get the call graph
                callgraph = CallGraph(apk_file_path)
                apk_callgraph = callgraph.get_call_graph()

                # Create a Find_Func object and unzip the tarball
                find_func = Find_Func(Tarball_path,unzip_path)
                find_func.unzip_tar_zst()

                # Iterate through the call graph and find the functions
                out_data = find_func.iterate_callgraph(apk_callgraph)

                # Write the output to a JSON file
                find_func.write_to_json(out_data, apk_base_name)
                print(f"Analysis of {file} complete.")
                num_files_analyzed += 1
        print(f"Analysis of {num_files_analyzed} out of {num_files} files complete.")

    else:
        print(f"Analyzing {apk_name}...")
        # Define paths for the apk, tarball, and unzip directory
        APK_path = APK_path + str(apk_name)
        unzip_path = Base_dir + apk_base_name 
        Tarball_path = Tarball_path + tarball_name

        # Create a CallGraph object and get the call graph
        callgraph = CallGraph(APK_path)
        apk_callgraph = callgraph.get_call_graph()

        # Create a Find_Func object and unzip the tarball
        find_func = Find_Func(Tarball_path,unzip_path)
        find_func.unzip_tar_zst()

        # Iterate through the call graph and find the functions
        out_data = find_func.iterate_callgraph(apk_callgraph)

        # Write the output to a JSON file
        find_func.write_to_json(out_data, apk_base_name)
        print(f"Analysis of {apk_name} complete.")
    
    # print(apk_base_name)
    # print("Tarball_path=" +Tarball_path)
    # print("unzip_path="+ unzip_path)

    # callgraph = CallGraph(APK_path)
    # apk_callgraph = callgraph.get_call_graph()

    
    
    # # now iterate all entries in callgraph/
    # out_data = {
    #     'raw': apk_callgraph,
    #     'functions': []
    # }
    # for entry in apk_callgraph:

    #     class_path, return_type, method_name = find_func.parse_entry(entry['entry_point'])

    #     if class_path != 0:
    #         content = find_func.find_function_in_file(method_name,class_path)
    #         outline = str(return_type)+'  '+str(method_name)+'  '+str(content)
    #         out_data['functions'].append(outline)
            # if 'children' in entry:
            #     for i in entry['children']:
            #         class_path, method_name = find_func.parse_invokes(i)
            # else:
            #     continue


        
        



