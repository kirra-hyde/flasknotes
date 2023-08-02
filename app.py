import os

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import connect_db, db, User, Note
from forms import RegisterForm, LoginForm, CSRFProtectionForm, AddNoteForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///user_notes")
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"  #TODO: Put in env

connect_db(app)
db.create_all()  #TODO: Unnecessary to do each time.

toolbar = DebugToolbarExtension(app)

@app.get("/")
def route_redirect():
    """Redirects logged-in users to their page and all others to register"""
    if session.get("username"):
        return redirect(f"/users/{session['username']}")

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

        # Check if users already exists and return flash error
        if User.query.get(username) is not None:
            flash("Username already exists.")
            return render_template("register_form.html", form=form)

        user = User.register(username, password, email, first_name, last_name)

        db.session.add(user)
        db.session.commit()

        session["username"] = user.username  #TODO: Could be in global variable

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
            session["username"] = user.username
            return redirect(f"users/{username}")
        else:
            form.username.errors = ["bad name/password"]

    return render_template("login_form.html", form=form)

@app.get("/users/<username>")
def display_user_page(username):
    """Show user page of a logged in user.  If not the authenticated user,
    return unauthorized"""

    if session.get("username") != username:
        raise Unauthorized()

    form = CSRFProtectionForm()

    user = User.query.get_or_404(username)

    return render_template("user_page.html", form=form, user=user)

@app.post("/logout")
def logout():
    """ Logs the current user out and redirect them to root """

    form = CSRFProtectionForm()

    if form.validate_on_submit():
        session.pop("username", None) #:TODO: Scary message

    return redirect("/")

@app.post("/users/<username>/delete")
def delete_account(username):
    """Removes current user from database.  Redirect to homepage."""

    if session.get("username") != username:
        raise Unauthorized()

    user = User.query.get_or_404(username)

    # Delete all the user's notes
    for note in user.notes:
        db.session.delete(note)

    db.session.commit()

    # Delete the user
    db.session.delete(user)
    db.session.commit()

    session.pop("username", None)

    return redirect("/")

@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def display_add_note_form_and_handle_note_creation(username):
    """Display an add note form and create new note instances from form.
    Redirect to user page."""

    if session.get("username") != username:
        raise Unauthorized()

    user = User.query.get_or_404(username)

    form = AddNoteForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        note = Note(title=title, content=content, owner_username=username)

        db.session.add(note)
        db.session.commit()

        return redirect(f"/users/{username}")


    return render_template("add_note_form.html", form=form)