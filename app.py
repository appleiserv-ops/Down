from flask import Flask, request, send_file, jsonify
import os
import uuid
import subprocess

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def run_download(url, out):
    cmd = [
        "yt-dlp",
        url,
        "-f", "bv*+ba/best",
        "--merge-output-format", "mp4",
        "--no-playlist",
        "--user-agent", "Mozilla/5.0",
        "-o", out
    ]
    subprocess.run(cmd, check=True)


@app.route("/")
def home():
    return "Universal Downloader API running"


@app.route("/download")
def download():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "no url"}), 400

    file_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_DIR, file_id + ".%(ext)s")

    try:
        run_download(url, output)

        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(file_id):
                path = os.path.join(DOWNLOAD_DIR, f)
                return send_file(path, as_attachment=True)

        return jsonify({"error": "file not found"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
