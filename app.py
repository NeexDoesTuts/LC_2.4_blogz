from flask import Flask, redirect, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from flask_debug import Debug

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:blogzishere@localhost:3306/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = 'ctx3IlH4hZVurEio3dx9o'
Debug(app)
# app.run(debug=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner # why is this owner and not owner_id
        if pub_date is None:
            pub_date = datetime.utcnow()
            self.pub_date = pub_date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship("Post", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route("/")
def index():
    return redirect("blog")


@app.route("/blog", methods=["POST", "GET"])
def blog():

    # if I send you here via POST (newpost), please save me   
    if request.method == "POST":
        post_title = request.form["post-title"]
        post_body = request.form["post-body"]
        if not post_title:
            flash("Please fill in blog title")
        if not post_body:
            flash("Please fill in post body")
        
        if not (post_body and post_title):
            return redirect("/newpost")   
        else:
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
        posts = Post.query.order_by(Post.pub_date.desc()).all() # otherwise grab all and display desc
        
        return render_template("blog.html", title="All blog posts", posts=posts)

@app.route("/newpost", methods=["GET"])
def new_post():
    return render_template("new_post.html", title="Publish new post")

if __name__ == "__main__":
    app.run()
