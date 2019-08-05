from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.database.queries import get_user, insert_user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.username.data)
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('data_center_select.choose_data'))
        else:
            flash('Invalid user or password.', category="danger")
    return render_template('login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout was correct.', category="success")
    return redirect(url_for('auth.login'))


# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         insert_user(username=form.username.data,
#                     password=form.password.data)
#         flash('You have successfully registered! You may now login.')
#         return redirect(url_for('auth.login'))
#     return render_template('register.html', form=form, title='Register')
