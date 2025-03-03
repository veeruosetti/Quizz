from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()
  
#usertable
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, unique=True)
    avatar = Column(String)
    phone = Column(String, unique=True)
    is_admin = Column(Boolean, default=False)

#subject table
class Subject(Base):
    __tablename__= 'subject'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

#topic table
class Topic(Base):
    __tablename__ ='topic'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'))

    Subject = relationship('Subject')

#quiz table
class Quiz(Base):
    __tablename__ = 'quiz'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topic.id'))
    duration = Column(Integer, nullable=False) #duration in minutes

    topic = relationship('Topic')

#QuizQuestion table
class QuizQuestion(Base):
    __tablename__ = 'quiz_question'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey('quiz.id'))
    question = Column(String, nullable=False)
    option1 = Column(String, nullable=False)
    option2 = Column(String, nullable=False)
    option3 = Column(String, nullable=False)
    option4 = Column(String, nullable=False)

    quiz = relationship('Quiz')

#QuizQuestionAnswer table
class QuizQuestionAnswer(Base):
    __tablename__ = 'quiz_question_answer'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_question_id = Column(Integer, ForeignKey('quiz_question.id'))
    answer = Column(String, nullable=False)

    quiz_question = relationship('QuizQuestion')

#QuizQuestionuseranswer table
class QuizQuestionUserAnswer(Base):
    __tablename__ = 'quiz_question_user_answer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    quiz_question_id = Column(Integer, ForeignKey('quiz_question.id'))
    answer = Column(String, nullable=False)

    quiz_question = relationship('QuizQuestion')

#UserQuiz table 
class UserQuiz(Base):
    __tablename__ = 'user_quiz'

    id = Column(Integer,primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    quiz_id = Column(Integer, ForeignKey('quiz.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False) #e.g, "completed", "in progress"

    user = relationship('User')
    quiz = relationship('Quiz')

#Database Connection
DATABASE_URL = "sqlite:///quiz.db" #change this if using mysql or postgresql
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)