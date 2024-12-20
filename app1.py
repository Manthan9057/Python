import streamlit as st
from flask import Flask, render_template_string, request, jsonify
import re
import threading
import socket
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# Flask App Initialization
app = Flask(__name__)

# HTML Template for the web interface
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
            background-color: black;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: #333;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            font-size: 24px;
        }
        input[type="text"] {
            width: 80%;
            padding: 10px;
            font-size: 16px;
            margin-top: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #444;
            color: white;
        }
        button {
            background-color: black;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            margin-top: 20px;
        }
        .count-section {
            margin-top: 20px;
            font-size: 18px;
        }
        .count-section span {
            font-weight: bold;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>YouTube Viewer</h1>
    <p>Enter the YouTube URL below:</p>
    <input type="text" id="youtubeUrl" placeholder="Paste YouTube URL here" />
    <button onclick="redirectToVideo()">Open Video</button>
    <div class="count-section">
        <p>Click Count: <span id="countDisplay">0</span></p>
    </div>
</div>
<script>
    let count = 0;
    function redirectToVideo() {
        const url = document.getElementById('youtubeUrl').value;
        const youtubeRegex = /^(https?:\\/\\/)?(www\\.youtube\\.com|youtu\\.be)\\/.+$/;
        if (youtubeRegex.test(url)) {
            fetch('/redirect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            }).then(response => response.json()).then(data => {
                if (data.success) {
                    count++;
                    document.getElementById('countDisplay').textContent = count;
                    alert("Video URL: " + data.url);
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

# Global Variables
click_count = 0
click_count_lock = threading.Lock()
youtube_regex = re.compile(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+$')

# Flask Routes
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/redirect', methods=['POST'])
def redirect_to_video():
    global click_count
    data = request.get_json()
    url = data.get('url', '')
    if youtube_regex.match(url):
        with click_count_lock:
            click_count += 1
        return jsonify(success=True, message="Video URL is valid!", url=url, count=click_count)
    return jsonify(success=False, message="Invalid YouTube URL.")

# Streamlit UI
st.markdown(
    """
    <style>
    body, .stApp, .stTextInput {
        color: white;
        background-color: black;
    }
    .stTextInput input {
        color: white !important;
        background-color: #333 !important;
        border: 1px solid white !important;
    }
    .stButton>button {
        background-color: black !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.image("logo.png", width=150, caption=None)
st.title("YouTube Video Redirect")
youtube_url = st.text_input("Paste YouTube URL here:")

def open_in_incognito(url, count=10, interval=10):
    for _ in range(count):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        time.sleep(5)
        driver.quit()
        time.sleep(interval)

if st.button("Open in Incognito 10 Times"):
    if youtube_regex.match(youtube_url):
        st.success("Opening video 10 times in incognito mode...")
        threading.Thread(target=open_in_incognito, args=(youtube_url, 10, 10)).start()
    else:
        st.error("Invalid YouTube URL. Please try again.")

# Local IP
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

st.write(f"Access Flask UI at: [http://{get_local_ip()}:5000](http://{get_local_ip()}:5000)")

# Run Flask
def run_flask():
    app.run(debug=False, use_reloader=False, port=5000)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    st.write("Flask server is running in the background.")
