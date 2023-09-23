# app/auth.py

# Import other necessary modules
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db, MEDIA_PATH  # Import MEDIA_PATH from __init__.py
from app.models import User
import os
from . import mail
from flask_mail import Message

auth = Blueprint('auth', __name__)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        
        # Redirect to the home view in the 'views' blueprint
        return redirect(url_for('views.home'))

    return render_template('authentication/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        suburb = request.form.get('suburb')
        state = request.form.get('state')
        country = request.form.get('country')
        username = request.form.get('username')
        password = request.form.get('password')
        profile_picture = request.files.get('profile_picture')

        user = User.query.filter_by(username=username).first()

        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.register'))

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(MEDIA_PATH, filename))

        new_user = User(fullname=fullname, gender=gender, dob=dob, 
        email=email, phone=phone, address=address, suburb=suburb, 
        state=state, country=country, username=username, 
        password_hash=generate_password_hash(password, method='sha256'), 
        profile_picture=filename if profile_picture else None)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('authentication/register.html')




@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
