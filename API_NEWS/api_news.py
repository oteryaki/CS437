from flask import Flask, request, jsonify, send_from_directory
import time
import os
import re
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Create logger2
logger2 = logging.getLogger('logger2')
logger2.setLevel(logging.INFO)

# Create file handler which logs even debug messages
file_handler = logging.FileHandler('abuse_logs.log')
file_handler.setLevel(logging.INFO)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to logger2
logger2.addHandler(file_handler)


def analyze_injection_attempts(request_data):
    """
    Analyze the request data for potential command injection attempts.

    :param request_data: The data to analyze, typically a string from user input.
    :return: Boolean indicating if a potential injection attempt was found.
    """

    # Patterns to check for command injection
    patterns = [
        # Semicolon to end a command (but not in encoded form like %3B)
        r"(?<!%3B);",

        # Double pipe or ampersand for logical operations
        r"\|\|", r"&&",

        # Single pipe for command chaining
        r"(?<!\|)\|(?!\|)",

        # Backticks or $() for command substitution
        r"`", r"\$\(",

        # Subshell execution
        r"\(\)",

        # Newline or Carriage return (typically won't appear in URL but just in case)
        r"\n", r"\r",
    ]

    # Check if any pattern matches the request data
    for pattern in patterns:
        if re.search(pattern, request_data):
            return pattern

    # No suspicious patterns found
    return False

@app.route('/APInews', methods=['GET'])
def download_file():
    """
    This is the APInews which downloads xml files using RSS feeds. It also returns an JSON object in the given sample
    format which is used by APIoriginal.

    {
  "news": [
    {
      "title": "Sample News 1",
      "image_link": "https://example.com/image1.jpg",
      "description": "This is a sample news article.",
      "url": "https://example.com/news/1"
    },
    {
      "title": "Sample News 2",
      "image_link": "https://example.com/image2.jpg",
      "description": "Another example news article.",
      "url": "https://example.com/news/2"
    }
  ]
}

    """

    # variables used in logging
    client_ip = request.remote_addr
    user_agent = request.user_agent.string
    url = request.args.get('url')

    # checking if a valid url is provided
    if not url:
        logging.info(f"No URL provided - Client IP: {client_ip}, User Agent: {user_agent}")
        return "No URL provided", 400
    injection_attempt = analyze_injection_attempts(url)

    # naming for the downloaded xml files
    domain = urlparse(url).netloc.split('.')[1]
    timestamp = time.time()
    domain = domain + str(timestamp)
    os.makedirs('data', exist_ok=True)

    file_path = os.path.join('data', f"{domain}.xml")

    # this is where command injection occurs
    command = f"curl -o \"{file_path}\" \"{url}\""

    # logging in case of an injection
    if injection_attempt:
        logger2.info(f"Executing command: {command} - Client IP: {client_ip}, User Agent: {user_agent}")
        logger2.warning(f"Command injection attempt detected: Pattern '{injection_attempt}' in URL '{url}'")

    # logging in all cases
    logging.info(f"Executing command: {command} - Client IP: {client_ip}, User Agent: {user_agent}")
    os.system(command)

    logging.info(f"File downloaded and processed - Client IP: {client_ip}, User Agent: {user_agent}")
    return jsonify(process_xml_files())


# it is used for hosting malicious xml files in order to demonstrate the injection scenario
@app.route('/myxmlfile')
def serve_xml_file():
    return send_from_directory('', 'malicious_data.xml')


def process_xml_files():
    """
    it reads the xml files, parse them and create the JSON object to return in the format that we expect.
    """
    news_list = []

    for filename in os.listdir('data'):
        if filename.endswith('.xml'):
            file_path = os.path.join('data', filename)
            tree = ET.parse(file_path)
            root = tree.getroot()

            for item in root.findall('.//item'):
                news_item = {
                    "title": item.findtext('title'),
                    "image_link": item.find('enclosure').get('url') if item.find('enclosure') is not None else '',
                    "description": ''.join(item.find('description').itertext()).strip(),
                    "url": item.findtext('link')
                }
                news_list.append(news_item)

    return {"news": news_list}


if __name__ == '__main__':
    app.run(debug=True)
