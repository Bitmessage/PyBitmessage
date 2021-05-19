from flask import Flask, send_from_directory

app = Flask(__name__)


@app.route("/repo/<path:path>")
def static_dir(path):
    return send_from_directory("repo", path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
