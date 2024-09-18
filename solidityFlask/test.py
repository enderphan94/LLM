import os
import subprocess
import re
import openai
import json
from flask import Flask, request, render_template, redirect, jsonify
from dotenv import load_dotenv

results = {"status": "Failed", "results": None}

slither_results = ""
if os.path.exists("slither_output.json"):
    with open("slither_output.json", 'r') as file:
        slither_results = file.read()
        print(f"Slither results read from file: {slither_results}")
        if not slither_results:
            print("Slither results file is empty after reading.")
else:
    print("Slither results file does not exist.")
