import os
import sys
import requests
import json
import markdown2

def create_body(module_hash, params=None, input=None):
    # Body 설정
    body = {
        "hash": module_hash,
        "params": params
    }
    if input is not None:
        body["messages"] = [{"role": "user", "content": input}]

    return body


def call_module(URL, header, body, module_num):
    # POST 요청
    response = requests.post(URL, headers=header, json=body)

    # save response to json file for debugging
    # with open('response.json', 'w', encoding='utf-8') as f:
    #     json.dump(response.json(), f, ensure_ascii=False, indent=4)

    # Check response from LaaS API
    if response.ok:
        content = response.json()["choices"][0]["message"]["content"]

        if module_num == "0":
            output, ques_code = content.split("---")
            return output, ques_code
        else:
            return content, None
        
    else:
        print("Error: Response status code:", response.status_code)
        print("Response content:", response.text)

        return None, None
    
def markdown_to_html(txt):
    # Escape numbers and special characters
    escaped_markdown = txt.replace("1.", "1\.").replace("2.", "2\.").replace("3.", "3\.").replace("4.", "4\.").replace("5.", "5\.").replace("6.", "6\.").replace("7.", "7\.").replace("8.", "8\.").replace("9.", "9\.").replace("0.", "0\.")
    
    # Define newlines where needed
    escaped_markdown = escaped_markdown.replace(" -", "\n-")

    # convert markdown to html
    html_response = markdown2.markdown(escaped_markdown)
    return html_response