import forms
import models

from flask import (abort, Flask, flash, g, render_template, redirect,
                   url_for)

from flask_login import (current_user, LoginManager, login_required,
                         login_user, logout_user)

from flask_bcrypt import check_password_hash

app = Flask(__name__, template_folder='templates')
app.secret_key = '249889fy231fe8fyw3e8h$%#$g=+"::'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.before_request
def before_request():
    """"connect to the database before each request"""
    g.db = models.db
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """closes database connection after each request"""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash('You registered!', 'success')
        models.User.create_user(
            username=form.username.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('new_user.html', form=form)


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.user_name == form.username.data)
        except models.DoesNotExist:
            flash('Your email or password does not exist')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in", 'success')
                return redirect(url_for('index'))
            else:
                flash('Your email or password does not exist')
    return render_template('login.html', form=form)


@app.route('/', methods=['GET'])
@app.route('/<int:user_id>', methods=['GET'])
def index(user_id=None):
    if user_id:
        try:
            posts = models.Entries.select().where(
                models.Entries.id == user_id).limit(25).order_by(
                models.Entries.date.desc())
            return render_template('index.html', user_posts=posts)
        except models.DoesNotExist:
            abort(404)
    else:
        posts = models.Entries.select().limit(25).order_by(
            models.Entries.date.desc())
        return render_template('index.html', user_posts=posts)


@app.route('/tag/<int:tag_id>', methods=['GET'])
@login_required
def listing(tag_id):
    tags = models.Tags.select().where(models.Tags.id == tag_id)


@app.route('/entries/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = forms.EntryForm()
    if form.validate_on_submit():
        try:
            models.Entries.create_entry(
                current_user.get_id(),
                form.title.data.strip(),
                form.date.data,
                form.time_spent.data,
                form.learned.data,
                form.resources.data,
            )
        except ValueError:
            return redirect(url_for('exists'))

        tags = form.tags.data.split(', ')
        exist_tags = []
        existing = models.Tags.select()
        for tag in tags:
            if tag not in existing.tag_name:
                models.TagPostRel.create_rel(
                    models.Entries.get(models.Entries.title **
                                       form.title.data,
                                       models.Tags.get(models.Tags.tag_name **
                                                       tag))
                )
            else:
                models.Tags.create_tag(tag)
                models.TagPostRel.create_rel(
                    models.Entries.get(models.Entries.title **
                                       form.title.data,
                                       models.Tags.get(models.Tags.tag_name **
                                                       tag))
                )
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit(entry_id):
    try:
        entry = models.Entries.get_by_id(entry_id)
    except models.DoesNotExist:
        redirect(url_for('error'))

    cur_tag = []
    for tag in models.Entries.get_by_id(entry_id).get_tags():
        cur_tag.append(tag.tag_name)

    form = forms.EntryForm()

    if form.validate_on_submit():
        if entry.user_id == current_user.id:
            form.title.data = entry.title
            form.date.data = entry.date
            form.time_spent = entry.time_spent
            form.learned = entry.learned
            form.resources = entry.resources
            new_tags = form.tags.split(', ')

            for tag in cur_tag:
                if tag not in new_tags:
                    models.TagPostRel.get(
                        from_entry=entry.id,
                        to_tag=models.Tags.get().where(models.Tags.tag_name == tag)
                    ).delete_instance()

            for tag in new_tags:
                if tag not in cur_tag:
                    try:
                        models.Tags.create_tag(
                            tag_name=tag
                        )
                    except models.IntegrityError:
                        pass
                    try:
                        models.TagPostRel.create_rel(
                            entry.id,
                            models.Tags.get().where(
                                models.Tags.tag_name == tag
                            )
                        )
                    except models.IntegrityError:
                        pass

            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('edit.html', entry=entry, form=form)


@app.route('/details/<int:entry_id>')
@login_required
def details(entry_id):
    entries = models.Entries.select().where(models.Entries.id == entry_id)
    return render_template('detail.html', entries=entries)


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out!", "success")
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


if __name__ == '__main__':
    models.initialize()
    app.run(debug=True)
'''
    models.Entries.get().where(
        models.Entries.title == "learned flask").delete_instance()

    models.User.get().where(
        models.User.user_name == "wilsonlee").delete_instance()
'''
models.User.create(
        user_name="wilsonlee",
        password="123456"
    )

models.Entries.create(
        user_id=1,
        title="learned flask",
        time_spent="6",
        learned="how to make a web app",
        resources="Treehouse and stack overflow",
        tags="career, programming, life "
    )
