import requests
import json
import os
from rouge_score import rouge_scorer

HOST = "localhost"
PORT = "8000"
HEADERS = {"Content-Type": "application/json",}

BASE_DIR = "/scratch/ms9761/rea-llm/deepseek/"
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
        self.raw = []
        self.funcs = {}

    def get_func_name(self, func_num):
        return f"Function_{func_num}"
    
    def get_func_name_from_entry_point(self, entry_point):
        """Implement logic to extract function name from entry point string"""
        # For example, if entry point is "<androidx.fragment.app.FragmentActivity: void <init>()>",
        # the function name would be "void <init>()"
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

    def summarize_func(self, prompt_key, questions, one_sum=False):
        llm_responses = {}

        for question_num in questions.keys():
            curr_question = questions[question_num]["question"]
            llm_response = self.ask_llm(prompt_key, curr_question)
            if one_sum == False:
                llm_responses[question_num] = llm_response
            else:
                return llm_response
        
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
    def preprocess_callgraph(self):

        return 0
    def read_data_from_file(self, apk_path):
        # TODO: Need to work on processing data from DJ's directory
        with open(apk_path, "r") as infile:
            apk_data = json.load(infile)
        
        self.raw = apk_data['raw']
        self.funcs = apk_data['functions']
    
    def get_prompt_key(self, code):
        # TODO: How do we format this?
        return f"[CODE]\n{code}\n[/CODE]\n\n"

    def get_func_code(self, func_uid):
        for func in self.funcs:
            if func.startswith(f"{func_uid}_"):
                return func
        return None

    def traverse_recursive(self, node, current_level=1):
         # Check if we've reached a depth of 4 levels or if there are fewer than 4 levels of children
        if current_level >= 4 or ("children" in node and not node["children"]):  
            # Perform the action (e.g., execute the function)
            func_name = self.get_func_name(node["function"])
            func_uid = str(node["uid"])
            func_code = self.get_func_code(func_uid)
            if func_code == None:
                print("Function code not found, skipping...")
                return

            print(f"Executing function: {func_name}")
            prompt_key = self.get_prompt_key(func_code)

            # Gather summaries from children nodes
            chd_summaries = []
            if "children" in node:
                for child in node["children"]:
                    if len(child["summary"]) > 0:
                        chd_summaries.append(child["summary"])

            joined_summaries = " ".join(chd_summaries)
            prompt_key += "\n" + joined_summaries
            summary = self.summarize_func(prompt_key, QUESTIONS, one_sum=True)
            node["summary"] = summary
            return

        if "children" in node:
            for child in node["children"]:
                self.traverse_recursive(child, current_level + 1)

    def summarize_apk(self):
        self.results = {}

        # Entry point 1
        # level 1 invoke, level 2, level 3, level 4, level 4, level 3, level 4, level 4 (start summarizing
        # use level 4 summary to summarize level 3
        # repeat for level 2 and level 1 => we have a summary for level 1
        # repeat the process till we reach level 4 or the highest level for that level 1 invoke
        # do that for all level 1s
        # use all level 1s to summarixe the entry point
        for ep_data in self.raw:

            # Grab attributes of entry point
            ep_name = ep_data["entry_point"]
            ep_children = ep_data["children"]
            ep_uid = str(ep_data["uid"])
            print("Summarizing entry point:", ep_name)
            print("Current entry point UID:", ep_uid)
            
            # Extract function name from entry point string
            func_name = self.get_func_name_from_entry_point(ep_name)
            print(f"Function name: {func_name}")

            # Get Entry point code
            print("Searching for entry point code...")
            code = self.get_func_code(ep_uid)

            # If entry point code is not found, skip
            if code == None:
                print("Entry point code not found, skipping...")
                continue
            else:
                print("Entry point code found!")
                print("Entry point code:", code)          
            
            # Summarize children functions
            # for child in ep_children:
            #     func_name = child["function"]
            #     func_uid = str(child["uid"])
            #     func_code = self.get_func_code(func_uid)

            #     if func_code == None:
            #         print("Child function code not found, skipping...")
            #         continue
                
            # Run recursive traversal
            print("Traversing children...")
            print("Current children count:", len(ep_children))
            if len(ep_children) > 0:
                print("Traversing children...")
                self.traverse_recursive(ep_data, 1)
            else:
                print("No children to traverse, skipping...")
                print("Summarizing entry point function...")
                continue

            # Summarize entry point function
            print(f"The following is the summaries of the children for the entry point function {func_name}: {self.summaries}")

        # for ep_name, ep_data in self.funcs.items():
        #     if "Entry-point: " not in ep_name:
        #         print("Not an entry point function, skipping...")
        #         continue
            
        #     func_name = self.get_func_name_from_entry_point(ep_name)
        #     code = ep_data["code"]
        #     print("Summarizing entry point:", ep_name)

        #     children = ep_data.get("children", [])
        #     summarized_callees = {}

        #     for child in children:
        #         print(f"The parent function of the current child is: {self.funcs[child]['parent']}")
                
        #         if child in self.funcs.keys() and self.funcs[child]["parent"] == ep_name:
        #             child_code = self.funcs[child]["code"]
        #             if child_code == "    None":
        #                 print("Child function code is None, skipping...")
        #                 continue

        #             # Send request to LLM to summarize child function
        #             child_summary = self.summarize_func(child_code, QUESTIONS, one_sum=True)
        #             print("Summarized child function:", child_summary)
        #             summarized_callees[child] = child_summary
        #         else:
        #             print("Child function not found:", child)

        #     # There is at least 1 entry in summarized_callees
        #     if len(summarized_callees) > 1:
        #         print(f"\n\nSummarized callee dict: {summarized_callees}")
        #         summary_list = list(summarized_callees.values()) # grab the summaries from the list of child functions
        #         print(f"\n\nSummarized callee list: {summary_list}")
        #         collective_child_summaries = " ".join(summary_list) + "\n[INST]Based on the previous child function summaries, summarize the following code for the parent function:[/INST]\n"
        #         summary = self.summarize_func(collective_child_summaries + code, QUESTIONS, one_sum=True)
        #         print("Summarized entry point function:", summary)
        #     # There's no valid children to work with, but at least we have the code
        #     elif code:
        #         summarized_callees = {"None": "No children functions found, no summary generated."}
        #         summary = self.summarize_func(code, QUESTIONS, one_sum=True)
        #         print(f"Entry point function code: {code}")
        #         print("Summarized entry point function:", summary)
        #     # No children, no code
        #     else:
        #         summarized_callees = {"None": "No children functions found, no summary generated."}
        #         summary = "Entry point function not found."
        #         print("Entry point function not found:", func_name)
                
        #     self.results[ep_name] = {"entry_point name": func_name, "code": code, "summary": summary, "children": summarized_callees}

    def save_as_text(self, text_dir, apk_name):
        app_title = f"===================={apk_name}===================="
        text = f"{app_title}\n\n"
        for entry_point, ep_data in self.results.items():
            print("Entry point data:", ep_data)
            header = f"--------------------{ep_data['entry_point name']}--------------------"
            code = ep_data["code"]
            entry_point_response = 'Response: ' + ep_data["summary"]
            child_summary = ""
            child_responses = ""
            if len(ep_data["children"]) > 1:
                print(f"Trying to print Summarized callee dict: {ep_data['children']}")
                for child_function_name, child_summary in ep_data["children"].items():
                    child_responses += f"\nChild Function {child_function_name}:\n{child_summary}\n\n"
            else:
                child_responses = f"\nChild Function None: No children functions found, no summary generated\n\n"
            text += f"{header}\n{code}\n\n{entry_point_response}\n{child_responses}\n\n"
        
        with open(text_dir + "_recurse.txt", "w") as outfile:
            outfile.write(text)
            outfile.close()

class Evaluation(APK_Recurse):

    def evaluate(self):
        # Initialize RougeScorer
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
        scores = {}

        # Grab reference summaries
        reference_summaries = [QUESTIONS[question_num]["answers"]["1"] for question_num in QUESTIONS.keys()]

        # Calculate scores for each entry point
        for entry_point, ep_data in self.results.items():
            summary = ep_data["summary"]
            scores[entry_point] = scorer.score(reference_summaries, summary)
        
        return scores


if __name__ == "__main__":
    for apk_filename in os.listdir(RECURSE_DIR):
        print("Processing APK:", apk_filename)
        curr_apk = APK_Recurse()

        print("\nReading data from file...")
        curr_apk.read_data_from_file(RECURSE_DIR + apk_filename)

        print("\nSummarizing APK...") 
        curr_apk.summarize_apk()
        exit()
        
        print("Parsing complete!\n")
        print(f"Results: {curr_apk.results}")
        print("Saving output...")
        curr_apk.save_as_text(OUTPUT_DIR + apk_filename, apk_filename)
        print(f"Output saved at {OUTPUT_DIR + apk_filename}!")