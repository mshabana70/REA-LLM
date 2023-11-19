import requests
import json


class Data:
    def __init__(self):
        self.data = None
        self.inputs = {}
        self.outputs = {}

    def get_data(self):
        return self.data

    def set_outputs(self, data):
        self.outputs = data

    def get_json(self):
        return json.dumps(self.data)

    def open_json(self, json_path):
        with open(json_path) as json_file:
            self.data = json.load(json_file)

    def save_json(self, json_path):
        with open(json_path, 'w') as json_file:
            json.dump(self.outputs, json_file)

    def preprocess(self):
        """ parse the json file and create a list of inputs """

        # Parsing through each APK in the json file
        for key in self.data.keys():
            #print(key)
            current_apk = self.data[key]

            # Parsing through each code snippet in the APK
            for code_num in current_apk.keys():
                self.inputs[f'function_{code_num}'] = {'code': current_apk[code_num]['code'], 'questions': current_apk[code_num]['questions']}
                #print(self.inputs)


