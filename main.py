from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Form
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import datetime
'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True,
                                       nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class NewPostForm(FlaskForm):
    title = StringField("Blog Post Title")
    subtitle = StringField("Subtitle")
    author_name = StringField("Your Name")
    img_url = StringField("Blog Image URL")
    body=CKEditorField('Body')
    submit = SubmitField("Submit Post")


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    data = db.session.execute(db.select(BlogPost))
    posts = data.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route('/<int:post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route('/new-post', methods=["GET", "POST"])
def new_post():
    form=NewPostForm()
    if form.validate_on_submit():
        new_entry=BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=datetime.datetime.now().strftime("%B %d, %Y"),
            body=form.body.data,
            author=form.author_name.data,
            img_url=form.img_url.data
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    id = db.get_or_404(BlogPost, post_id)
    form = NewPostForm(
    title=id.title,
    subtitle=id.subtitle,
    img_url=id.img_url,
    author_name=id.author,
    body=id.body
    )
    if form.validate_on_submit():
        id.title=form.title.data
        id.subtitle = form.subtitle.data
        id.img_url = form.img_url.data
        id.author = form.author_name.data
        id.body = form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=id.id))
    return render_template("make-post.html", post_id=id, form=form)

@app.route('/delete/<post_id>', methods=["GET", "POST"])
def delete_post(post_id):
    id = db.get_or_404(BlogPost, post_id)
    db.session.delete(id)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
