import requests
import json

# Define the URL and headers
url = "http://127.0.0.1:1234/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}
input_file_path = "token.sol"  # Replace with your file path

try:
    with open(input_file_path, 'r') as file:
        full_text = file.read()
except FileNotFoundError:
    print(f"File not found: {input_file_path}")
    exit(1)


# Prompts for the model
system_prompt = """You are tasked with performing a comprehensive review of a Solidity smart contract. Your goal is to identify any potential security vulnerabilities, business logic flaws, adherence to best practices, and spelling or syntax errors. Provide a detailed report highlighting the identified issues, their severity, and recommended solutions."""
user_prompt_correct = "Analyze the following Solidity code and return a JSON array of vulnerabilities found, with each vulnerability containing severity, description (including file name and line of code), references, and mitigation solution."

# Define the payload
payload = {
    "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "messages": [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"{user_prompt_correct}\n\nCode:\n{full_text}"
        }
    ],
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "vulnerability_response",
            "strict": "true",
            "schema": {
                "type": "object",
                "properties": {
                    "vulnerabilities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "severity": {"type": "string"},
                                "description": {"type": "string"},
                                "references": {"type": "string"},
                                "mitigation": {"type": "string"}
                            },
                            "required": ["severity", "description", "references", "mitigation"]
                        }
                    }
                },
                "required": ["vulnerabilities"]
            }
        }
    },
    "temperature": 0.7,
    "max_tokens": 4000,  # Increase to allow a more detailed response
    "stream": False
}

# Make the request
response = requests.post(url, headers=headers, json=payload)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    response_json = response.json()
    # Extract the vulnerabilities list
    # vulnerabilities = json.loads(response_json['choices'][0]['message']['content'])['vulnerabilities']
    # for vulnerability in vulnerabilities:
    #     print("Vulnerability:", vulnerability)
    content_json = json.loads(response_json['choices'][0]['message']['content'])
    
    # Beautify the full JSON response
    beautified_json = json.dumps(content_json, indent=4)
    print(beautified_json)

    # Loop through each vulnerability and print it
    # vulnerabilities = content_json.get('vulnerabilities', [])
    # for idx, vulnerability in enumerate(vulnerabilities, start=1):
    #     print(f"\nVulnerability {idx}:")
    #     print(json.dumps(vulnerability, indent=4))
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)