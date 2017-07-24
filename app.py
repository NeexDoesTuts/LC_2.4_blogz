from flask import Flask, redirect, request, render_template, flash, session
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
        self.owner = owner # why is this owner and not owner_id,
        # passing in the entire object I think
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


@app.before_request
def require_login():
    allowed_routes = ["login", "blog", "index", "signup"] # these are names for methods and not request routes!
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", users=users)


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
            owner = User.query.filter_by(username=session["username"]).first()

            new_post = Post(post_title, post_body, owner)
            db.session.add(new_post)
            db.session.commit()
            id = new_post.id # grab id upon creation of new post
            # and redirect here with the new id so it displays the post
            return redirect("/blog?id={}".format(id))

    # if there is some argument in the query AKA the blog id from above redirect
    # or the user id
    if len(request.args) != 0:
        user_id = request.args.get("user") 
        post_id = request.args.get("id")
        # fix for posts and users not in database
        
        if user_id:
            user_posts = Post.query.filter_by(owner_id=user_id).all()
            return render_template("user_posts.html", user_posts=user_posts)
        if post_id:
            post = Post.query.get(post_id)
            if post:
                return render_template("blog_post.html", post=post, title=post.title)
            else:
                flash("There is no blog with that id. Read sth else?")
                return redirect("/blog")
    else:
        posts = Post.query.order_by(Post.pub_date.desc()).all() # otherwise grab all and display desc
        return render_template("blog.html", title="All blog posts", posts=posts)

@app.route("/newpost", methods=["GET"])
def new_post():
    return render_template("new_post.html", title="Publish new post")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]
        error = False

        if password != verify:
            flash("Passwords do not match.")
            error = True
        
        if not (password or verify or username):
            flash("Fields cannot be left empty.")
            error = True

        if len(password) < 3:
            flash("Password has to be at least 3 characters long")
            error = True

        if len(username) < 3:
            flash("Username has to be at least 3 characters long")                
            error = True
        if " " in password or " " in username:
            flash("Spaces are not allowed.")
            error = True

        if error:
            return render_template("signup.html")


        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            flash("Welcome aboard! Time to write something!")
            return redirect("/newpost")
        else:
            flash("User already exists!")

    return render_template("signup.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html", title="Please login")
    else:
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first() # user return or None

        # if user exists and verified password
        if user and user.password == password:
            session["username"] = username
            flash("You are logged in! The scene is yours...")
            return redirect("/newpost")
        elif user and user.password != password: # user exists but wrong password (otherwise nontype error)
            flash("Password is incorrect", "error")
        elif not user:
            flash("No such user", "error")

        return render_template("login.html", title="Please login")

@app.route("/logout")
def logout():
    del session["username"]
    flash("You are logged out!")
    return redirect("/blog")








if __name__ == "__main__":
    app.run()




