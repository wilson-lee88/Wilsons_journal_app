import forms
import models

from flask import (Flask, flash, g, render_template, redirect,
                   url_for)

app = Flask(__name__, template_folder='templates')
app.secret_key = '249889fy231fe8fyw3e8h$%#$g=+"::'


@app.before_request
def before_request():
    """"connect to the database before each request"""
    g.db = models.db
    g.db.connect()


@app.after_request
def after_request(response):
    """closes database connection after each request"""
    g.db.close()
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    """pulls up 25 entries to display on index page"""
    posts = models.Entries.select().limit(25).order_by(
        models.Entries.date.desc())
    return render_template('index.html', posts=posts)


@app.route('/new', methods=('GET', 'POST'))
def new_post():
    """new post form"""
    form = forms.EntryForm()
    if form.validate_on_submit():
        flash('You have made an entry!', 'success')
        try:
            models.Entries.create_entry(
                title=form.title.data.strip(),
                date=form.date.data,
                time_spent=form.time_spent.data,
                learned=form.learned.data,
                resources=form.resources.data,
            )
        except ValueError:
            return redirect(url_for('index'))
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/edit/<int:entry_id>', methods=('GET', 'POST'))
def edit(entry_id):
    entry = models.Entries.get_by_id(entry_id)
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.Entries.update(
            title=form.title.data,
            date=form.date.data,
            time_spent=form.time_spent.data,
            learned=form.learned.data,
            resources=form.resources.data
        ).where(models.Entries.id == entry.id).execute()
        return redirect(url_for('index'))
    return render_template('edit.html', entry=entry, form=form)


@app.route('/delete/<int:entry_id>', methods=['GET', 'POST'])
def delete(entry_id):
    entry = models.Entries.get_by_id(entry_id)
    entry.delete_instance()
    return redirect(url_for('index'))


@app.route('/details/<int:entry_id>', methods=['GET', 'POST'])
def details(entry_id):
    entries = models.Entries.get_by_id(entry_id)
    return render_template('detail.html', entries=entries)


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404


if __name__ == '__main__':
    models.initialize()
    app.run(debug=True)
