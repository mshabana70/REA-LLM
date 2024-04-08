import subprocess
import os
import re
import sys

APK_path = '/scratch/ms9761/rea-llm/construct_json/app_files/apks/'
Tarball_path ='/scratch/ms9761/rea-llm/construct_json/app_files/tars/'
Base_dir = '/scratch/cg4053/CallGraph/'
Soot_path = '/scratch/cg4053/soot_tur/SootStarterCode/'
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
                elif line.startswith("  invokes"):
                    if 'invokes' not in current_entry:
                        current_entry['children'] = []
                    current_entry['children'].append(line)
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
            result = subprocess.run([Soot_path + "/RunSootTutorial", self.apk_path], capture_output=True, text=True)
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

class Find_Func:
    de_apk_path = ''
    func_content = ''
    directory = ''
    file_path = ''
    pattern = ''
    return_type = ''
    method_name = ''
    class_path = ''

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
        cmd = ['tar', '--use-compress-program=unzstd', '-xvf', self.de_apk_path, '-C', self.directory]

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

        # Extract the class path, return type, and method name if a match is found
        if match:
            class_path = match.group(1)
            resource_path = unzip_path+"/sources/"
            
            self.class_path = os.path.join(resource_path, class_path.replace(".", "/") + ".java")
            print("class_path =" + str(self.class_path))
            self.return_type = match.group(2)
            self.method_name = match.group(3)
            print("method_name=" + self.method_name)
            print("return_type=" + self.return_type)
            print("***********************************")
        else:
            print("No match found")
        

  
    def find_function_in_file(self):
        """
        Search for a method in a given file and print its contents if found, based on access modifiers.
        """
        if self.class_path != '':
            with open(self.class_path, 'r') as file:
                content = file.read()
        
            # Regular expression patterns for function and class extraction
            function_pattern = r'((public|private|protected|static|\s)*)\s*[\w<>[]+\s+([\w]+)\s*\([^)]*\)\s*({)?'
            class_pattern = r'(public|private|protected|\s)*\s*class\s+([\w]+)\s*(extends\s+\w+\s*)?(implements\s+\w+\s*)?{'
            
            # Compile regular expression patterns
            function_regex = re.compile(function_pattern)
            class_regex = re.compile(class_pattern)
            
            # Find functions
            functions = [(match.group(3), match.group()) for match in function_regex.finditer(content)]
            # Find classes
            classes = [(match.group(2), match.group()) for match in class_regex.finditer(content)]
            print(functions)
            print(classes)
            return None
        # Build a pattern to match a method starting with access modifiers
        # This regex looks for the method name ensuring it is preceded by public, private, or protected,
        # and then captures everything until the next public, private, protected, or the end of the file.
        # Note: This simple approach does not account for all possible complexities of Java syntax.
    #     pat = rf"(public|protected|private)\s+.*?\b{re.escape(self.method_name)}\b.*?(?=(public|protected|private)\s+|\Z)"
        
    #     matches = re.findall(pat, content, re.DOTALL)

    #     if matches:
    #         for match in matches:
    #             # Extracted content includes the entire method
    #             method_content = match[0]
    #             print(f"Method content for {self.method_name}: \n{method_content}\n")
    #             # Assuming you want to return the first match's content
    #             return method_content
    #         print("Method found.")
    #     else:
    #         print(f"Method {self.method_name} not found in {self.class_path}.")
    # else:
    #     print("Class path is not set.")
    #     return None


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
    unzip_path = Base_dir + apk_base_name
    Tarball_path = Tarball_path + tarball_name
    
    # print(apk_base_name)
    # print("Tarball_path=" +Tarball_path)
    # print("unzip_path="+ unzip_path)

    callgraph = CallGraph(APK_path)
    apk_callgraph = callgraph.get_call_graph()

    find_func = Find_Func(Tarball_path,unzip_path)
    find_func.unzip_tar_zst()
     # now iterate all entries in callgraph

    for entry in apk_callgraph:
        find_func.parse_entry(entry['entry_point'])
        
        find_func.find_function_in_file()


        
        



