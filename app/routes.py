import os
from urllib.parse import urlsplit
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import sqlalchemy as sa
from app import db, app
from app.models import User
from app.forms import LoginForm, RegistrationForm, ProfileForm


@app.route('/index')
@app.route('/')
@login_required
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
        
        # Handle the 'next' argument in the request
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
    return render_template('user.html', user=user)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        # Update phone number
        user.phone = form.phone.data

        # Handle avatar file upload
        if form.avatar.data:
            avatar = form.avatar.data
            if avatar and allowed_file(avatar.filename):
                filename = secure_filename(avatar.filename)
                avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                avatar.save(avatar_path)

                # Save the filename in the user model with forward slashes
                user.avatar = f'images/avatars/{filename}'

        # Commit changes to the database
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user', username=user.username))

    return render_template('profile.html', form=form, user=user)


