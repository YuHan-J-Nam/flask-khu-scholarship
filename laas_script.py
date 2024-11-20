from flask import Flask, request, jsonify
from functions import create_body, call_module
import os, requests
from datetime import datetime

app = Flask(__name__)

# Load environment variables
WANTED_API_URL = 'https://api-laas.wanted.co.kr/api/preset/v2/chat/completions'
WANTED_API_KEY = '32f1d4fcdaa5aa91b34c4b5343d512a13e9c2d303a7f4a6da196af4d7b0463a5'

# Header configuration
header = {
    "project": "KHU_PROMPTHON_018",
    "apiKey": WANTED_API_KEY,
}

# Module hash and parameters
module_hash = {
    "0": "39c80921dd1db0b51cff11e7e3519cb062a1d8658f891e8dc4b644dff0cd3a9f",
    "1": "79759a823a132c4f63c6375c414741ab4148fb1686fcb3e3d52b412aca4d2b99",
    "2": "d9d5cda6ab02eee1cc96f79a3d0caecb372ece47c43e1471148930cdb2e96924",
    "3": "fce0ba9ecfdad62c3c38f11b07da7bf5bcb08bebd583cb80c4ff324039d5fb77",
    "99": "cdc84e9c9bc3c696c2595d4c8027be8ac200283c476ab53f2f6c29800da89c17",
}

params_dict = {
    "0": None,
    "1": None,
    "2": None,
    "3": {"today_datetime": datetime.now().strftime("%A %Y-%m-%d %H:%M:%S")},
    "99": None,
}

def process_chat(user_input):
    """Core logic for processing chat without relying on Flask."""
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(f"user: {user_input}\n")

    # Prepare API input
    with open('log.txt', 'r', encoding='utf-8') as f:
        log = f.read()

    recall_body = {
        "hash": "59c96154c0ac7a7f92dba5e47ca695d762c7f188abb13383f6c43130d441cba9",
        "messages": [{"role": "user", "content": log}],
    }

    # Call Recall Module
    recall_output = requests.post(WANTED_API_URL, headers=header, json=recall_body)

    if recall_output.ok:
        recall_content = recall_output.json()["choices"][0]["message"]["content"]
        with open('recall_log.txt', 'w', encoding='utf-8') as f:
            f.write(recall_content)
        api_input = f"{recall_content}\n 사용자 질문:{user_input}"
    else:
        return {"response": "Error with Recall Module", "status": recall_output.status_code}

    # Call Module 0
    module_0_body = create_body(module_hash["0"], params=None, input=api_input)
    content, module_num = call_module(WANTED_API_URL, header, module_0_body, module_num="0")

    # Call Next Module
    module_body = create_body(module_hash[module_num], params=params_dict[module_num], input=content)
    final_content = call_module(WANTED_API_URL, header, module_body, module_num)[0]

    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(f"AI: {final_content}\n")

    return final_content

@app.route("/api/chat", methods=["POST"])
def chat():
    """Flask route for handling chat."""
    data = request.get_json()
    user_input = data.get("input")

    if not user_input:
        return jsonify({"error": "Input is required"}), 400

    # Call the core processing logic
    response = process_chat(user_input)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
