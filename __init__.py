from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello, I love item catalog"
if __name__ == "__main__":
    app.run()
