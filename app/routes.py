import os
from flask_wtf import FlaskForm  
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField, HiddenField, SubmitField  
from wtforms.validators import DataRequired, Optional  
from urllib.parse import urlsplit
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import sqlalchemy as sa
from app import db, app
from app.models import User, Subject, Topic, Quiz, QuizQuestion 
from app.enums import QuestionDurationEnum, QuizStatusEnum
from app.forms import (
    LoginForm, 
    RegistrationForm, 
    ProfileForm, 
    SubjectForm, 
    TopicForm,
    QuizForm,
    QuizQuestionForm
)


# TopicForm with added extra fields
class TopicForm(FlaskForm):
    name = StringField("Topic Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    duration = IntegerField("Duration (in minutes)", validators=[Optional()])
    difficulty_level = SelectField("Difficulty Level", choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium')
    is_active = BooleanField("Is Active", default=True)
    subject_id = HiddenField()  # This will be set when creating or editing a topic
    created_at = StringField("Created At", validators=[Optional()])  # Example extra field
    updated_at = StringField("Updated At", validators=[Optional()])  # Example extra field
    submit = SubmitField("Save")


@app.route('/index')
@app.route('/')
def index():
    return render_template("index.html", title="Home")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for("index")
        
        return redirect(next_page)
    
    return render_template("login.html", title="Sign In", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is None:
        app.logger.error(f"User with username {username} not found in the database.")
        flash("User not found.", "danger")
        return redirect(url_for('index')) 
    
    return render_template('user.html', user=user)

@app.route("/user/<username>/edit", methods=["GET", "POST"])
@login_required
def profile(username):
    user = db.session.scalar(sa.select(User).where(User.username == username))

    if user != current_user and not current_user.is_admin:
        flash('You do not have permission to edit this profile.', 'danger')
        return redirect(url_for('index'))

    form = ProfileForm()

    if request.method == "GET":
        form.phone.data = user.phone

    if form.validate_on_submit():
        user.phone = form.phone.data

        # Handle avatar file upload
        if form.avatar.data:
            avatar = form.avatar.data
            if avatar:
                filename = secure_filename(avatar.filename)
                avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                avatar.save(avatar_path)
                user.avatar = f'images/avatars/{filename}'

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user', username=user.username))

    return render_template('profile.html', form=form, user=user)

@app.route("/subjects", methods=["GET"])
@login_required
def subjects():
    subjects = db.session.execute(sa.select(Subject)).scalars().all()
    return render_template("subjects.html", subjects=subjects)

@app.route("/subjects/new", methods=["GET", "POST"])
@login_required
def new_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(name=form.name.data, description=form.description.data)
        db.session.add(subject)
        db.session.commit()
        flash("Subject created successfully!", "success")
        return redirect(url_for("subjects"))

    return render_template("subject_form.html", form=form)

@app.route("/subjects/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_subject(id):
    if not current_user.is_admin:
        flash("permission denied", "danger")
        return redirect(url_for("subjects"))
    
    subject = db.session.scalar(sa.select(Subject).where(Subject.id == id))
    
    if not subject:
        flash("Subject not found or you do not have permission to edit it.", "danger")
        return redirect(url_for("subjects"))
    
    form = SubjectForm(obj=subject)

    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash("Subject updated successfully!", "success")
        return redirect(url_for("subjects"))
    
    return render_template("subject_form.html", form=form, subject=subject)

@app.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        flash("permission denied", "danger")
        return redirect(url_for("subjects"))
    
    subject = db.session.scalar(sa.select(Subject).where(Subject.id == subject_id))
    
    if not subject:
        flash("Subject not found or you do not have permission to delete it.", "danger")
        return redirect(url_for("subjects"))

    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully!", "success")
    return redirect(url_for("subjects"))

@app.route("/subjects/<int:subject_id>/topics", methods=["GET", "POST"])
@login_required
def topics(subject_id):
    subject = db.first_or_404(sa.select(Subject).where(Subject.id==subject_id))
    topics = db.session.scalars(sa.select(Topic).where(Topic.subject_id == subject_id)).all()
    if not subject:
        flash("Subject not found.", "danger")
        return redirect(url_for("subjects"))
    
    form = TopicForm()

    if not current_user.is_anonymous and current_user.is_admin and form.validate_on_submit():
        topic = Topic(
            name=form.name.data,
            description=form.description.data,
            subject = subject
        )
        db.session.add(topic)
        db.session.commit()
        flash("Topic created successfully!", "success")
        return redirect(url_for("view_subject", subject_id=subject_id))  # Redirect to subject page


    return render_template("subject_topics.html", form=form, subject=subject, topics=topics)

@app.route("/subjects/<int:subject_id>/topics/<int:topic_id>/edit", methods=["GET", "POST"])
@login_required
def edit_topic(subject_id, topic_id):
    topic = db.first_or_404(sa.select(Topic).where(
        Topic.id == topic_id, Topic.subject_id == subject_id
    ))

    form = TopicForm(obj=topic)

    if current_user.is_anonymous and not current_user.is_admin:
        redirect(url_for('view_subject', subject_id=subject_id))

    if form.validate_on_submit():
        topic.name=form.name.data
        topic.description=form.description.data

        db.session.commit()
        return redirect(url_for('view_subject', subject_id=subject_id))
    return render_template("topic_form.html", form=form)

@app.route("/subjects/<int:subject_id>/topics/<int:topic_id>/delete", methods=["GET", "POST"])
@login_required
def delete_topic(subject_id, topic_id):
    topic = db.session.scalar(sa.select(Topic).where(Topic.id == topic_id))
    if not topic:
        flash("Topic not found.", "danger")
        return redirect(url_for("subjects"))

    db.session.delete(topic)
    db.session.commit()
    flash("Topic deleted successfully!", "success")
    return redirect(url_for("view_subject", subject_id=subject_id))

@app.route("/subjects/<int:subject_id>", methods=["GET", "POST"])
def view_subject(subject_id):
    subject = db.first_or_404(sa.select(Subject).where(Subject.id == subject_id))
    if not subject:
        flash("Subject not found.", "danger")
        return redirect(url_for("subjects"))

    if current_user.is_anonymous and not current_user.is_admin:
        quizzes = db.session.scalars(sa.select(Quiz).where(Quiz.subject_id == subject_id, Quiz.status == QuizStatusEnum.FROZEN.value))
    else:
        quizzes = db.session.scalars(sa.select(Quiz).where(Quiz.subject_id == subject_id))

    form = QuizForm()

    if form.validate_on_submit():
        quiz = Quiz(duration=form.duration.data, status=form.status.data, quiz_subject=subject)
        db.session.add(quiz)
        db.session.commit()
        flash("Quiz created successfully!", "success")
        return redirect(url_for("view_subject", subject_id=subject_id))

    return render_template("subject_details.html", form=form, subject=subject, quizzes=quizzes)

@app.route("/subject/<int:subject_id>/quizzes/<int:quiz_id>", methods=["GET", "POST"])
def view_quiz(subject_id, quiz_id):
    quiz = db.first_or_404(sa.select(Quiz).where(Quiz.id == quiz_id, Quiz.subject_id == subject_id))
    questions = db.session.scalars(sa.select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id)).all()
    form = QuizQuestionForm()
    
    if form.validate_on_submit():
        new_question = QuizQuestion(
            question=form.question.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            quiz = quiz
        )
        db.session.add(new_question)
        db.session.commit()
        
        flash("Question created successfully!", "success")
        return redirect(url_for("view_quiz", subject_id=quiz.subject_id, quiz_id=quiz_id))
    return render_template("quiz_details.html", quiz=quiz, form=form, questions=questions)

@app.route("/subject/<int:subject_id>/quizzes/<int:quiz_id>/edit", methods=["GET", "POST"])
@login_required
def edit_quiz(subject_id, quiz_id):
    quiz = db.first_or_404(sa.select(Quiz).where(Quiz.id == quiz_id, Quiz.subject_id == subject_id))
    
    form = QuizForm()
    if request.method == "GET":
        form.duration.data = quiz.duration.name
        form.status.data = quiz.status.name

    if form.validate_on_submit():
        quiz.duration = QuestionDurationEnum[form.duration.data]
        quiz.status = QuizStatusEnum[form.status.data]
        db.session.commit()
        return redirect(url_for("view_subject", subject_id=subject_id))

    return render_template("quiz_form.html", form=form)

# Route for deleting a quiz
@app.route('/subject/<int:subject_id>/quizzes/<int:quiz_id>', methods=['POST'])
def delete_quiz(subject_id, quiz_id):
    quiz = db.first_or_404(sa.select(Quiz).where(Quiz.id == quiz_id, Quiz.subject_id == subject_id))

    if not current_user.is_anonymous and current_user.is_admin:
            db.session.delete(quiz)
            db.session.commit()
    
    return redirect(url_for('view_subject', subject_id=subject_id))


