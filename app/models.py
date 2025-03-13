import os
from datetime import date
from datetime import datetime, timezone
from flask_login import UserMixin
from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional
import pydenticon, hashlib, base64
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from app.enums import QuestionDurationEnum, QuizStatusEnum

# User table
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
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

# Subject table
class Subject(db.Model):
    __tablename__ = 'subject'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)  # Primary key
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True, nullable=False)  # Name of the subject
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)  # Optional description of the subject
    created_at: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now())  # Timestamp when subject is created
    
    # Relationship with Topic (one-to-many)
    topics: so.Mapped[list["Topic"]] = so.relationship("Topic", back_populates="subject")
    quizzes: so.Mapped[list["Quiz"]] = so.relationship("Quiz", back_populates="quiz_subject")

    def __repr__(self):
        return f"<Subject {self.name}>"

class Topic(db.Model):
    __tablename__ = 'topic'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)  # Primary key
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True, nullable=False)  # Name of the topic
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)  # Description of the topic
    created_at: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now())  # Timestamp when topic is created
    
    # Relationship with Subject (many-to-one)
    subject_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey(Subject.id), nullable=False)
    subject: so.Mapped["Subject"] = so.relationship("Subject", back_populates="topics")

    def __repr__(self):
        return f"<Topic {self.name}>"

class Quiz(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    created_at: so.Mapped[date] = so.mapped_column(sa.Date, nullable=False, default=lambda: datetime.now(timezone.utc))
    duration: so.Mapped[QuestionDurationEnum] = so.mapped_column(
        sa.Enum(QuestionDurationEnum),
        nullable=False,
        default=QuestionDurationEnum.ONE_MINUTE
    )
    status: so.Mapped[QuizStatusEnum] = so.mapped_column(
        sa.Enum(QuizStatusEnum), 
        nullable=False,
        default=QuizStatusEnum.OPEN
    )

    subject_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey(Subject.id), nullable=False)
    quiz_subject: so.Mapped["Subject"] = so.relationship("Subject", back_populates="quizzes")
    questions: so.Mapped[list["QuizQuestion"]] = so.relationship("QuizQuestion", back_populates="quiz")
    
    def __repr__(self):
        return f'<Quiz {self.id}>'

class QuizQuestion(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    question: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    created_at: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now())
    option1: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    option2: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    option3: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    option4: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    quiz_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey(Quiz.id), nullable=False)
    quiz: so.Mapped["Quiz"] = so.relationship("Quiz", back_populates="questions")

    def __repr__(self):
        return f"<Question {self.question}>"

class QuizzQuestionAnsers(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    answer: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    created_at: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now())
    question_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey(QuizQuestion.id), nullable=False)
    question: so.Mapped["QuizQuestion"] = so.relationship("QuizQuestion", back_populates="answers")

    def __repr__(self): 
        return f"<Answer {self.answer}>"

class QuizQuestionUserAnswers(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    answer: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    created_at: so.Mapped[sa.DateTime] = so.mapped_column(sa.DateTime, default=sa.func.now())
    question_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey(QuizQuestion.id), nullable=False)
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey(User.id), nullable=False)
    question: so.Mapped["QuizQuestion"] = so.relationship("QuizQuestion", back_populates="user_answers")
    user: so.Mapped["User"] = so.relationship("User", back_populates="answers")

    def __repr__(self):
        return f"<Answer {self.answer}>"

@login.user_loader
def load_user(id):
    return db.session.query(User).get(int(id))