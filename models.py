"""
models.py — BookClub

SQLAlchemy models for all database entities.
"""

import uuid
from datetime import datetime, timezone
from extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    """A BookClub member.
    
    User has a reading_streak column. Does the stats endpoint use it? (Check routes/stats.py before guessing.)
    No the stats route calculates the reading streak by calculating the numbers of days from started.
    """

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    reading_streak = db.Column(db.Integer, default=0)
    last_finished_at = db.Column(db.DateTime, nullable=True)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    reading_events = db.relationship("ReadingEvent", backref="reader", lazy=True)
    added_books = db.relationship("Book", backref="added_by_user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "reading_streak": self.reading_streak,
            "last_finished_at": (
                self.last_finished_at.isoformat() if self.last_finished_at else None
            ),
        }


class Book(db.Model):
    """A book in the shared reading list."""

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    added_by = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reading_events = db.relationship("ReadingEvent", backref="book", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "pages": self.pages,
            "genre": self.genre,
            "added_by": self.added_by,
            "added_at": self.added_at.isoformat(),
        }


class ReadingEvent(db.Model):
    """
    Records a user's interaction with a book.

    started_at  — when the user began reading (always set)
    finished_at — when the user marked the book as finished (None if still reading)

    What fields does ReadingEvent have? Which ones are always set, and which can be null?
    Reading Event has an id, the associated user_id, the book_id, started_at which is datetime, and finished_at which is also datetime.
    Everything is set and not nullable except the finished_at field.

    What does the UniqueConstraint on ReadingEvent prevent?
    UniqueConstraint prevents the combination of user_id and book_id from being in two seperate rows.
    What this means is that a user can only have one entry with a specific book once, a user cannot read and finish a book, then some time later read and finish that same book.
    This also prevents users from starting the same book multiple times.


    
    """

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.String(36), db.ForeignKey("book.id"), nullable=False)
    started_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    finished_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "book_id", name="unique_user_book"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }
