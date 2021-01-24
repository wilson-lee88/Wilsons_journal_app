import forms
import models

from flask_bcrypt import check_password_hash

from flask import (Flask, flash, g, render_template, redirect, request,
                   url_for)

from flask_login import (current_user, LoginManager, login_required,
                         login_user, logout_user)

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
    g.user = current_user.get_id()


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
    return render_template('register.html', form=form)


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
            flash('Your email or password does not exist', 'alert')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in", 'success')
                return redirect(url_for('index'))
            else:
                flash('Your email or password does not exist', 'alert')
    return render_template('login.html', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/entries', methods=['GET', 'POST'])
@app.route('/entries/tags/<int:tag_id>', methods=['GET', 'POST'])
def index(tag_id=None):
    """pulls up 25 entries to display on index page"""
    if tag_id:
        posts = models.Entries.select().join(
            models.TagEntryRel, on=models.TagEntryRel.from_entry
        ).where(models.TagEntryRel.to_tag == tag_id)
    else:
        posts = models.Entries.select().limit(25).order_by(
            models.Entries.date.desc())
    return render_template('index.html', posts=posts)


@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def new_post():
    """new post form"""
    form = forms.EntryForm()
    if form.validate_on_submit():
        flash('You have made an entry!', 'success')
        try:
            models.Entries.create_entry(
                user_id=g.user,
                title=form.title.data.strip(),
                date=form.date.data,
                time_spent=form.time_spent.data,
                learned=form.learned.data,
                resources=form.resources.data,
            )
        except ValueError:
            return redirect(url_for('index'))
        tags = form.tags.data.strip().split()
        for tag in tags:
            if models.DoesNotExist:
                try:
                    models.Tags.create_tag(
                        tag_name=tag
                    )
                except ValueError:
                    pass
                models.TagEntryRel.create_rel(
                    models.Entries.select().order_by(models.Entries.id.desc()).get(),
                    models.Tags.select().where(models.Tags.tag_name == tag).get()
                )
            else:
                models.TagEntryRel.create_rel(
                    models.Entries.select().order_by(models.Entries.id.desc()).get(),
                    models.Tags.select().where(models.Tags.tag_name == tag)
                )

        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/<int:entry_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(entry_id):
    entry = models.Entries.get_by_id(entry_id)

    tags = models.Entries.tags(entry_id)
    string = []
    for tag in tags:
        string.append(tag.tag_name)
    form = forms.EntryForm()
    if request.method == 'GET':
        form.learned.data = entry.learned
        form.resources.data = entry.resources
        form.tags.data = ' '.join(string)
    if form.validate_on_submit():
        models.Entries.update(
            user_id=g.user,
            title=form.title.data,
            date=form.date.data,
            time_spent=form.time_spent.data,
            learned=form.learned.data,
            resources=form.resources.data
        ).where(models.Entries.id == entry.id).execute()
        new_tags = form.tags.data.split()

        tag_data = models.Tags.select()
        all_tags = []
        for tags in tag_data:
            all_tags.append(tags.tag_name)

        tags = entry.tags()
        current_tags = []
        for tag in tags:
            current_tags.append(tag.tag_name)

        for tag in new_tags:
            if tag not in current_tags:
                if tag not in all_tags:
                    models.Tags.create_tag(
                        tag_name=tag
                    )
                    models.TagEntryRel.create_rel(
                        models.Entries.get_by_id(entry.id),
                        models.Tags.select().order_by(models.Tags.id.desc()).get()
                    )
                else:
                    models.TagEntryRel.create_rel(
                        models.Entries.get_by_id(entry.id),
                        models.Tags.select().where(
                            models.Tags.tag_name == tag
                        )
                    )
        for tag in current_tags:
            if tag not in new_tags:
                models.TagEntryRel.get(
                    from_entry=models.Entries.get(
                        models.Entries.id == entry.id),
                    to_tag=models.Tags.get(
                        models.Tags.tag_name == tag)
                ).delete_instance()
        return redirect(url_for('index'))

    return render_template('edit.html', form=form, entry=entry)


@app.route('/entries/<int:entry_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(entry_id):
    tag_rel = models.TagEntryRel.select().where(
        models.TagEntryRel.from_entry == entry_id
    )
    for tag in tag_rel:
        tag.delete_instance()
    entry = models.Entries.get_by_id(entry_id)
    entry.delete_instance()
    return redirect(url_for('index'))


@app.route('/entries/<int:entry_id>', methods=['GET', 'POST'])
def details(entry_id):
    entries = models.Entries.get_by_id(entry_id)
    tags = models.Entries.tags(entry_id)
    return render_template('detail.html', entries=entries, tags=tags)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out!", 'success')
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


if __name__ == '__main__':
    models.initialize()

    models.Entries.create_entry(
        user_id=1,
        title="first entry",
        date="2021-01-23",
        time_spent=1,
        learned="Python",
        resources="Treehouse"
    )

    app.run(debug=True)
