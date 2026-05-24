from flask import Flask, request, send_file, jsonify
import os, uuid, subprocess

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def download(url, output):
    base_cmd = [
        "yt-dlp",
        url,
        "-f", "bv*+ba/best",
        "--merge-output-format", "mp4",
        "--no-playlist",
        "--force-ipv4",
        "--user-agent", "Mozilla/5.0",
        "--extractor-retries", "3",
        "--retry-sleep", "2",
        "-o", output
    ]

    r = run_cmd(base_cmd)

    if r.returncode != 0:
        return False, r.stderr

    return True, None


@app.route("/")
def home():
    return "PRO downloader running"


@app.route("/download")
def dl():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "no url"}), 400

    url = url.strip()

    file_id = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_DIR, file_id + ".%(ext)s")

    ok, err = download(url, output)

    if not ok:
        return jsonify({
            "error": "download failed",
            "details": err
        }), 500

    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(file_id):
            return send_file(os.path.join(DOWNLOAD_DIR, f), as_attachment=True)

    return jsonify({"error": "file not found"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
