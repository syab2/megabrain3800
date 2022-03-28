from turtle import title
from flask import Flask, render_template, redirect, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

import random

from data import db_session
from data.users import User
from data.games import Game
from data.edit import EditProfile

from forms.login import LoginForm
from forms.register import RegisterForm
from forms.game import GameForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/profile')
def profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('profile.html', title='Профиль', user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    db_sess = db_session.create_session()
    games = db_sess.query(Game).all()
    try:
        user = db_sess.query(User).filter(User.id == current_user.id)  
        return render_template('index.html', user=user, current_user=current_user, games=games, title='Главная')
    except Exception:
        return render_template('index.html', current_user=current_user, games=games, title='Главная')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.set_password(form.password.data)
        user.icon = '/static/img/user-icon.png'
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/add_game', methods=["GET", "POST"])
@login_required
def add_game():
    form = GameForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        game = Game()

        game.title = form.title.data
        game.description = form.description.data

        filename = str(''.join([str(random.randint(1, 10)) for x in range(5)])) + '_' + str(secure_filename(form.icon.data.filename))
        form.icon.data.save(f'static/img/{filename}')
        game.icon = url_for('static', filename=f'img/{filename}')

        filename1 = str(''.join([str(random.randint(1, 10)) for x in range(5)])) + '_' + str(secure_filename(form.archive.data.filename))
        form.archive.data.save(f'static/games/{filename1}')
        game.archive = url_for('static', filename=f'games/{filename1}')

        current_user.games.append(game)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('game_add.html', form=form, title='Добавление игры')


@app.route('/edit_profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfile()
    if request.method == 'GET':     
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        form.nickname.data = user.nickname
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.nickname = form.nickname.data
        filename = str(''.join([str(random.randint(1, 10)) for x in range(5)])) + '_' + str(secure_filename(form.icon.data.filename))
        form.icon.data.save(f'static/img/{filename}')
        user.icon = url_for('static', filename=f'img/{filename}')
        db_sess.commit()        
        return redirect('/profile')
    return render_template('edit_profile.html', form=form, title='Редактирование профиля', user=user)



def main():
    db_session.global_init('db/mega.db')
    app.run()


if __name__ == '__main__':
    main()
