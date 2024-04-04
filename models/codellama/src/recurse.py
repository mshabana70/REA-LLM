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
        self.code = given_code
        self.results = {}

    def get_prompt_key(self, given_code=None):
        # TODO: How do we format this?
        if given_code is not None:
            code = given_code
        else:
            code = self.code
        return f"[CODE]\n{code}\n[/CODE]\n\n"

    def save_response(self, question_num, question, response):
        self.results[question_num] = {"question": question, "response": response, "answers": {}}
    
    def analyze_response(self, question_num, answers):
        response = self.results[question_num]["response"].lower()
        for answer in answers.values():
            self.results[question_num]["answers"][answer] = answer.lower() in response


class APK:
    def __init__(self):
        self.funcs = {}

    def get_func_name(self, func_num):
        return f"Function_{func_num}"
    
    def get_func_name_from_entry_point(self, entry_point):
        """Implement logic to extract function name from entry point string"""
        # For example, if entry point is "<androidx.fragment.app.FragmentActivity: void <init>()>",
        # the function name would be "void <init>()"
        if "Entry-point: " not in entry_point:
            return entry_point
        func_name = entry_point.split(": ")[-1].replace('>', '')
        func_name = func_name.replace('<', '')
        return func_name

    def ask_llm(self, prompt_key, question, host=HOST, port=PORT, headers=HEADERS, instruction_key=INSTRUCTION_KEY):
        full_prompt = instruction_key + prompt_key + question
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

    def read_data_from_file(self, apk_path):
        # TODO: Need to work on processing data from DJ's directory
        with open(apk_path, "r") as infile:
            apk_data = json.load(infile)
            
        for func_num, func in enumerate(apk_data['functions']):
            func_name = self.get_func_name(func_num + 1)
            print(f"Processing {func_name}, which looks like this: {func}")
            self.funcs[func_name] = Func(func)

    def summarize_func(self, prompt_key, questions):
        llm_responses = {}

        for question_num in questions.keys():
            curr_question = questions[question_num]["questions"]
            llm_response = self.ask_llm(prompt_key, curr_question)
            llm_responses[question_num] = llm_response
        
        return llm_responses

    def summarize_apk(self, questions=QUESTIONS):
        for func_obj in self.funcs.values():
            prompt_key = func_obj.get_prompt_key()
            llm_responses = self.summarize_func(prompt_key, questions)

            for question_num, llm_response in llm_responses.items():
                func_obj.save_response(question_num, questions[question_num]["questions"], llm_response)
                print("Response received!")
                func_obj.analyze_response(question_num, questions[question_num]["answers"])
                print("Response analyzed!")

    def save_as_json(self, json_dir):
        output = {func_name: {"code": func_obj.code, "results": func_obj.results} for func_name, func_obj in self.funcs.items()}

        with open(json_dir, "w") as outfile:
            json.dump(output, outfile, indent=2)
    
    def save_as_text(self, text_dir, apk_name):
        app_title = f"===================={apk_name}===================="
        text = f"{app_title}\n\n"
        for func_name, func_obj in self.funcs.items():
            header = f"--------------------{func_name}--------------------"
            code = func_obj.code
            response = ""
            for question_num in QUESTIONS:
                results = func_obj.results[question_num]
                print(results)
                response += f"Question {question_num}: {results['question']}\nResponse: {results['response']}\n\n"
                print(response)
            text += f"{header}\n{code}\n\n{response}\n\n"
        
        with open(text_dir + ".txt", "w") as outfile:
            outfile.write(text)
            outfile.close()


class APK_Recurse(APK):
    def read_data_from_file(self, apk_path):
        # TODO: Need to work on processing data from DJ's directory
        with open(apk_path, "r") as infile:
            apk_data = json.load(infile)
            
        self.funcs = apk_data['functions'] 
        print(f"APK functions: {self.funcs}")

    def summarize_apk(self):
        self.results = {}

        for ep_name, ep_data in self.funcs.items():
            if "Entry-point: " not in ep_name:
                print("Not an entry point function, skipping...")
                continue
            
            func_name = self.get_func_name_from_entry_point(ep_name)
            code = ep_data["code"]
            print("Summarizing entry point:", ep_name)

            children = ep_data.get("children", [])
            summarized_callees = {}

            for child in children:
                print(f"The parent function of the current child is: {self.funcs[child]['parent']}")
                
                if child in self.funcs.keys() and self.funcs[child]["parent"] == ep_name:
                    child_code = self.funcs[child]["code"]
                    if child_code == "    None":
                        print("Child function code is None, skipping...")
                        continue

                    # Send request to LLM to summarize child function
                    child_summary = self.summarize_func(child_code)
                    print("Summarized child function:", child_summary)
                    summarized_callees[child] = child_summary
                else:
                    print("Child function not found:", child)

            # There is at least 1 entry in summarized_callees
            if len(summarized_callees) > 1:
                summary_list = list(summarized_callees.values()) # grab the summaries from the list of child functions
                collective_child_summaries = " ".join(summary_list) + "\n[INST]Based on the previous child function summaries, summarize the following code for the parent function:[/INST]\n"
                summary = self.summarize_func(collective_child_summaries + code)
                print("Summarized entry point function:", summary)
            # There's no valid children to work with, but at least we have the code
            elif code:
                summarized_callees = {"None", "No children functions found, no summary generated."}
                summary = self.summarize_func(code)
                print(f"Entry point function code: {code}")
                print("Summarized entry point function:", summary)
            # No children, no code
            else:
                summarized_callees = {"None": "No children functions found, no summary generated."}
                summary = "Entry point function not found."
                print("Entry point function not found:", func_name)
                
            self.results[ep_name] = {"entry_point name": func_name, "code": code, "summary": summary, "children": summarized_callees}

    def save_as_text(self, text_dir, apk_name):
        app_title = f"===================={apk_name}===================="
        text = f"{app_title}\n\n"
        for entry_point, ep_data in self.results.items():
            print("Entry point data:", ep_data)
            header = f"--------------------{ep_data['entry_point name']}--------------------"
            code = ep_data["code"]
            entry_point_response = 'Response: ' + ep_data["summary"]
            child_summary = ""
            if len(ep_data["children"]) > 1:
                child_responses = f"Child Function: {ep_data['children']}"
            else:
                for child_function_name, child_summary in ep_data["children"]:
                    child_responses += f"Child Function {child_function_name}:\n{child_summary}\n\n"
            text += f"{header}\n{code}\n\n{entry_point_response}\n{child_responses}\n\n"
        
        with open(text_dir + "_recurse.txt", "w") as outfile:
            outfile.write(text)
            outfile.close()


if __name__ == "__main__":
    for apk_filename in os.listdir(RECURSE_DIR):
        print("Processing APK:", apk_filename)
        curr_apk = APK_Recurse()

        curr_apk.read_data_from_file(RECURSE_DIR + apk_filename) 
        curr_apk.summarize_apk()
        
        print("Parsing complete!\n")
        print(f"Results: {curr_apk.results}")
        print("Saving output...")
        curr_apk.save_as_text(OUTPUT_DIR + apk_filename, apk_filename)
        print(f"Output saved at {OUTPUT_DIR + apk_filename}!")



