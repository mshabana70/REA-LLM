import os
import re

SOOT_PATH = '/scratch/ms9761/rea-llm/construct_json/app_files/'

class CallGraph:

    def __init__(self, SOOT_PATH):
        self.SOOT_PATH = SOOT_PATH
        self.call_graph = {}
    
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

    def get_call_graph(self):
        """Run the soot command and save the call graph"""
        if not os.path.exists(self.apk_path):
            print(f"The file {self.apk_path} does not exist.")
            sys.exit(1)
        output = self.run_soot_tutorial()
        parsed_output = self.parse_output(output)
        if parsed_output:
            print(output)
        return self.call_graph