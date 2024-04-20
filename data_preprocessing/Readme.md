This repo contains all my work on data_processing part. It includes an androguard script which utilize pyhton lib androguard to generate a callgraph output from an apk file.
In this script, we also added UID for each methods in our callgraph in order to easier locate them in recursive summary process. This callgarph will only contain non-library 
methods in an apk file and each method will have a depth value to denote which layer it is on in our callgraph. And for treesitter python script, it used a python lib called tree-sitter
, which is able to help us find one method's function body according to its name. So in this script we first use Androguard lib to get a callgraph and use treesitter
to find their according function bodies in source code files and put them in our output json file. call_graph_output.json is our generated sample json file.
