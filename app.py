import os
from flask import Flask, request, jsonify, render_template
import markdown2
from functions import markdown_to_html
from laas_script import process_chat

app = Flask(__name__)

LOG_FILE = "log.txt"

@app.route("/")
def home():
    return render_template("index.html")  # Serve an HTML template as the homepage

@app.route("/api/chat", methods=["POST"])
def call_llm():
    data = request.get_json()
    user_input = data.get("input")

    if user_input.lower() == "exit":
        return jsonify({"response": "Session ended. Goodbye!"})

    # Create log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"User session started.\n")

    response = process_chat(user_input)

    print(response)

    # Escape numbers and special characters
    escaped_markdown = markdown_to_html(response)

    # Convert markdown to HTML
    html_response = markdown2.markdown(escaped_markdown)
    print(html_response)

    return jsonify({"response": html_response})

# Delete log file when the app is shut down
# @app.teardown_appcontext
# def cleanup_log_file(exception=None):
#     if os.path.exists(LOG_FILE):
#         os.remove(LOG_FILE)
#     return exception

if __name__ == "__main__":
    app.run(debug=True)
