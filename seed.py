"""Seed file to make sample data playlist app."""

from models import User, Note, db
from app import app

# Create all tables

db.drop_all()
db.create_all()

# Add some users

test_user1 = User.register(
    username="testuser1",
    email="tu1@gmail.com",
    password="password",
    first_name="Test User 1 FN",
    last_name="Test User 1 LN",
)

test_user2 = User.register(
    username="testuser2",
    email="tu2@gmail.com",
    password="password",
    first_name="Test User 2 FN",
    last_name="Test User 2 LN",
)

# Add some notes

test_note1 = Note(
    title="Test Note 1 Title",
    content="Test Note 1 Content",
    owner_username="testuser1"
)

test_note2 = Note(
    title="Test Note 2 Title",
    content="Test Note 2 Content",
    owner_username="testuser1"
)

db.session.add(test_note1)
db.session.add(test_note2)
db.session.commit()



