import os

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import connect_db, db, User
from forms import RegisterForm, LoginForm, LogoutForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///user_notes")
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.get("/")
def route_redirect():
    """Redirects users from route to register"""
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def display_registration_form_and_handle_registration():
    """Shows a form that will register/create a user when submitted.
    Handles form submission and creates user. Redirects to user page."""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)

        db.session.add(user)
        db.session.commit()

        return redirect(f"/users/{username}")

    return render_template("register_form.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def display_login_form_and_handle_login():
    """Shows a login form, handles login, and redirects to user page."""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session[username] = user.username
            return redirect(f"users/{username}")
        else:
            form.username.errors = ["bad name/password"]

    return render_template("login_form.html", form=form)

@app.get("/users/<username>")
def display_user_page(username):
    """Show user page of a logged in user."""
    #TODO: Add way to confirm login

    form = LogoutForm()

    return render_template("user_page.html", form=form)

@app.post("/logout")
def logout():
    """ Logs the current user out and redirect them to root """

    form = LogoutForm()

    if form.validate_on_submit():
        session.pop("username", None)

    return redirect("/")