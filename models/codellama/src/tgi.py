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
OUTPUT_DIR = BASE_DIR + "outputs/"

INSTRUCTION_KEY = "[INST]Analyze the following script of code that will be presented to you between [CODE] and [/CODE] tags and answer the accompanying question.[/INST]\n"
with open(QUESTIONS_PATH, "r") as questions_json:
    QUESTIONS = json.load(questions_json)

MAX_TOKEN_SIZE = 2000


class Func:
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.results = {}
        self.length = len(code)

    def get_prompt_key(self):
        return f"[CODE]\n{self.code}\n[/CODE]\n\n"

    def save_response(self, question_num, question, response):
        self.results[question_num] = {"question": question, "response": response, "answers": {}}
    
    def analyze_response(self, question_num, answers):
        response = self.results[question_num]["response"]
        for idx in range(1, len(answers) + 1):
            self.results[question_num]["answers"][answers[str(idx)]] = answers[str(idx)].lower() in response.lower()
    
    def format_for_output(self):
        return {"code": self.code, "results": self.results}


class APK:
    def __init__(self):
        self.funcs = []
        self.raw = None

    def get_func_name(self, func_num_start, func_num_end=None):
        if func_num_end is None:
            return f"Function_{func_num_start}"
        return f"Function_{func_num_start}-{func_num_end}"

    def read_data_from_json(self, input_path):
        with open(input_path, "r") as infile:
            apk_data = json.load(infile)

        self.raw = apk_data['raw']  # This is the raw code from each apk json (too large for input)
        apk_functions = apk_data['functions']  # This is a list of the functions from each apk json

        for func_num, code in enumerate(apk_functions):
            self.funcs.append(Func(name=self.get_func_name(func_num), code=code))
        
        # Sliding window
        num_funcs = len(self.funcs)
        start, end = 0, 0
        total_length = 0
        code = ""
        num_newlines = 2

        while end < num_funcs:
            total_length += self.funcs[end].length + num_newlines
            code += self.funcs[end].code + "\n" * num_newlines

            while total_length > MAX_TOKEN_SIZE and start < end:
                total_length -= self.funcs[start].length + num_newlines
                code = code[self.funcs[start].length + num_newlines:]
                start += 1

            while end < num_funcs - 1 and total_length + self.funcs[end + 1].length + num_newlines <= MAX_TOKEN_SIZE:
                end += 1
                total_length += self.funcs[end].length + num_newlines
                code += self.funcs[end].code + "\n" * num_newlines

            if total_length <= MAX_TOKEN_SIZE and start != end:
                self.funcs.append(Func(name=self.get_func_name(start, end), code=code))

            end += 1

    def save_as_json(self, output_path):
        output = {func_obj.name: func_obj.format_for_output() for func_obj in self.funcs}

        with open(output_path, "w+") as outfile:
            json.dump(output, outfile, indent=2)


if __name__ == "__main__":
    for apk_name in os.listdir(DECOMPILED_CODE_DIR):
        print("Processing APK:", apk_name)
        curr_apk = APK()
        curr_apk.read_data_from_json(input_path=DECOMPILED_CODE_DIR + apk_name)

        for curr_func in curr_apk.funcs:
            prompt_key = curr_func.get_prompt_key()

            for question_num in QUESTIONS:
                curr_question = QUESTIONS[question_num]["question"]
                full_prompt = INSTRUCTION_KEY + prompt_key + curr_question
                data = {
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": 2000,
                    },
                }

                print("Sending request to server...")
                response = requests.post(f"http://{HOST}:{PORT}/generate", headers=HEADERS, json=data)
                curr_func.save_response(question_num, curr_question, response.json()["generated_text"])
                print("Response received!")

                curr_func.analyze_response(question_num, QUESTIONS[question_num]["answers"])
                print("Response analyzed!")

        print("Saving output...")
        curr_apk.save_as_json(output_path=OUTPUT_DIR + apk_name)
        print(f"Output saved at {OUTPUT_DIR + apk_name}!")
