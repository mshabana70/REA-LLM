import requests
from data import Data

HOST = "localhost"
PORT = "8000"

headers = {
    "Content-Type": "application/json",
}

INSTRUCTION_KEY = "[INST]Analyze the following script of code that will be presented to you between [CODE] and [/CODE] tags and answer the accompanying question.[/INST]\n"

# Build a ingress pipeline for APK decompiled code

# Break the program down to functions

# Create json of functions with array of questions/answers

# Function name as key, dictionary as value
# Dictionary has "function" as key and function decompiled code as value.
# Dictionary has "questions" as key and array of questions and answers as values (2d array possibly?).

# Parse through Json for each function key, pass function decompiled code and first question to model in prompt key.
# Compare the json answer with the response generated from the model.

# Restructure prompt key with functions pulled from data ingress pipeline

response_dict = {}
# This is the input json that will be passed to the model
model_data = Data()
model_data.open_json("/scratch/ms9761/rea-llm/codellama/inputs/test.json")
#print(data.get_data())
model_data.preprocess()

# Iterate through function and question dictionary
for function_num in model_data.inputs.keys():
    function = model_data.inputs[function_num]['code']
    questions = model_data.inputs[function_num]['questions']
    response_dict[function_num] = {'code': function, 'results': []}

    # Construct prompt key with function code
    PROMPT_KEY = f"[CODE]\n{function}\n[/CODE]\n"

    # Iterate through questions for each function
    for question_num in questions:
        current_question = questions[question_num]['question']
        full_prompt = INSTRUCTION_KEY + PROMPT_KEY + '\n' + current_question
        print(full_prompt)
        data = {
            'inputs': full_prompt,
            'parameters': {
                'max_new_tokens': 2000,
            },
        }

        response = requests.post(f'http://{HOST}:{PORT}/generate', headers=headers, json=data)
        print(response.json())
        response_dict[function_num]['results'].append({f'question_{question_num}': current_question, 'response': response.json()['generated_text']})
        print(response_dict)

        # Need to do a comparison of the response with the answer in the json file
        answers = questions[question_num]['answers']
        curr_idx = int(question_num) - 1
        response_dict[function_num]['results'][curr_idx]['answers'] = []
        for answer_num in answers.keys():
            print(answer_num)

            if answers[answer_num] in response_dict[function_num]['results'][curr_idx]['response']:
                print("Correct!")
                response_dict[function_num]['results'][curr_idx]['answers'].append({'test' : answers[answer_num], 'success': True})
            else:
                print("Incorrect!")
                print(f"Correct answer: {answers[answer_num]}")
                print(f"Your answer: {response_dict[function_num]['results'][curr_idx]['response']}")
                response_dict[function_num]['results'][curr_idx]['answers'].append({'test' : answers[answer_num], 'success': False})
            print(response_dict)

# This will be returned to an output json file for analysis (or output a nicely formatted html page with the results of the inference for one APK)
print(response_dict)

# Write the output json file
model_data.set_outputs(response_dict)
model_data.save_json("/scratch/ms9761/rea-llm/codellama/outputs/test_output.json")
