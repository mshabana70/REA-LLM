import requests
import json
import os
from rouge_score import rouge_scorer

HOST = "localhost"
PORT = "8000"
HEADERS = {"Content-Type": "application/json",}

BASE_DIR = "/scratch/ms9761/rea-llm/codellama/"
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

    def traverse_recursive(self, node, depth=0, max_depth=4):
        long_sum = "\n\nSummarize the following code in one paragraph:\n"
        short_sum = "\n\nSummarize the following code in one sentence:\n"
        # Check if we've reached a depth of 4 levels or if there are fewer than 4 levels of children
        if depth > max_depth:
            return
        
        # Handle recursion
        if 'children' in node and node["summary"] == "":
            print(f"\nCurrent node in traverse_recursive: {node}")
            for child in node["children"]:
                self.traverse_recursive(child, depth + 1)
        
        # Check if we have reached the entry_point node
        if 'entry_point' in node:
            dict_key = "entry_point"
        else:
            dict_key = "function"
        
        #print(f"\n\nCurrent node in traverse_recursive: {node}")
        func_name = self.get_func_name(node[dict_key])
        func_uid = str(node["uid"])
        func_code = self.get_func_code(func_uid)

        # Handle summarization
        # Check if current node has code
        if func_code == None:
            node["summary"] = "No code found for function"
            return
        
        # Craft prompt key using code from current node
        prompt_key = self.get_prompt_key(func_code)

        # Gather summaries from children nodes (if any)
        chd_summaries = ["Given the following summaries:\n\n"]
        if "children" in node:
            for child in node["children"]:
                if len(child["summary"]) > 0 and child["summary"] != "No code found for function" and child["summary"] != "No summary generated for this function":
                    chd_summaries.append(child["summary"])
        
        # Join children node summaries into a single string for current node summary
        # Craft prompt key using code from current node
        prompt_code = self.get_prompt_key(func_code)
        if len(chd_summaries) > 1:
            # If there are more than 10 children nodes, we only take the first 10
            if len(chd_summaries) > 8:
                joined_summaries = " ".join(chd_summaries[:10])
            else:
                joined_summaries = " ".join(chd_summaries)
            prompt_key = joined_summaries + long_sum + prompt_code
        
        # Summarize current node
        print(f"Prompt key for current node {func_name}: {prompt_key}\n\n")
        summary = self.summarize_func(prompt_key, QUESTIONS, one_sum=True)
        if summary == None or len(summary) == 0:
            summary = "No summary generated for this function"
        print(f"Summary for current node {func_name}: {summary}")
        node["summary"] = summary
        return


    def summarize_apk(self):
        self.results = {}

        for ep_data in self.raw:
            # Grab attributes of entry point
            ep_name = ep_data["entry_point"]
            ep_children = ep_data["children"]
            ep_uid = str(ep_data["uid"])
            print("\nSummarizing entry point:", ep_name)
            print("Current entry point UID:", ep_uid)
            
            # Extract function name from entry point string
            func_name = self.get_func_name_from_entry_point(ep_name)

            # Get Entry point code
            code = self.get_func_code(ep_uid)

            # If entry point code is not found, skip
            if code == None:
                print("Entry point code not found, skipping...")
                ep_data["summary"] = "No code found for entry point"
                continue       
            
            # Summarize children functions
            # Run recursive traversal
            if len(ep_children) > 0:
                self.traverse_recursive(ep_data, 0)
            else:
                print("No children to traverse, summarizing entry point function...")
                prompt_key = "\n\nSummarize the following code in one paragraph:\n" + self.get_prompt_key(code)
                print(f"Prompt key for current node {func_name}: {prompt_key}\n\n")
                summary = self.summarize_func(prompt_key, QUESTIONS, one_sum=True)
                ep_data["summary"] = summary
                print(f"Summary of current entry point function {func_name} without children: {ep_data}")
                continue

            # Summarize entry point function
            # Grab all summaries from first level children nodes
            chd_summaries = ["Given the following summaries:\n"]
            for child in ep_children:
                if len(child["summary"]) > 0 and child["summary"] != "No code found for function":
                    print(f"This node has an existing summaries: {child['summary']}")
                    chd_summaries.append(child["summary"])
            
            # Join children node summaries into a single string for current node summary
            prompt_code = self.get_prompt_key(code)
            if len(chd_summaries) > 1:
                joined_summaries = " ".join(chd_summaries)
                prompt_key = joined_summaries + "\nSummarize the following code:\n" + prompt_code

            # Summarize current entry point node
            print(f"Prompt key for current node {func_name}: {prompt_key}\n\n")
            summary = self.summarize_func(prompt_key, QUESTIONS, one_sum=True)
            if summary == None or len(summary) == 0:
                summary = "No summary generated for this function"
            ep_data["summary"] = summary
            print(f"Summary of current entry point function {func_name} and its children: {ep_data}")

    def write_json(self, text_dir):
        output = {"Results": self.raw}

        with open(text_dir + "_recurse_eight.json", "w") as outfile:
            json.dump(output, outfile, indent=2)

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

        print("Summarization complete!\n")
        print("Writing the results...")
        print(curr_apk.write_json(OUTPUT_DIR + apk_filename))
        exit()
        
        print("Parsing complete!\n")
        print(f"Results: {curr_apk.results}")
        print("Saving output...")
        curr_apk.save_as_text(OUTPUT_DIR + apk_filename, apk_filename)
        print(f"Output saved at {OUTPUT_DIR + apk_filename}!")