import os
import json
import matplotlib.pyplot as plt
from jinja2 import Template

def parse_json(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    # Extract relevant information from the JSON data
    # Return a dictionary containing function details and accuracy information
    

def compute_accuracy(model_results):
    # Calculate accuracy for each question and overall accuracy
    # Update the dictionary with accuracy information
    pass

def plot_results(model_results, output_directory):
    # Create visualizations using matplotlib or other plotting libraries
    # Save the plots to the output directory

def process_model_directory(model_directory, output_directory):
    model_results = {}
    for function_file in os.listdir(model_directory):
        if function_file.endswith(".json"):
            function_path = os.path.join(model_directory, function_file)
            function_data = parse_json(function_path)
            function_results = compute_accuracy(function_data)
            model_results[function_file] = function_results

    plot_results(model_results, output_directory)

    return model_results

def generate_html(model_results):
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Model Accuracy Visualization</title>
    </head>
    <body>
        <h1>Model Accuracy Overview</h1>
        {% for model, results in model_results.items() %}
            <h2>{{ model }}</h2>
            {% for function, accuracy in results.items() %}
                <h3>{{ function }}</h3>
                <p>Overall Accuracy: {{ accuracy['overall'] }}</p>
                <!-- Add other accuracy metrics as needed -->
                <img src="{{ accuracy['plot_path'] }}" alt="{{ function }} Plot">
            {% endfor %}
        {% endfor %}
    </body>
    </html>
    """

    template = Template(template_str)
    rendered_html = template.render(model_results=model_results)
    with open("model_accuracy_visualization.html", 'w') as html_file:
        html_file.write(rendered_html)

def main():
    models_directory = "/path/to/models/"
    output_directory = "/path/to/output/"
    all_model_results = {}

    for model_directory in os.listdir(models_directory):
        model_path = os.path.join(models_directory, model_directory)
        if os.path.isdir(model_path):
            model_results = process_model_directory(model_path, output_directory)
            all_model_results[model_directory] = model_results

    generate_html(all_model_results)

if __name__ == "__main__":
    main()
