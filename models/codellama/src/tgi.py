import requests
import json
import os


HOST = "localhost"
PORT = "8000"
HEADERS = {"Content-Type": "application/json",}

BASE_DIR = "/scratch/ms9761/rea-llm/codellama/"
QUESTIONS_PATH = BASE_DIR + "inputs/questions.json"
DECOMPILED_CODE_DIR = BASE_DIR + "decompiled_code/"  # This would be DJ's scratch folder
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
            self.outputs["results"][question_num]["answers"][answers[str(idx)]] = answers[str(idx)] in response


class APK:
    def __init__(self):
        self.funcs = {}

    def get_func_name(self, func_num):
        return f"Function_{func_num}"

    def read_data_from_dir(self, apk_dir):
        # TODO: Need to work on processing data from DJ's directory
        for func_num, filename in enumerate(os.listdir(apk_dir)):
            with open(apk_dir + filename, "r") as infile:
                func_name = self.get_func_name(func_num + 1)
                self.funcs[func_name] = Func(infile.read())

    def save_as_json(self, json_dir):
        output = {func_name: func_obj.outputs for func_name, func_obj in self.funcs.items()}

        with open(json_dir, "w") as outfile:
            json.dump(output, outfile, indent=2)


if __name__ == "__main__":
    for apk in os.listdir(DECOMPILED_CODE_DIR):
        curr_apk = APK()
        curr_apk.read_data_from_dir(DECOMPILED_CODE_DIR + apk + "/")

        for curr_func in curr_apk.funcs.values():
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

                response = requests.post(f"http://{HOST}:{PORT}/generate", headers=HEADERS, json=data)
                curr_func.save_response(question_num, curr_question, response.json()["generated_text"])
                curr_func.analyze_response(question_num, QUESTIONS[question_num]["answers"])

        curr_apk.save_as_json(OUTPUT_DIR + apk + ".json")



