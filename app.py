from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:buildablog@localhost:3306/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route("/")
def index():
    return redirect("blog")


@app.route("/blog", methods=["POST", "GET"])
def blog():
    if request.method == "POST":
        post_title = request.form["post-title"]
        post_body = request.form["post-body"]
        new_post = Post(post_title, post_body)
        db.session.add(new_post)
        db.session.commit()

    posts = Post.query.all()

    return render_template("blog.html", title="Blog posts", posts=posts)

if __name__ == "__main__":
    app.run()
