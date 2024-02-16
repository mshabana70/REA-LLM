import requests
import json
import os
from openai import OpenAI


HOST = "0.0.0.0"
PORT = "8000"
HEADERS = {"Content-Type": "application/json",}

BASE_DIR = "/scratch/ms9761/rea-llm/mistral/"
#BASE_DIR = "C:/Users/mshab/Documents/NYU/Research/LLM/models/codellama/"
QUESTIONS_PATH = BASE_DIR + "inputs/questions.json"
DECOMPILED_CODE_DIR = BASE_DIR + "mal_samples/"  # This would be DJ's scratch folder
OUTPUT_DIR = BASE_DIR + "outputs/"

INSTRUCTION_KEY = "[INST]Analyze the following script of code that will be presented to you between [CODE] and [/CODE] tags and answer the accompanying question.[/INST]\n"
with open(QUESTIONS_PATH, "r") as questions_json:
    QUESTIONS = json.load(questions_json)


class Func:
    def __init__(self, code):
        self.outputs = {"code": code, "results": {}}

    def get_prompt_key(self):
        # TODO: How do we format this?
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

    def save_as_json(self, json_dir):
        output = {func_name: func_obj.outputs for func_name, func_obj in self.funcs.items()}

        with open(json_dir, "w") as outfile:
            json.dump(output, outfile, indent=2)


if __name__ == "__main__":
    # Define OpenAI object
    client = OpenAI(
            api_key = "EMPTY",
            base_url = f"http://{HOST}:{PORT}/v1"
        )



    for apk in os.listdir(DECOMPILED_CODE_DIR):
        print("Processing APK:", apk)
        curr_apk = APK()
        curr_apk.read_data_from_file(DECOMPILED_CODE_DIR + apk)

        for curr_func in curr_apk.funcs.values():
            prompt_key = curr_func.get_prompt_key()

            for question_num in QUESTIONS:
                curr_question = QUESTIONS[question_num]["question"]
                full_prompt = INSTRUCTION_KEY + prompt_key + curr_question

                print("Sending request to server...")

                response = client.chat.completions.create(
                        model='mistralai/Mixtral-8x7B-Instruct-v0.1',
                        messages=[{"role": "user", "content": full_prompt}],
                    )
                curr_func.save_response(question_num, curr_question, response.model_dump_json(indent=4))
                print("Response received!")

                curr_func.analyze_response(question_num, QUESTIONS[question_num]["answers"])
                print("Response analyzed!")

        print("Saving output...")
        curr_apk.save_as_json(OUTPUT_DIR + apk)
        print(f"Output saved at {OUTPUT_DIR + apk}!")



