from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


import os
from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request

from process import chat, docs_embeddings
from utils import create_response, log_message


###--------------------------------------------------------------------------###
### Creating Flask App


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    return app


# Creating Flask App
app = create_app()


# ----------------- UTILS & HELPERS ----------------- #


def handle_request(func, *args, **kwargs):
    """Handle a request to the API."""
    try:
        par = request.json if request.method == "POST" else request.args
        if request.method == "POST":
            log_message(f"{par}\n", "info")
        return func(par, *args, **kwargs)
    except Exception as e:
        log_message(f"Error: {e}", "error")
        return create_response(False, f"Error: An error occurred {e}", {}, 400)


###--------------------------------------------------------------------------###


@app.route(f"/add_docs", methods=["POST"])
@cross_origin()
def add_docs_route():
    """Handle the POST request to generate embeddings for documents"""
    return handle_request(docs_embeddings)


###--------------------------------------------------------------------------###


@app.route(f"/chat", methods=["POST"])
@cross_origin()
def chat_route():
    """Handle the POST request to chat with the documents database."""
    return handle_request(chat)


###--------------------------------------------------------------------------###


def main():
    # Start the Flask app.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=False)


###--------------------------------------------------------------------------###

if __name__ == "__main__":
    main()
