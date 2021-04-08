from flask import Flask, render_template, session, flash, url_for, redirect
from rpiplatesrecognition.forms import LoginForm

def init_app(app: Flask):
    @app.route('/')
    def index():
        if 'user' in session:
            return render_template('index.html', user=session['user'])
        else:
            return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            flash(f'Login requested for user {form.username.data}')
            return redirect(url_for('index'))
        return render_template('login.html', form=form)
