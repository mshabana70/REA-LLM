from openai import OpenAI
import json
import os 

# Replace 'YOUR_API_KEY' with your actual GPT-4 API key
API_KEY = 'YOUR_API_KEY'
RECURSE_DIR = 'YOUR_DIRECTORY'

# Endpoint URL for GPT-4 API
#API_URL = 'https://api.openai.com/v1/engines/davinci-codex/completions'
INSTRUCTION_KEY = "You are a helpful code evaluation bot that summarizes decompiled code from Android applications to aid security researchers in reversing android applications. Please, provide all answers in concise and accurate paragraph of what the decompiled code is doing.\n"
client = OpenAI(API_KEY)

class APK:
    def __init__(self):
        self.raw = []
        self.funcs = {}
        self.count = 0
        self.max_depth = 0

    def get_func_name(self, func_num):
        return f"Function_{func_num}"
    
    def get_func_code(self, func_uid):
        for func in self.funcs:
            if func_uid == func["UID"]:
                return func["code"]
        return None

    # Function to send request to GPT-4 API
    def send_request(self, prompt_text):
        response = client.chat.completions.create(
            model="davinci-codex",
            response_format={"type": "json_object"},
            messages=prompt_text, 
            max_tokens=2000
        )
        return response.choices[0].message.content

    def read_data_from_file(self, apk_path):
        # TODO: Need to work on processing data from DJ's directory
        with open(apk_path, "r") as infile:
            apk_data = json.load(infile)
        
        self.raw = apk_data['Raw']
        self.funcs = apk_data['Functions']
    
    def set_node_summary(self, node_uid, summary):
        for node in self.funcs:
            if node["UID"] == node_uid:
                node["ground_truth"] = summary
                print(f"Ground Truth set for node {node['method_name']}")
                return
        return

    def summarize_apk(self):
        self.results = {}

        for node in self.raw:
            node_method = node["method_name"]
            node_class = node["class_name"]
            node_uid = node["UID"]
            node_depth = int(node["Depth"])
            print(f"\n\n++++++++++++++Summarizing {node_method}++++++++++++++")

            # Set max depth
            if node_depth > self.max_depth:
                self.max_depth = node_depth

            # Check if current node has code
            node_code = self.get_func_code(node_uid)
            if node_code == "None":
                print("No code found for function, skipping...")
                self.set_node_summary(node_uid, "No code found for function")
                continue
            
            # Check node successors
            if len(node["Successors"]) == 0:
                print("No children nodes found, summarizing current function...")

                # Craft prompt key using code from current node
                chat = [
                    {"role": "system", "content": INSTRUCTION_KEY},
                    {"role": "user", "content": node_code}
                ]
                prompt_key = self.get_prompt_key(chat)
                print(f"Prompt key with no successors:\n{prompt_key}")

                # Summarize current node
                summary = self.send_request(prompt_key, QUESTIONS, one_sum=True)
                print(f"Summary for current node {node_method}: {summary}")

                # Save summary to current node
                self.set_node_summary(node_uid, summary)
                continue
            else:
                # Traverse children nodes and grab successor summaries
                success_sums = self.traverse_recursive(node)

                success_chat = f"Given the following summaries of the current code's sucessors:\n{success_sums}\n\nSummarize the following code in one paragraph:\n{node_code}\n"
                chat = [
                    {"role": "system", "content": INSTRUCTION_KEY},
                    {"role": "user", "content": success_chat}
                ]
                # Craft prompt key using successor summaries and code from current node
                prompt_key = self.get_prompt_key(chat)
                print(f"Prompt key with successors:\n{prompt_key}")

                # Summarize current node
                summary = self.send_request(prompt_key)
                print(f"Summary for current node {node_method}: {summary}")

                # Save summary to current node
                self.set_node_summary(node_uid, summary)

    def traverse_recursive(self, node, depth=0, max_depth=4):
        
        # Check if the current node is less than the max depth in call graph
        depth = int(node["Depth"])
        if depth == self.max_depth:
            # If we have reached the max depth, we stop traversing and summarize the current node
            return None
        else:
            print(f"Current depth: {depth}, Max depth: {self.max_depth}")

            # Get summaries of Successors
            successor_sums = []
            for method in node["Successors"]:
                print(f"Method: {method}")
                # Check if the method is in the functions list
                for func in self.funcs:
                    if func["method_name"] == method and method != node["method_name"]:
                        print(f"Function found: {func}")
                        if func["summary"] != "":
                            print(f"Summary found: {func['summary']}")
                            successor_sums.append(func["summary"])
                        else:
                            print("No summary found")
                        break
                
            
            # Join summaries of successors
            if len(successor_sums) > 0:
                joined_sums = " ".join(successor_sums)
                return joined_sums
            else:
                return None

    def get_prompt_key(self, prompt):
        long_sum = "\n\nSummarize the following code in one paragraph:\n"
        short_sum = "\n\nSummarize the following code in one sentence:\n"
        header = "Given the following summaries of the current code's sucessors:\n"
        if sum_length == "short" and success_sums is not None:
            return f"{header}\n{success_sums}\n{short_sum}\n\n[CODE]\n{code}\n[/CODE]"
        elif sum_length == "long" and success_sums is not None:
            return f"{header}\n{success_sums}\n{long_sum}\n\n[CODE]\n{code}\n[/CODE]"
        else:
            return f"{short_sum}\n[CODE]\n{code}\n[/CODE]\n\n"

    # Function to save response to a file
    def save_response(self, response_data, filename):
        with open(filename, 'w') as file:
            json.dump(response_data, file, indent=4)

# Example usage
if __name__ == '__main__':
    for apk_filename in os.listdir(RECURSE_DIR):
        print("Processing APK:", apk_filename)
        curr_apk = APK_Recurse()

        print("\nReading data from file...")
        curr_apk.read_data_from_file(RECURSE_DIR + apk_filename)

        print("\nSummarizing APK...")
        curr_apk.summarize_apk()

        print("Summarization complete!\n")

        print("Writing the results...")
        print(curr_apk.write_json(OUTPUT_DIR + apk_filename))
        exit()
        
        print("Parsing complete!\n")
        print(f"Results: {curr_apk.results}")
        print("Saving output...")
        curr_apk.save_as_text(OUTPUT_DIR + apk_filename, apk_filename)
        print(f"Output saved at {OUTPUT_DIR + apk_filename}!")