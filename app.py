from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URL"] = "mysql+pymysql://build-a-blog:buildablog@localhost:3306/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

@app.route("/")
def index():
    return redirect("blog")


@app.route("/blog")
def blog():
    return "hello there"

if __name__ == "__main__":
    app.run()
