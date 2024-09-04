import os
import logging
import requests
from flask import jsonify
from termcolor import colored


###--------------------------------------------------------------------------###


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


###--------------------------------------------------------------------------###


def create_response(status, message, data, code):
    return jsonify({"status": status, "message": message, "data": data}), code


###--------------------------------------------------------------------------###


def log_message(message, level):
    """
    Logs a message with the specified severity level.

    Parameters:
    - message (str): The log message.
    - level (str): The log level. Valid values are 'debug', 'info', 'warning', 'error', 'critical'.
    """
    color_map = {
        "debug": "cyan",
        "info": "green",
        "warning": "yellow",
        "error": "red",
        "critical": "red",
    }

    # Validate log level
    if level.lower() not in color_map:
        raise ValueError("Invalid log level specified.")

    if not hasattr(logger, level.lower()):
        raise ValueError(f"Unsupported log level: {level}")

    colored_message = colored(message, color_map[level.lower()])
    getattr(logger, level.lower())(colored_message)


###--------------------------------------------------------------------------###


def download_file(url: str, output_dir: str = "temp"):
    """Download a file from a URL and save it to the specified directory."""
    os.makedirs(output_dir, exist_ok=True)
    file_name = url.split("/")[-1]
    file_path = os.path.join(output_dir, file_name)

    # Check if file already exists to avoid re-downloading
    if not os.path.exists(file_path):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                return file_path
            else:
                e = f"Error: Unable to download the file. HTTP status code: {response.status_code}"
                log_message(e, "error")
        except requests.exceptions.RequestException as e:
            log_message(f"Error: Unable to download the file from {url}", "error")
    else:
        log_message(f"File already exists: {file_path}", "info")
        return file_path
