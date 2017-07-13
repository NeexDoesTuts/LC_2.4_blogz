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

    # if I send you here via POST (newpost), please save me   
    if request.method == "POST":
        post_title = request.form["post-title"]
        post_body = request.form["post-body"]
        new_post = Post(post_title, post_body)
        db.session.add(new_post)
        db.session.commit()
        id = new_post.id # grab id upon creation of new post
        # and redirect here with the new id so it displays the post
        return redirect("/blog?id={}".format(id))

    # if there is some argument in the query AKA the blog id from above redirect
    if len(request.args) != 0:
        id = request.args["id"] # grab the id
        post = Post.query.get(id) # grab the post from database
        # display only this new post on the page 
        return render_template("blog_post.html", post=post, title=post.title)
    else:
        posts = Post.query.all() # otherwise grab all and display
        return render_template("blog.html", title="All blog posts", posts=posts)

@app.route("/newpost", methods=["GET"])
def new_post():
    return render_template("new_post.html", title="Publish new post")

if __name__ == "__main__":
    app.run()
