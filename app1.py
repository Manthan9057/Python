import streamlit as st
from flask import Flask, render_template_string, request, jsonify, send_from_directory
import threading
import socket
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from streamlit.web import cli as stcli
import os

# Flask App Initialization
app = Flask(__name__, static_folder="static")

# Save the uploaded logo into the static folder
logo_path = "logo.png"
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists(logo_path):
    with open(logo_path, "wb") as f:
        f.write(open("logo.png", "rb").read())

# HTML Template for Flask UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video Redirect</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: #333;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }
        h1 {
            color: #FF0000;
            font-size: 24px;
        }
        img {
            max-width: 150px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            width: 80%;
            padding: 10px;
            font-size: 16px;
            margin-top: 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        button {
            background-color: #FF0000;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 20px;
            font-size: 16px;
        }
        button:hover {
            background-color: #cc0000;
        }
    </style>
</head>
<body>
<div class="container">
    <img src="{{ url_for('static', filename='logo.png') }}" alt="Logo">
    <h1>YouTube Viewer</h1>
    <p>Enter the YouTube URL below:</p>
    <input type="text" id="youtubeUrl" placeholder="Paste YouTube URL here" />
    <br>
    <button onclick="redirectToVideo()">Open in Incognito 10 Times</button>
</div>

<script>
    function redirectToVideo() {
        const url = document.getElementById('youtubeUrl').value;

        const youtubeRegex = /^(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+$/;

        if (youtubeRegex.test(url)) {
            fetch('/redirect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            }).then(response => response.json()).then(data => {
                if (data.success) {
                    alert("Opening video in incognito mode 10 times with 10-minute intervals.");
                } else {
                    alert(data.message);
                }
            });
        } else {
            alert('Please enter a valid YouTube URL');
        }
    }
</script>
</body>
</html>
"""

# Regular expression for YouTube URL validation
youtube_regex = re.compile(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+$')

# Flask route
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/redirect', methods=['POST'])
def redirect_to_video():
    data = request.get_json()
    url = data.get('url', '')

    if youtube_regex.match(url):
        # Open video in incognito mode 10 times
        threading.Thread(target=open_in_incognito_multiple_times, args=(url, 10, 600)).start()
        return jsonify(success=True, message="Opening video in incognito 10 times with 10-minute intervals.", url=url)
    else:
        return jsonify(success=False, message="Invalid YouTube URL.")

# Function to open a YouTube video in incognito mode
def open_in_incognito(url):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

# Function to open video in incognito mode multiple times
def open_in_incognito_multiple_times(url, count, interval):
    for i in range(count):
        open_in_incognito(url)
        if i < count - 1:  # Avoid sleeping after the last execution
            time.sleep(interval)

# Streamlit UI
st.image(logo_path, width=150)
st.title("YouTube Video Redirect")
st.write("Enter the YouTube URL below:")
youtube_url = st.text_input("Paste YouTube URL here")

if st.button("Open Video in Incognito 10 Times"):
    if youtube_regex.match(youtube_url):
        st.success("Opening video in incognito mode 10 times with 10-minute intervals.")
        threading.Thread(target=open_in_incognito_multiple_times, args=(youtube_url, 10, 600)).start()
    else:
        st.error("Invalid YouTube URL. Please enter a valid URL.")

# Helper function to get the local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# Display network address
def display_network_info():
    local_ip = get_local_ip()
    st.write(f"Access this app on your local network at: http://{local_ip}:8501")

display_network_info()

# Run Flask App in a separate thread
def run_flask():
    app.run(debug=False, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start Streamlit App
    stcli.main()
