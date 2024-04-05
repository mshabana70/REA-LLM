from tree_sitter import Language, Parser

# Load the Java language grammar. Adjust the path to where you've compiled or downloaded your Java language binary

# Read the Java source code you want to analyze
def find_function_body(source_code, function_name):
    Language.build_library(
    # Store the library in the `build` directory
    "build/my-languages.so",
    # Include one or more languages
    ["./tree-sitter-java"],
    )

    JAVA_LANGUAGE = Language('build/my-languages.so', 'java')

    parser = Parser()
    parser.set_language(JAVA_LANGUAGE)

    encoded_source_code = source_code.encode('utf-8')

    # Parse the source code
    tree = parser.parse(encoded_source_code)
    
    # Function to recursively search for the function declaration
    def search_tree(node):
        if node.type == 'method_declaration':
            # Assuming the function name is stored in an identifier within the method_declaration
            for child in node.children:
                if child.type == 'identifier' and child.text.decode('utf8') == function_name:
                    return node
        # Recurse through all children of the current node
        for child in node.children:
            result = search_tree(child)
            if result:
                return result
        return None
    
    # Search for the function in the root node of the parsed tree
    function_node = search_tree(tree.root_node)
    
    # If the function is found, extract and return its body
    if function_node:
        # Extract the function body. The exact way to do this depends on the tree-sitter-java grammar specifics.
        # This is a simplified example; you might need to adjust it based on the grammar structure.
        body_node = next((child for child in function_node.children if child.type == 'block'), None)
        if body_node:
            start_byte = body_node.start_byte
            end_byte = body_node.end_byte
            return source_code[start_byte:end_byte]
    
    return None
