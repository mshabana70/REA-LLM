import os
import xml.etree.ElementTree as ET
import re
import json

BASE = '/scratch/ds6934/APK_Test_DC/maltest/'
Target = ""
OUTPUT_FOLDER = "./"
all_path = "all_apks.txt"

def folder_path(target):
    return BASE + target

def get_target():
    with open (all_path,'r') as fin:
        target = fin.readlines()
        cleaned_list = [item.strip("\n") for item in target]
        return cleaned_list

def find_main_activity(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    for activity in root.iter('activity'):
        print(activity.iter('intent-filter'))
        if list(activity.iter('intent-filter')):
            print(list(activity.iter('intent-filter')))
            for intent_filter in activity.iter('intent-filter'):
                print(intent_filter)
                action = intent_filter.find("action")
                category = intent_filter.find("category")
                print(action, category)
                print(action.get('{http://schemas.android.com/apk/res/android}name'))
                print(category.get('{http://schemas.android.com/apk/res/android}name'))
                if action is not None and category is not None:
                    if (action.get('{http://schemas.android.com/apk/res/android}name') == "android.intent.action.MAIN" or category.get('{http://schemas.android.com/apk/res/android}name') == "android.intent.category.LAUNCHER"):
                        return activity.get('{http://schemas.android.com/apk/res/android}name')
        else:
            print("hello2")
            return activity.get('{http://schemas.android.com/apk/res/android}name')


    return "Main activity not found"


def open_file(path):
    if not path.endswith("/"):
        path += "/"
    res_folder = path + 'resources/'
    file_path = res_folder + 'AndroidManifest.xml'
    main_activity = find_main_activity(file_path)
    path_to_sources = 'sources/' + "/".join(main_activity.split(".")) + '.java'
    print(path_to_sources)
    return path_to_sources

def parse_java_file(file_path):
    with open(file_path, 'r') as file:
        java_code = file.read()

    method_pattern = r'(?:public|private|protected)\s+\w+\s+\w+\(.*?\)\s*\{(?:\{[^}]*\}|[^}])*}'
    methods = re.findall(method_pattern, java_code, re.DOTALL)
    for method in methods:
        print(method)
    return java_code,methods
    

def open_sources(target_path,apk):
    raw,funcs = parse_java_file(target_path)
    # Constructing the data structure for JSON
    data = {
        "raw": raw,
        "functions": funcs
    }
    output = OUTPUT_FOLDER + apk + '.json'
    # Writing the data to a JSON file
    with open(output, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def OutPut(target):
    base_path = folder_path(target)
    if not base_path.endswith("/"):
        base_path += "/"
    activity_java = open_file(base_path) 
    target_path = base_path + activity_java
    open_sources(target_path,target)


if __name__ == "__main__":
    Target = get_target()
    print("target = " + str(Target))
    for t in Target:
        OutPut(t)
