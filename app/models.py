import os
from flask_login import UserMixin
from app import db
from datetime import timedelta
import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional
import pydenticon, hashlib, base64
from app import login
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash

# User table
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    phone: so.Mapped[str] = so.mapped_column(sa.String(15), index=True, unique=True)
    is_admin: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    avatar: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def gen_avatar(self, size=36, write_png=True):
        foreground = [ 
            "rgb(45,79,255)",
            "rgb(254,180,44)",
            "rgb(226,121,234)",
            "rgb(30,179,253)",
            "rgb(232,77,65)",
            "rgb(49,203,115)",
            "rgb(141,69,170)"
        ]
        background = "rgb(256,256,256)"

        digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        basedir = os.path.abspath(os.path.dirname(__file__))
        pngloc = os.path.join(basedir, 'usercontent', 'identicon', str(digest) + '.png')
        icongen = pydenticon.Generator(5, 5, digest=hashlib.md5, foreground=foreground, background=background)
        pngicon = icongen.generate(self.email, size, size, padding=(8, 8, 8, 8), inverted=False, output_format="png")
        
        if write_png:
            if not os.path.exists(os.path.join(basedir, 'usercontent', 'identicon')):
                os.makedirs(os.path.join(basedir, 'usercontent', 'identicon'))  # Ensure directory exists
            with open(pngloc, "wb") as pngfile:
                pngfile.write(pngicon)
        else:
            return str(base64.b64encode(pngicon))[2:-1]
        
    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# # Subject table
# class Subject(db.Model):
#     __tablename__ = 'subject'

#     id: so.Mapped[int] = sa.Column(sa.Integer, primary_key=True)  # Primary key
#     name: so.Mapped[str] = sa.Column(sa.String(100), unique=True, nullable=False)  # Name of the subject
#     description: so.Mapped[str] = sa.Column(sa.Text, nullable=True)  # Optional description of the subject
#     created_at: so.Mapped[sa.DateTime] = sa.Column(sa.DateTime, default=sa.func.now())  # Timestamp when subject is created

#     # Relationship with Topic (one-to-many)
#     topics: so.Mapped[list["Topic"]] = so.relationship("Topic", backref="subject", lazy=True)

#     def __init__(self, name: str, description: str = None):
#         self.name = name
#         self.description = description

#     def __repr__(self):
#         return f"<Subject {self.name}>"  
 
# # Topic table
# class Topic(db.Model):
#     __tablename__ = 'topic'

#     # Define columns
#     id: so.Mapped[int] = sa.Column(sa.Integer, primary_key=True)
#     name: so.Mapped[str] = sa.Column(sa.String(100), unique=True, nullable=False)  # Topic name
#     description: so.Mapped[str] = sa.Column(sa.Text, nullable=True)  # Optional description of the topic
#     created_at: so.Mapped[sa.DateTime] = sa.Column(sa.DateTime, default=sa.func.now())  # Timestamp when the topic is created

#     # Relationship with Subject (one-to-many)
#     subject_id: so.Mapped[int] = sa.Column(sa.Integer, sa.ForeignKey('subject.id'), nullable=False)  # Foreign key to Subject
#     subject: so.Mapped["Subject"] = so.relationship( backref="topics", lazy=True)  # One subject can have many topics

#     # Relationship with Question (one-to-many)
#     questions: so.Mapped[list["Question"]] = so.relationship("Question", backref="topic", lazy=True)  # A topic can have many questions

#     def __init__(self, name: str, subject_id: int, description: str = None):
#         self.name = name
#         self.subject_id = subject_id
#         self.description = description

#     def __repr__(self):
#         return f"<Topic {self.name}>"
    
#     # Quiz table
# class Quiz(db.Model):
#     __tablename__ = 'quiz'

#     # Define columns using the latest version (SQLAlchemy 2.0)
#     id: so.Mapped[int] = sa.Column(sa.Integer, primary_key=True)  # Primary key for the quiz
#     title: so.Mapped[str] = sa.Column(sa.String(256), nullable=False)  # Title of the quiz
#     duration: so.Mapped[int] = sa.Column(sa.Integer, nullable=False)  # Duration in minutes
#     created_at: so.Mapped[sa.DateTime] = sa.Column(sa.DateTime, default=sa.func.now())  # Timestamp for creation
#     topic_id: so.Mapped[int] = sa.Column(sa.Integer, sa.ForeignKey('topic.id'), nullable=False)  # Foreign key to Topic

#     # Relationship with Topic (one-to-many)
#     topic: so.Mapped["Topic"] = so.relationship("Topic", backref="quizzes", lazy=True)  # A topic can have multiple quizzes

#     def __init__(self, title: str, duration: int, topic_id: int):
#         self.title = title
#         self.duration = duration
#         self.topic_id = topic_id

#     def __repr__(self):
#         return f"<Quiz {self.title}>"
    

    





