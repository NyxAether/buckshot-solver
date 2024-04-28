from flask import Flask

app = Flask(__name__)


@app.route("/")
def index() -> str:
    return "Hello, World!"
