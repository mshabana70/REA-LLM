import requests
import json
import os


HOST = "localhost"
PORT = "8000"
HEADERS = {"Content-Type": "application/json",}

BASE_DIR = "/scratch/ms9761/rea-llm/deepseek/"
#BASE_DIR = "C:/Users/mshab/Documents/NYU/Research/LLM/models/codellama/"
QUESTIONS_PATH = BASE_DIR + "inputs/questions.json"
DECOMPILED_CODE_DIR = BASE_DIR + "decompiled_code/"  # This would be DJ's scratch folder
OUTPUT_DIR = BASE_DIR + "outputs_text/"

INSTRUCTION_KEY = "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n\nInstruction: Please analyze the following code and answer the question about the provided code.\n\n"
with open(QUESTIONS_PATH, "r") as questions_json:
    QUESTIONS = json.load(questions_json)


class Func:
    def __init__(self, code):
        self.outputs = {"code": code, "results": {}}

    def get_prompt_key(self):
        # TODO: How do we format this?
        code = self.outputs["code"]
        return f"Input:\n{code}\n\n"

    def save_response(self, question_num, question, response):
        self.outputs["results"][question_num] = {"question": question, "response": response, "answers": {}}
    
    def analyze_response(self, question_num, answers):
        response = self.outputs["results"][question_num]["response"]
        for idx in range(1, len(answers) + 1):
            self.outputs["results"][question_num]["answers"][answers[str(idx)]] = answers[str(idx)].lower() in response


class APK:
    def __init__(self):
        self.funcs = {}
        self.raw = None

    def get_func_name(self, func_num):
        return f"Function_{func_num}"

    def read_data_from_file(self, apk_dir):
        # TODO: Need to work on processing data from DJ's directory
        with open(apk_dir, "r") as infile:
            apk_data = json.load(infile)
            self.raw = apk_data['raw'] # This is the raw code from each apk json (too large for input)
            apk_functions = apk_data['functions'] # This is a list of the functions from each apk json
            for func_num, function in enumerate(apk_functions):
                print(f"Processing function {func_num + 1}, which looks like this: {function}")
                func_name = self.get_func_name(func_num + 1)
                self.funcs[func_name] = Func(function)

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
    for apk in os.listdir(DECOMPILED_CODE_DIR):
        print("Processing APK:", apk)
        curr_apk = APK()
        curr_apk.read_data_from_file(DECOMPILED_CODE_DIR + apk)

        for curr_func in curr_apk.funcs.values():
            prompt_key = curr_func.get_prompt_key()

            for question_num in QUESTIONS:
                curr_question = QUESTIONS[question_num]["question"]
                full_prompt = INSTRUCTION_KEY + prompt_key + curr_question
                data = {
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": 1000,
                    },
                }

                print("Sending request to server...")

                response = requests.post(f"http://{HOST}:{PORT}/generate", headers=HEADERS, json=data)
                curr_func.save_response(question_num, curr_question, response.json()["generated_text"])
                print("Response received!")

                curr_func.analyze_response(question_num, QUESTIONS[question_num]["answers"])
                print("Response analyzed!")

        print("Saving output...")
        curr_apk.save_as_text(OUTPUT_DIR + apk, apk)
        print(f"Output saved at {OUTPUT_DIR + apk}!")



