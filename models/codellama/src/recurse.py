import requests
import json
import os

HOST = "localhost"
PORT = "8000"
HEADERS = {"Content-Type": "application/json",}

BASE_DIR = "/scratch/ms9761/rea-llm/codellama/"
#BASE_DIR = "C:/Users/mshab/Documents/NYU/Research/LLM/models/codellama/"
QUESTIONS_PATH = BASE_DIR + "inputs/questions.json"
DECOMPILED_CODE_DIR = BASE_DIR + "decompiled_code/"  # This would be DJ's scratch folder
OUTPUT_DIR = BASE_DIR + "outputs_text/"
RECURSE_DIR = "/scratch/ms9761/rea-llm/construct_json/app_files/test/"

INSTRUCTION_KEY = "[INST]Analyze the following script of code that will be presented to you between [CODE] and [/CODE] tags and answer the accompanying question.[/INST]\n"
with open(QUESTIONS_PATH, "r") as questions_json:
    QUESTIONS = json.load(questions_json)


class Func:
    def __init__(self, given_code=None):
        self.outputs = {"code": code, "results": {}}

    def get_prompt_key(self, code=None):
        # TODO: How do we format this?
        if given_code is not None:
            code = given_code
        else:
            code = self.outputs["code"]
        return f"[CODE]\n{code}\n[/CODE]\n\n"

    def save_response(self, question_num, question, response):
        self.outputs["results"][question_num] = {"question": question, "response": response, "answers": {}}
    
    def analyze_response(self, question_num, answers):
        response = self.outputs["results"][question_num]["response"]
        for idx in range(1, len(answers) + 1):
            self.outputs["results"][question_num]["answers"][answers[str(idx)]] = answers[str(idx)].lower() in response


class APK:
    def __init__(self):
        # For non recursive summary
        self.funcs = {}

        # For recursive summary
        self.raw = None
        self.apk_functions = {}
        self.results = {}

    def get_func_name(self, func_num):
        return f"Function_{func_num}"

    def read_data_from_file(self, apk_dir, recurse=False):
        # TODO: Need to work on processing data from DJ's directory
        with open(apk_dir, "r") as infile:
            apk_data = json.load(infile)
            if recurse:
                self.raw = apk_data['raw'] # This is the call graph of the following apk (entrypoints and childern functions)
                self.apk_functions = apk_data['functions'] # This is a list of the functions from each apk json
                print(f"APK functions: {self.apk_functions}")
                #self.results = self.recursive_summarize_functions(apk_data)
            else:
                self.raw = apk_data['raw'] # This is the raw code of the following apk
                self.apk_functions = apk_data['functions'] # This is a list of the functions from each apk json
                for func_num, function in enumerate(apk_functions):
                    print(f"Processing function {func_num + 1}, which looks like this: {function}")
                    func_name = self.get_func_name(func_num + 1)
                    self.funcs[func_name] = Func(function)
    
    def get_func_name_from_entry_point(self, entry_point):
        """Implement logic to extract function name from entry point string"""
        # For example, if entry point is "<androidx.fragment.app.FragmentActivity: void <init>()>",
        # the function name would be "void <init>()"
        func_name = entry_point.split(": ")[-1].replace('>', '')
        func_name = func_name.replace('<', '')
        return func_name

    def get_summarization(self, code):
        """Send request to LLM to summarize the given code"""
        # Implement your logic here to send request to LLM and get summarized output
        summarized_output = self.send_requests_to_llm(HOST, PORT, HEADERS, INSTRUCTION_KEY, QUESTIONS, code)
        return summarized_output

    def send_requests_to_llm(self, host, port, headers, instruction_key, questions, code=None):

        if code is not None:
            prompt_key = f"[CODE]\n{code}\n[/CODE]\n\n"
            for question_num in questions:
                curr_question = questions[question_num]["question"]
                full_prompt = instruction_key + prompt_key + curr_question
                data = {
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": 2000,
                    },
                }

                print("Sending request to server...")
                response = requests.post(f"http://{host}:{port}/generate", headers=headers, json=data)
                llm_response = response.json()["generated_text"]
                print("Response received!")

                # Come back to this later (BLEU evaluation metrics)
                # func_obj.analyze_response(question_num, questions[question_num]["answers"])
                # print("Response analyzed!")

                return llm_response
        else:
            for func_obj in self.funcs.values():
                prompt_key = func_obj.get_prompt_key()

                for question_num in questions:
                    curr_question = questions[question_num]["question"]
                    full_prompt = instruction_key + prompt_key + curr_question
                    data = {
                        "inputs": full_prompt,
                        "parameters": {
                            "max_new_tokens": 2000,
                        },
                    }

                    print("Sending request to server...")
                    response = requests.post(f"http://{host}:{port}/generate", headers=headers, json=data)
                    llm_response = response.json()["generated_text"]
                    func_obj.save_response(question_num, curr_question, llm_response)
                    print("Response received!")

                    func_obj.analyze_response(question_num, questions[question_num]["answers"])
                    print("Response analyzed!")


    def recursive_summarize_functions(self):
        results_dict = {}
        for entry_point_name, entry_point_data in self.apk_functions.items():

            # Clean up the entry point name
            if "Entry-point: " not in entry_point_name:
                print("Not an entry point function, skipping...")
                continue
            
            entry_point_func_name = self.get_func_name_from_entry_point(entry_point_name)
            entry_point_func_code = entry_point_data["code"]
            print("Summarizing entry point:", entry_point_func_name)

            # Check if children functions exist
            children = entry_point_data.get("children", [])


            # Check if children functions exist
            if children and len(entry_point_func_code) > 0:

                # Create a list for the summaries of the children functions
                summarized_callees = {}
                for child in children:

                    # Get the function name of the child function
                    child_func_name = self.get_func_name_from_entry_point(child)
                    
                    print(f"The parent function of the current child is: {self.apk_functions[child]['parent']}")
                    if child in self.apk_functions.keys() and self.apk_functions[child]["parent"] == entry_point_name:
                        child_func_code = self.apk_functions[child]["code"]
                        if child_func_code == "    None":
                            print("Child function code is None, skipping...")
                            continue

                        # Send request to LLM to summarize child function
                        summarized_child_func = self.get_summarization(child_func_code)
                        print("Summarized child function:", summarized_child_func)
                        summarized_callees[child_func_name] = summarized_child_func
                    else:
                        print("Child function not found:", child_func_name)

                # Use summarized_callees to help summarize the entry point function
                if len(summarized_callees) > 1:
                    summary_list = list(summarized_callees.values()) # grab the summaries from the list of child functions
                    collective_child_summaries = " ".join(summary_list) + "\n[INST]Based on the previous child function summaries, summarize the following code for the parent function:[/INST]\n"
                    summarized_entry_point_func = self.get_summarization(collective_child_summaries + entry_point_func_code)
                    print("Summarized entry point function:", summarized_entry_point_func)
                else:
                    summarized_callees["None"] = "No children functions found, no summary generated."
                    print(f"Entry point function code: {entry_point_func_code}")
                    summarized_entry_point_func = self.get_summarization(entry_point_func_code)
                    print("Summarized entry point function:", summarized_entry_point_func)
                results_dict[entry_point_name] = {"entry_point name": entry_point_func_name, "code": entry_point_data["code"], "summary": summarized_entry_point_func, "children": summarized_callees}

            else:
                print("No children functions for this entry point")
                # Summarize the entry point function
                if len(entry_point_func_code) > 0:
                    summarized_entry_point_func = self.get_summarization(entry_point_func_code)
                    print("Summarized entry point function:", summarized_entry_point_func)
                else:
                    print("Entry point function not found:", entry_point_func_name)
                    summarized_entry_point_func = "Entry point function not found."
                results_dict[entry_point_name] = {"entry_point name": entry_point_func_name, "code": entry_point_data["code"], "summary": summarized_entry_point_func, "children": {"None": "No children functions found, no summary generated."}}
        
        return results_dict

    def save_recurse_as_text(self, text_dir, apk_name):
        app_title = f"===================={apk_name}===================="
        text = f"{app_title}\n\n"
        for entry_point, entry_point_data in self.results.items():
            print("Entry point data:", entry_point_data)
            header = f"--------------------{entry_point_data['entry_point name']}--------------------"
            code = entry_point_data["code"]
            entry_point_response = 'Response: ' + entry_point_data["summary"]
            child_summary = ""
            if len(entry_point_data["children"]) > 1:
                child_responses = f"Child Function: {entry_point_data['children']}"
            else:
                for child_function_name, child_summary in entry_point_data["children"]:
                    child_responses += f"Child Function {child_function_name}:\n{child_summary}\n\n"
            text += f"{header}\n{code}\n\n{entry_point_response}\n{child_responses}\n\n"
        
        with open(text_dir + "_recurse.txt", "w") as outfile:
            outfile.write(text)
            outfile.close()

    def save_as_text(self, text_dir, apk_name):
        app_title = f"===================={apk_name}===================="
        text = f"{app_title}\n\n"
        for func_name, func_obj in self.funcs.items():
            header = f"--------------------{func_name}--------------------"
            code = func_obj.outputs["code"]
            response = ""
            for question_num in QUESTIONS:
                results = func_obj.outputs["results"][question_num]
                print(results)
                response += f"Question {question_num}: {results['question']}\nResponse: {results['response']}\n\n"
                print(response)
            text += f"{header}\n{code}\n\n{response}\n\n"
        
        with open(text_dir + ".txt", "w") as outfile:
            outfile.write(text)
            outfile.close()

    def save_as_json(self, json_dir):
        output = {func_name: func_obj.outputs for func_name, func_obj in self.funcs.items()}

        with open(json_dir, "w") as outfile:
            json.dump(output, outfile, indent=2)

if __name__ == "__main__":
    for apk in os.listdir(RECURSE_DIR):
        print("Processing APK:", apk)
        curr_apk = APK()
        #curr_apk.read_data_from_file(DECOMPILED_CODE_DIR + apk) # For non recursive summary
        print("Parsing through functions (non-recursive)...\n")

        # Store json data into the APK object (raw and apk_functions)
        curr_apk.read_data_from_file(RECURSE_DIR + apk, recurse=True) 

        # Run the recursive summarization for the apk
        curr_apk.results = curr_apk.recursive_summarize_functions()
        
        
        print("Parsing complete!\n")
        print(f"Results: {curr_apk.results}")
        print("Saving output...")
        curr_apk.save_recurse_as_text(OUTPUT_DIR + apk, apk)
        print(f"Output saved at {OUTPUT_DIR + apk}!")



