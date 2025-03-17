import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    PasswordField, 
    BooleanField, 
    SubmitField, 
    TextAreaField, 
    IntegerField, 
    SelectField, 
    HiddenField,
    FieldList,
    FormField
)
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
from flask_login import current_user

from app import db
from app.models import User, Subject, Topic
from app.enums import QuestionDurationEnum, QuizStatusEnum, QuestionAnswerEnum


# Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    phone = StringField("Phone", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError("Please use a different username")
        
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError("Please use a different email address")

# Profile Form
class ProfileForm(FlaskForm):
    phone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=15)])
    avatar = FileField('Update Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField("Submit")


# Subject Form
class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')


# Topic Form
class TopicForm(FlaskForm):
    name = StringField("Topic Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    duration = IntegerField("Duration (in minutes)", validators=[Optional()])
    difficulty_level = SelectField("Difficulty Level", choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium')
    is_active = BooleanField("Is Active", default=True)
    subject_id = HiddenField()  # This will be set when creating or editing a topic
    submit = SubmitField("Save")

    def validate_name(self, name):
        # Check if topic name already exists (unique validation for Topic)
        topic = db.session.scalar(sa.select(Topic).where(Topic.name == name.data))
        if topic is not None:
            raise ValidationError("Topic already exists")

    def validate_description(self, description):
        # Ensure the description is not longer than 1000 characters
        if len(description.data) > 1000:
            raise ValidationError("Description must be less than 1000 characters")

class QuizForm(FlaskForm):
    duration = SelectField('Question Duration in minutes', choices=[(d.name, d.value) for d in QuestionDurationEnum], validators=[DataRequired()])
    status = SelectField('Select Status', choices=[(s.name, s.value) for s in QuizStatusEnum], validators=[DataRequired()])
    submit = SubmitField("Submit")

class QuizQuestionForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired()])
    option2 = StringField('Option 2', validators=[DataRequired()])
    option3 = StringField('Option 3', validators=[DataRequired()])
    option4 = StringField('Option 4', validators=[DataRequired()])

    # Set choices for the answer options using integer values
    option = SelectField('Answer', choices=[
        (QuestionAnswerEnum.OPTION1.value, "Option 1"),
        (QuestionAnswerEnum.OPTION2.value, "Option 2"),
        (QuestionAnswerEnum.OPTION3.value, "Option 3"),
        (QuestionAnswerEnum.OPTION4.value, "Option 4"),
    ], validators=[DataRequired()])

    submit = SubmitField('Submit')

class QuizQuestionAnswerForm(FlaskForm):
    option = SelectField('Answer', choices=[(o.name, o.value) for o in QuestionAnswerEnum], validators=[DataRequired()])
    submit = SubmitField('Submit')