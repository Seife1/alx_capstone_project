import os
import secrets
from PIL import Image
from bs4 import BeautifulSoup
from flask import render_template, url_for, flash, redirect, request, abort
from blog import app, db, bcrypt, mail
from flask_login import login_required, logout_user, login_user, current_user
from blog.forms import (RegistrationForm, LoginForm, SearchForm,
                        ForgotForm, ResetForm, UpdateAccountForm, PostForm)
from blog.models import User, Admin, Post, Category, Tag, Comment, Like
from flask_mail import Message


@app.route('/')
@app.route('/about')
@app.route('/contact')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route('/register', strict_slashes = False, methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created for {form.username.data}!', 'success')
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route('/login', strict_slashes = False, methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, password=form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash('You logged in successfuly !!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('user'))
        else:
            flash('Log in Unsuccessful, please check again', 'unsuccess')
    return render_template("login.html", title="Login", form=form)

# Extracting sample paragraph
def sample(content):
    soup = BeautifulSoup(content, 'html.parser')
    paragraphs = soup.find_all('p')
    if paragraphs:
        return paragraphs[0].get_text()
    return None

@app.route('/latest_post', strict_slashes=False)
@app.route('/user', strict_slashes = False)
@login_required
def user():
    posts = Post.query.order_by(Post.id.desc()).all()
    for post in posts:
        post.sample_para = sample(post.content)
    return render_template("latest_post.html", title="User Dashboard", posts=posts)


@app.route('/my_post', strict_slashes=False)
@login_required
def my_post():
    posts = Post.query.order_by(Post.id.desc()).all()
    for post in posts:
        post.sample_para = sample(post.content)
    return render_template("my_post.html", title="Your Posts", posts=posts)

# define and configure the path to store the uploaded images
def save_img(image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(image.filename)
    picture_fn = random_hex + f_ext
    picture_path =os.path.join(app.root_path, 'static/img', picture_fn)
    image.save(picture_path)
    return picture_fn


@app.route('/add_post', strict_slashes = False, methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    default_image = 'blogrammer.png'

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_img(form.picture.data)
        else:
            picture_file = default_image

        post = Post(title=form.title.data, content=form.content.data,
                    img=picture_file, author=current_user, read_time=form.read_time.data)
        category = Category(name=form.categories.data)
        db.session.add_all([post, category])
        post.categories_post.append(category)
        db.session.commit()

        flash('Your post has been created!', 'success')
        return redirect(url_for('user'))
    return render_template("add_post.html", title="New Post",
                           form=form, header="📚Write Your Own Post✍️", action = url_for('add_post'))


def save_pic(form_pic):
    """To save an uploaded picture in the file system"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pic.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile', picture_fn)
    form_pic.save(picture_path)

    """Resizing the image to minimize the storage"""
    output_size = (125, 125)
    i = Image.open(picture_path)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/profile', strict_slashes = False, methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_pic(form.picture.data)
            current_user.img = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your acount has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email        
    img_file = url_for('static', filename='profile/' + current_user.img)
    return render_template("profile.html", title="Dashboard",
                           img_file=img_file, form=form)


@app.route('/user/<int:post_id>', strict_slashes = False)
def pages(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("pages.html", title=post.title, post=post)


@app.route('/user/<int:post_id>/update',
           strict_slashes = False, methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.read_time = form.read_time.data

        if form.picture.data:
            picture_file = save_img(form.picture.data)
            post.img = picture_file

            post.categories_post = []
            for category_name in form.categories.data:
                category = Category.query.filter_by(name=category_name).first()
                if category:
                    post.categories_post.append(category)
        
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('pages', post_id=post.id))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.categories.data = [category.name for category in post.categories_post]
        form.read_time.data = post.read_time
    return render_template("add_post.html", title="Update Post",
                           form=form, header="📚Update Your Own Post✍️", action = url_for('update_post', post_id=post.id))


@app.route('/user/<int:post_id>/delete',
           strict_slashes = False, methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", 'success')
    return redirect(url_for('user'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('✍️Password Reset Request',
                  sender='seife4033@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
@app.route('/forgot', strict_slashes = False, methods=['GET', 'POST'])
def forgot():
    if current_user.is_authenticated:
        return redirect(url_for('user'))
    
    form=ForgotForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'success')
        return redirect(url_for('login'))
    
    return render_template("forgotpw.html", title="Forgot PW", form=form)


@app.route('/reset/<token>', strict_slashes = False, methods=['GET', 'POST'])
def reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('user'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for("forgot"))
    
    form=ResetForm()
    token = user.get_reset_token()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been updated successfully!, You are now able to login', 'success')
        return redirect(url_for('login'))
    
    return render_template("reset.html", title="Reset PW", form=form, token=token)


@app.context_processor #pass file to base file
def base():
    form=SearchForm()
    return dict(form=form)

@app.route('/search', methods=['POST'])
def search():
    form=SearchForm()
    posts = Post.query

    searched = form.search.data
    posts = posts.filter(Post.title.like('%' + searched + '%'))
    posts = posts.order_by(Post.id.desc()).all()
    return render_template("search.html", title="Searched Result",
                           posts=posts, form=form, searched=searched)

@app.route('/logout', strict_slashes = False)
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
