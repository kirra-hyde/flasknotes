from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Site user."""
    __tablename__="users"

    username = db.Column(
        db.String(20),
        primary_key=True,
    )
    password = db.Column(
        db.String(100),
        nullable=False,
    )
    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )
    first_name = db.Column(
        db.String(30),
        nullable=False,
    )
    last_name = db.Column(
        db.String(30),
        nullable=False
    )

    notes = db.relationship("Note", backref="user")


    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """
        Register a new user with the provided details
        Stores provided password one-way hashed.
        Returns a new User instance with the hashed password.
        """

        hashed = bcrypt.generate_password_hash(password).decode('utf8')
        user = cls(
            username=username,
            password=hashed,
            email=email,
            first_name=first_name,
            last_name=last_name
            )
        db.session.add(user)
        db.session.commit()

        return user

    @classmethod
    def authenticate(cls, username, password):
        """
        Authenticates the provided username with the provided password.
        Returns the associated User instance if username and password match.
        Returns False if the username / password combination is not found.
        """

        user = cls.query.filter_by(username=username).one_or_none()
        if user and bcrypt.check_password_hash(user.password, password):
            return user

        return False


class Note(db.Model):
    """User Notes"""
    __tablename__="notes"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    title = db.Column(
        db.String(100),
        nullable=False,
    )
    content = db.Column(
        db.Text,
        nullable=False
    )
    owner_username = db.Column(
        db.String(20),
        db.ForeignKey("users.username"),
        nullable=False
    )
