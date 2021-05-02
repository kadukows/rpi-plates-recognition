from flask import Flask, render_template, session, flash, url_for, redirect, jsonify
from flask.globals import request
from flask_login import current_user, login_user
from flask_login.utils import login_required, logout_user
from flask_socketio import SocketIO, join_room, leave_room
from werkzeug.urls import url_parse

from .db import db
from .db.helpers import get_whitelists_for_user_query, get_modules_for_user_query
from .forms import AddModuleFormAjax, BindModuleToWhitelistsForm, ChangePasswordForm, LoginForm, RegistrationForm, AddModuleForm, AddWhitelistForm, AddPlateForm
from .models import User, Module, Whitelist, Plate
from .auth import admin_required

def init_app(app: Flask, sio: SocketIO):
    @app.route('/')
    @app.route('/index')
    def index():
        if current_user.is_authenticated:
            form = AddModuleFormAjax()

            edit_whitelist_form = BindModuleToWhitelistsForm()
            edit_whitelist_form.whitelists.choices = [(whitelist.id, whitelist.name) for whitelist in current_user.whitelists]

            if current_user.role == 'User':
                return render_template('index.html', modules=current_user.modules, form=form, edit_whitelist_form=edit_whitelist_form)
            elif current_user.role == 'Admin':
                return render_template('index.html', modules=Module.query.all())
        else:
            return render_template('index.html')


    @app.route('/add_module_ajax', methods=['POST'])
    @login_required
    def add_module_ajax():
        form = AddModuleFormAjax()

        if not form.validate_on_submit():
            result = {'errors': {}}
            for field in form:
                if field.errors:
                    result['errors'][field.name] = [error for error in field.errors]

            return result, 409
        else:
            module = Module.query.filter_by(unique_id=form.unique_id.data).first()
            module: Module
            assert module

            module.user = current_user
            db.session.commit()

            return '', 201




    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))

            login_user(user)

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')

            return redirect(url_for('index'))

        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'You, {user.username}, are now registered!')
            return redirect(url_for('login'))

        return render_template('register.html', form=form)

    @app.route('/add_module', methods=['GET', 'POST'])
    @login_required
    def add_module():
        form = AddModuleForm()
        if form.validate_on_submit():
            module = Module.query.filter_by(unique_id=form.unique_id.data).first()
            module.user = current_user
            db.session.commit()
            flash(f'Module {module.unique_id} is now registered to you')
            return redirect(url_for('index'))

        return render_template('add_module.html', form=form)

    @app.route('/user_profile', methods=['GET', 'POST'])
    @login_required
    def user_profile():
        form = ChangePasswordForm()
        if form.validate_on_submit():
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash(f'Password change was successful!')
            return redirect(url_for('index'))

        return render_template('user_profile.html', form=form)


    @app.route('/whitelists')
    @login_required
    def whitelists():
        return render_template('whitelists.html', whitelists=current_user.whitelists)


    @app.route('/edit_whitelist/<int:whitelist_id>', methods=['GET'])
    @login_required
    def edit_whitelist(whitelist_id):
        whitelist = get_whitelists_for_user_query(current_user) \
            .filter(Whitelist.id == whitelist_id).first()

        if whitelist is None:
            flash('Unknown whitelist id')
            return redirect(url_for('index'))

        form = AddPlateForm(whitelist_id = whitelist.id)

        return render_template('edit_whitelist.html', whitelist=whitelist, form=form)


    @app.route('/edit_whitelist/add_plate', methods=['POST'])
    @login_required
    def edit_whitelist_add_plate():
        form = AddPlateForm()

        if not form.validate_on_submit():
            result = {'errors': {}}
            for field in form:
                if field.errors:
                    result['errors'][field.name] = [error for error in field.errors]

            return result, 409
        else:
            plate = Plate(text=form.plate.data)
            whitelist = Whitelist.query.get(form.whitelist_id.data)
            whitelist.plates.append(plate)
            db.session.commit()
            flash(f'Added plate: {plate.text}')
            return {'plate': plate.text}, 201



    @app.route('/add_whitelist', methods=['GET','POST'])
    @login_required
    def add_whitelist():
        form = AddWhitelistForm()

        if form.validate_on_submit():
            whitelist = Whitelist(name=form.whitelist_name.data)
            whitelist.user = current_user
            db.session.add(whitelist)
            db.session.commit()

            flash('Added whitelist')
            return redirect(url_for('whitelists'))

        return render_template('add_whitelist.html', form=form)


    @app.route('/delete_plate_from_whitelist/<int:whitelist_id>', methods=['POST'])
    @login_required
    def delete_plate_from_whitelist(whitelist_id):
        whitelist = (Whitelist.query
            .filter(Whitelist.user_id == current_user.id)
            .filter(Whitelist.id == whitelist_id)).first()

        if whitelist is None:
            flash('Wrong whitelist')
            return redirect(url_for('index'))

        plate_id = request.args.get('plate_id', None)

        if plate_id is None:
            flash("Wrong plate")
            return redirect(url_for('edit_whitelist', whitelist_id=whitelist_id))

        plate = (Plate.query
            .filter(Plate.whitelist_id == whitelist_id)
            .filter(Plate.id == plate_id)).first()

        if plate is None:
            flash('Wrong plate')
            return redirect(url_for('edit_whitelist', whitelist_id=whitelist_id))

        whitelist.plates.remove(plate)
        flash(f'Sucessfully removed plate: {plate.text}')
        db.session.commit()
        return redirect(url_for('edit_whitelist', whitelist_id=whitelist_id))


    @app.route('/get_bound_whitelists_for_module')
    @login_required
    def get_bound_whitelists_for_module():
        unique_id = request.args['unique_id'] or None
        if unique_id is None:
            return {}, 409

        module = get_modules_for_user_query(current_user).filter(Module.unique_id == unique_id).first()

        if module is None:
            return {}, 409

        return {
            'whitelists_names': [whitelist.name for whitelist in module.whitelists]
        }, 201
