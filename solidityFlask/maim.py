import os
import subprocess
import re
import openai
import json
from flask import Flask, request, render_template, redirect, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'sol'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_solidity_version(contract_file):
    with open(contract_file, 'r') as file:
        content = file.read()
    match = re.search(r'pragma\s+solidity\s+\^?(\d+\.\d+\.\d+);', content)
    if match:
        return match.group(1)
    else:
        print("Solidity version not found in the contract. Defaulting to version 0.8.0.")
        return "0.8.0"

def use_solidity_version(version):
    print(f"Using solc version: {version}")
    os.system(f"solc-select install {version}")
    os.system(f"solc-select use {version}")

def flatten_contract(contract_file, flattened_file):
    try:
        with open(flattened_file, 'w') as outfile:
            with open(contract_file, 'r') as infile:
                content = infile.read()
                outfile.write(content)
                print(f"Flattened content written to {flattened_file}")
    except Exception as e:
        print(f"Error flattening contract: {e}")

def compile_contract(flattened_file):
    command = f"solc --optimize --bin {flattened_file}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Compilation failed with output:\n{result.stderr}")
        return False
    else:
        print(f"Compilation output:\n{result.stdout}")
    return True

def run_slither(flattened_file):
    try:
        slither_output_file = 'slither_output.json'
        if os.path.exists(slither_output_file):
            os.remove(slither_output_file)
            print("Existing slither_output.json removed.")

        command = f"slither {flattened_file} --json {slither_output_file}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        print(f"Slither command executed: {command}")
        print(f"Slither command output: {result.stdout}")
        if result.returncode != 0:
            print(f"Slither failed with return code {result.returncode}:\n{result.stderr}")
            return False

        if not os.path.exists(slither_output_file):
            print("Slither results file was not created.")
            return False

        with open(slither_output_file, 'r') as f:
            slither_data = f.read().strip()
            print(f"Slither results read from file: {slither_data}")
            if not slither_data:
                print("Slither results file is empty.")
                return False
        return True

    except Exception as e:
        print(f"Error running Slither: {e}")
        return False

def analyze_with_gpt4(flattened_file, slither_results):
    print("Starting GPT-4 analysis...")

    with open(flattened_file, 'r') as file:
        contract_content = file.read()

    system_prompt = (
        "You are an expert in Solidity auditing. Review the given Solidity code for known vulnerabilities, best practices, and spelling errors. "
        "Also review the results from Slither. Provide a JSON output with the following fields:\n"
        "1. issue_name\n2. severity_level\n3. impact_of_the_vulnerability\n4. vulnerable_code_snippet\n5. mitigation_solution"
    )

    user_prompt_correct = "Analyze the following Solidity code and combine it with results from Slither:"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_prompt_correct}\nSolidity Contract:\n{contract_content}\n\nSlither Results:\n{slither_results}\n"}
            ],
            n=1,
            stop=None,
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=10000
        )

        report_json = json.loads(response['choices'][0]['message']['content'].strip())
        print(f"GPT-4 analysis results: {report_json}")
        return report_json
    except Exception as e:
        print(f"Error during GPT-4 analysis: {e}")
        return None

def process_audit(main_contract, uploaded_files):
    results = {"status": "Failed", "results": None}
    try:
        main_contract_path = os.path.join(app.config['UPLOAD_FOLDER'], main_contract)
        flattened_file = os.path.join(app.config['UPLOAD_FOLDER'], 'flattened.sol')
        
        print("Extracting Solidity version...")
        solc_version = extract_solidity_version(main_contract_path)
        if not solc_version:
            print("Failed to extract Solidity version.")
            return results
            
        print(f"Using Solidity version {solc_version}...")
        use_solidity_version(solc_version)
        
        print("Flattening contract...")
        flatten_contract(main_contract_path, flattened_file)
        
        if not os.path.isfile(flattened_file):
            print(f"Flattened file {flattened_file} was not created.")
            return results
        
        print("Compiling contract...")
        if not compile_contract(flattened_file):
            return results
        
        
        
        slither_results = ""
        slither_output_file = "slither_output.json"
        if os.path.exists(slither_output_file):
            try:
                with open(slither_output_file, 'r') as file:
                    slither_results = file.read().strip()
                    print(f"Slither results read from file: {slither_results}")
                    if not slither_results:
                        print("Slither results file is empty after reading.")
                        return results
            except Exception as e:
                print(f"Error reading Slither results: {e}")
                return results
        else:
            print("Slither results file does not exist.")
            return results
        
        print("Analyzing with GPT-4 for comprehensive audit...")
        final_results = analyze_with_gpt4(flattened_file, slither_results)
        if final_results is None:
            print("Failed during GPT-4 analysis.")
            return results
        
        print(f"GPT-4 analysis results processed.")
        
        with open("final_audit_results.json", "w") as outfile:
            json.dump(final_results, outfile, indent=4)

        results["status"] = "Completed"
        results["results"] = final_results

    except Exception as e:
        print(f"Error during processing: {e}")

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'main_contract' not in request.form:
        return redirect(request.url)

    main_contract = request.form['main_contract']

    uploaded_files = []
    for file in request.files.getlist('file'):
        if file and allowed_file(file.filename):
            filename = file.filename  # Avoid using secure_filename since we're not saving user-controlled data
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_files.append((file.filename, file_path))
            print(f"Uploaded file saved to {file_path}")

    if main_contract not in [fname for fname, _ in uploaded_files]:
        print(f"Main contract file {main_contract} does not exist in uploaded files.")
        return jsonify({'status': 'Failed', 'error': f"Main contract file {main_contract} does not exist in uploaded files."}), 400

    # Process the audit synchronously and get the results
    results = process_audit(main_contract, uploaded_files)

    # Save results to allow rendering in the results page
    with open("results.json", "w") as outfile:
        json.dump(results, outfile, indent=4)

    return render_template('result.html', results=results["results"])

if __name__ == '__main__':
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDERER)
    app.run(debug=True)