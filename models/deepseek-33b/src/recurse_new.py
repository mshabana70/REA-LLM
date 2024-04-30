import requests
import json
import os
from rouge_score import rouge_scorer

HOST = "localhost"
PORT = "8000"
HEADERS = {"Content-Type": "application/json",}

BASE_DIR = "/scratch/ms9761/rea-llm/deepseek-33b/"
QUESTIONS_PATH = BASE_DIR + "inputs/questions.json"
DECOMPILED_CODE_DIR = BASE_DIR + "decompiled_code/"  # This would be DJ's scratch folder
OUTPUT_DIR = BASE_DIR + "outputs_text/"
RECURSE_DIR = "/scratch/ms9761/rea-llm/construct_json/app_files/test/"

INSTRUCTION_KEY = "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n\nInstruction: Please analyze the following code and answer the question about the provided code.\n\n"
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
        return f"Input:\n{code}\n\n"

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
        self.count = 0
        self.max_depth = 0

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

        # Check if response is full of newline characters
        # Get count of newline characters
        newline_count = llm_response.count("\n")
        # Get count of characters in response
        char_count = len(llm_response)
        # If the response is full of newline characters, retry
        if newline_count == char_count and self.count < 3:
            print("Empty response received, retrying...")
            self.count += 1
            return self.ask_llm(prompt_key, question)

        # If the response is empty, retry
        if len(llm_response) == 0  and self.count < 3:
            print("Empty response received, retrying...")
            self.count += 1
            return self.ask_llm(prompt_key, question)
        elif len(llm_response) == 0 and self.count == 3:
            print("Empty response received after 3 retries, skipping...")
            return "No summary generated for this function"
        # If the response is not empty and full of newline characters
        elif newline_count == char_count and self.count == 3:
            print("Empty response received after 3 retries, skipping...")
            return "No summary generated for this function"
        print("Response received!")

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

    def read_data_from_file(self, apk_path):
        # TODO: Need to work on processing data from DJ's directory
        with open(apk_path, "r") as infile:
            apk_data = json.load(infile)
        
        self.raw = apk_data['Raw']
        self.funcs = apk_data['Functions']
    
    def get_prompt_key(self, code, sum_length="short", success_sums=None):
        # TODO: How do we format this?
        long_sum = "\n\nSummarize the following code in one paragraph:\n"
        short_sum = "\n\nSummarize the following code in one sentence:\n"
        header = "Given the following summaries of the current code's sucessors:\n"
        if sum_length == "short" and success_sums is not None:
            return f"{header}\n{success_sums}\n{short_sum}\n\nInput:\n{code}\n"
        elif sum_length == "long" and success_sums is not None:
            return f"{header}\n{success_sums}\n{long_sum}\n\nInput:\n{code}\n"
        else:
            return f"{short_sum}\nInput:\n{code}\n\n"

    def get_func_code(self, func_uid):
        for func in self.funcs:
            if func_uid == func["UID"]:
                return func["code"]
        return None
    
    def set_node_summary(self, node_uid, summary):
        for node in self.funcs:
            if node["UID"] == node_uid:
                node["summary"] = summary
                print(f"Summary set for node {node['method_name']}")
                return
        return

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
            
    def summarize_apk(self, apk_name):
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
                prompt_key = self.get_prompt_key(node_code)
                print(f"Prompt key with no successors:\n{prompt_key}")

                # Summarize current node
                summary = self.summarize_func(prompt_key, QUESTIONS, one_sum=True)
                print(f"Summary for current node {node_method}: {summary}")

                # Save summary to current node
                self.set_node_summary(node_uid, summary)
                continue
            else:
                # Traverse children nodes and grab successor summaries
                success_sums = self.traverse_recursive(node)

                # Craft prompt key using successor summaries and code from current node
                prompt_key = self.get_prompt_key(node_code, sum_length="short", success_sums=success_sums)
                print(f"Prompt key with successors:\n{prompt_key}")

                # Summarize current node
                summary = self.summarize_func(prompt_key, QUESTIONS, one_sum=True)
                print(f"Summary for current node {node_method}: {summary}")

                # Save summary to current node
                self.set_node_summary(node_uid, summary)
            
            self.write_json(OUTPUT_DIR + apk_name)
        
        print("Summarization complete!")

    def write_json(self, text_dir):
        output = {"Results": self.funcs}

        with open(text_dir + "_topo.json", "w") as outfile:
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

    def evaluate_rouge(self):
        # Initialize RougeScorer
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
        scores = {}

        # Parse completed summaries
        for node in self.funcs:
            summary = node["summary"]
            ground_truth = node["ground_truth"]

            # Calculate scores for each entry point
            if ground_truth != "" and summary != "" and summary != "No summary generated for this function":
                score_result = scorer.score(ground_truth, summary)
                rouge1_score = score_result["rouge1"][0]
                rougeL_score = score_result["rougeL"][0]
                scores[node["UID"]] = {"rouge1": rouge1_score, "rougeL": rougeL_score}

                # Print scores
                print(f"Scores for {node['method_name']} at {node['UID']}:\n{scores[node['UID']]}")

                # Save scores to node
                node["scores"] = scores[node['UID']]
            else:
                print(f"Skipping {node['method_name']} at {node['UID']}")
                node["scores"] = None
                continue
        
        # Calculate average scores
        avg_scores = {}
        for score in scores.values():
            for key, value in score.items():
                if key not in avg_scores:
                    avg_scores[key] = value
                else:
                    avg_scores[key] += value
            
        for key in avg_scores.keys():
            avg_scores[key] = avg_scores[key] / len(scores)
        
        print(f"Average scores across {len(scores)} nodes for APK:\nRouge1 Avg Score {avg_scores['rouge1']}\nRougeL Avg Score {avg_scores['rougeL']}")
        return scores
            


if __name__ == "__main__":
    for apk_filename in os.listdir(RECURSE_DIR):
        print("Processing APK:", apk_filename)
        curr_apk = APK_Recurse()

        print("\nReading data from file...")
        curr_apk.read_data_from_file(RECURSE_DIR + apk_filename)

        print("\nSummarizing APK...")
        curr_apk.summarize_apk(apk_filename)

        print("Summarization complete!\n")

        print("Evaluating results...")
        scores = curr_apk.evaluate_rouge()

        print("Writing the results...")
        print(curr_apk.write_json(OUTPUT_DIR + apk_filename))
        exit()
        
        print("Parsing complete!\n")
        print(f"Results: {curr_apk.results}")
        print("Saving output...")
        curr_apk.save_as_text(OUTPUT_DIR + apk_filename, apk_filename)
        print(f"Output saved at {OUTPUT_DIR + apk_filename}!")