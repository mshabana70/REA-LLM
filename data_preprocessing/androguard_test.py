from androguard.misc import AnalyzeAPK
import networkx as nx
import json
from treesitter import find_function_body
import os
import time
import re

apk_path = "Demo.apk"
root_dir = "./intermediate/Demo/sources/"

apk, dex, dx = AnalyzeAPK(apk_path)

call_graph = dx.get_call_graph()

manifest = apk.get_android_manifest_xml()

global_counter = 0

outdata = {
    'Raw': [],
    'Functions': []
}
def is_library_class(class_name):
    library_prefixes = ("Ljava", "Landroid","Lcom")
    return any(class_name.startswith(prefix) for prefix in library_prefixes)


# Process each activity

# print(root_nodes)
# Traverse from each root


# def find_node_by_access_flag(call_graph, target):
#     parts = target.split('->')
#     classname, remainder = parts[0], parts[1]
#     methodname, descriptor = remainder.split('(')
#     descriptor = f'({descriptor}'
#
#     # 'call_graph' is your DiGraph object containing all the nodes
#     for node in call_graph.nodes:
#         node_data = call_graph.nodes[node]
#
#         # Match the node based on methodname, descriptor, and classname
#         if (node_data.get('methodname') == methodname and
#                 node_data.get('descriptor') == descriptor and
#                 node_data.get('classname') == classname):
#
#             print(f"Found node: {node}")
#
#             # If the node has 'accessflags', print them
#             if 'accessflags' in node_data:
#                 print(f"Access flags: {node_data['accessflags']}")
#                 return node
#     else:
#         print("No matching node found.")
#         return None

def dfs(graph, start, visited=None, depth=0):
    global global_counter
    global nodes_list

    if visited is None:
        visited = set()
    visited.add(start)
    output = {
        "Outstr":"",
        "Depth": 0,
        "UID": "",
        "class_name": "",
        "method_name": "",
        "Successors":[]
    }
    for next in graph.successors(start):
        try:
            output["Successors"].append(next.name)
        except:
             output["Successors"].append(next.full_name)
    try:
        classname = start.class_name
        name = start.name
        access_flag_str = start.access_flags_string
        s = "classname = "+str(classname)+"   Is_lib?  " + str(is_library_class(classname))
        # with open('results.txt',"a") as f:
        #     f.write(s)
        #     f.write('\n')

        # print("classname = "+str(classname)+"   Is_lib?  " + str(is_library_class(classname)))
        if is_library_class(classname) or name == '<init>':
            return visited


        output["Outstr"] = "Depth " + str(depth) + " UID: " + str(global_counter) + " Class name = " + str(classname) + " Method name = " + str(name) + " Access = " + str(access_flag_str)
        output["Depth"] = str(depth)
        output["UID"] = str(global_counter)
        output["class_name"] = str(classname)
        output["method_name"] = str(name)
        nodes_list.append(start)
        global_counter += 1
        # if len(set(graph.successors(start)) - visited) == 0:
        #     outstr += "        Successors: "
        # else:
        #     succ_list = []
        #     succ = graph.successors(start)
        #     for s in succ:
        #         try:
        #             succ_list.append(s.name)
        #         except:
        #             succ_list.append(s.full_name)

        #     outstr += "        Successors: "  + str(succ_list)
        outdata['Raw'].append(output)
    except:

        pass
   
    
    for next in set(graph.successors(start)) - visited:
        dfs(graph, next, visited, depth + 1)

    #nodes_list.append(start)
    return visited

# Traverse from each root node



def print_method_body(class_name, method_name):
    # Search across all classes
    for method in dex.get_methods():
        if method.class_name == class_name and method_name in method.name:
            print(f"Method found: {method.name}")
            print(f"Class: {method.class_name}")
            print(f"Access Flags: {method.access_flags_string()}")

            # Retrieve and print the method's bytecode
            code = method.get_code()
            if code:
                print("Bytecode:")
                bytecode = code.get_bc()
                for ins in bytecode.get_instructions():
                    print(ins.get_name(), ins.get_output())

                print("\nReadable Form:")
                for i in code.get_instructions():
                    print(i.get_name(), i.get_output())
            else:
                print("No code available for this method.")
            break
    else:
        print("Method not found.")

def find_java_file(root_dir,class_path):
    rel_path = class_path [1:-1].replace('/',os.sep) + ".java"
    file_path = root_dir + rel_path
    try:
        with open(file_path ,'r') as file:
            content = file.read()
            return content
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None   

# Define a function to extract the depth value from a string
def extract_depth(string):
    pattern = r"Depth (\d+)"
    match = re.search(pattern, string)
    if match:
        return int(match.group(1))
    else:
        return None

# Define a function to extract "Successors" information from a string
def extract_successors(string):
    pattern = r"Successors:\s+(\[.*?\])"  # Pattern to match the Successors list
    match = re.search(pattern, string)
    if match:
        successors_str = match.group(1)  # Extract the Successors list as a string
        successors_list = re.findall(r"'(.*?)'", successors_str)  # Extract items within quotes as list elements
        return successors_list
    else:
        return None  # Return None if Successors information is not found


if __name__ == '__main__':
  

    activities = apk.get_activities()
    print("Activities:", activities)

    # Services (background execution entry points)
    services = apk.get_services()
    print("Services:", services)

    # Broadcast Receivers (event listeners entry points)
    receivers = apk.get_receivers()
    print("Broadcast Receivers:", receivers)

    # Content Providers (data management entry points)
    providers = apk.get_providers()
    print("Content Providers:", providers)

    method_lists = []
    nodes_list = []

    for node, deg in call_graph.in_degree():
        print(node.class_name)
        state = is_library_class(node.class_name)
        
        if deg == 0 and not state and node.name != '<init>':
            method_lists.append(node)
    # for activity in activities:
    #     class_descriptor = 'L' + activity.replace('.', '/') + ';'
    #     class_analysis = dx.get_class_analysis(class_descriptor)
    #     if class_analysis:
    #         for method_analysis in class_analysis.get_methods():

    #             #   exclude all lib methodes
    #             method = method_analysis.get_method()
    #             if not is_library_class(method.class_name):
    #                 method_lists.append(method)
    #                 print_method_body(method.class_name, method.name)

    # Sort the list of strings based on the extracted depth value

    for root in method_lists:
        #s = f"Branch starting from {root}: \n"
        #print(f"Zero degree node: {root}")
        #outdata['Raw'].append(s)
        dfs(call_graph, root)


    sorted_methods = sorted(outdata['Raw'], key=lambda x: -extract_depth(x['Outstr']) if extract_depth(x['Outstr']) is not None else float('-inf'))
    outdata['Raw'] = sorted_methods

    successors_lists = [] 

    for i in range(0,len(nodes_list)):
        content = find_java_file(root_dir, nodes_list[i].class_name)
        if content != None:
            func_body = find_function_body(content,nodes_list[i].name)
            if func_body != None:
                #func_info = "UID = " + str(i) + " Name = " + str(nodes_list[i].name)+" Class_name = "+ str(nodes_list[i].class_name) + "\n" + str(func_body)
                func_info = {
                    "UID": str(i),
                    "method_name": str(nodes_list[i].name),
                    "class_name": str(nodes_list[i].class_name),
                    "code": str(func_body),
                    "summary": "",
                    "ground_truth": ""
                }
            else:
                #func_info = "UID = " + str(i) + " Name = " + str(nodes_list[i].name)+" Class_name = "+ str(nodes_list[i].class_name) + "\n" + "NOT FOUND"
                func_info = {
                    "UID": str(i),
                    "method_name": str(nodes_list[i].name),
                    "class_name": str(nodes_list[i].class_name),
                    "code": str(func_body),
                    "summary": "",
                    "ground_truth": ""
                }
            outdata["Functions"].append(func_info)

    print("Length of nodes_list = ",len(nodes_list))
    print("Length of outdata = ",len(outdata["Functions"]))
    print("Length of outdata[Raw] = ",len(outdata["Raw"]))

    with open('call_graph_output.json', 'w') as f:
        json.dump(outdata, f, indent=4)
        

