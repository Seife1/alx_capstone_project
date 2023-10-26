"""
Database Module
"""
from blog import db, login_manager, app
from datetime import datetime, timedelta
from flask_login import UserMixin
import jwt

@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Stores information about the users who create and manage the blog posts"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), nullable=False, unique=True)
    email = db.Column('email', db.String(150 ), nullable=False, unique=True)
    img = db.Column('img', db.String(100), nullable=False, default='Avatar.jpg')
    password = db.Column('password', db.String(60), nullable=False)
    rgr_date = db.Column('registration_date', db.DateTime, default=datetime.utcnow)
    admin_id = db.Column('admin_id', db.Integer, db.ForeignKey('admins.id'))

    
    # SQLAlchemy Relationship patterns - User have one to many relationship with posts
    posts = db.relationship('Post', backref='author', lazy=False)

    # SQLAlchemy Relationship patterns - User have one to many relationship with comment
    comments = db.relationship('Comment', backref='comment_me', lazy=False)

    # SQLAlchemy Relationship patterns - User have one to many relationship with like
    likes = db.relationship('Like', backref='like_me', lazy=False)

    # # SQLAlchemy Relationship patterns - Blog post have one to many relationship with Media
    # medias = db.relationship('Media', backref='media_for', lazy=False)


    # Email password reset
    def get_reset_token(self, expires_sec=180):
         exp_time = datetime.utcnow() + timedelta(seconds=expires_sec)
         token = jwt.encode({'user_id': self.id, 'exp': exp_time},
                            app.config['SECRET_KEY'], algorithm='HS256')
         return token
        # s = Serializer(app.config['SECRET_KEY'], expires_sec)
        # return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        # s = Serializer(app.config['SECRET_KEY'])
        # try:
        #      user_id = s.loads(token)['user_id']
        # except:
        #      return None
        # return User.query.get(user_id)
        try:
             payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
             user_id = payload['user_id']
             exp_time = payload['exp']

             if datetime.utcnow() <= datetime.fromtimestamp(exp_time):
                  return User.query.get(user_id)
             else:
                  return None
        except jwt.ExpiredSignatureError:
             return None
                  

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.img}', '{self.rgr_date}')"


class Admin(db.Model, UserMixin):
    """Stores information about the admins who create and manage the blog posts and users also"""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), nullable=False, unique=True)
    img = db.Column('image', db.String(30), nullable=False, default='Avatar.jpg')
    email = db.Column('email', db.String(30), nullable=False, unique=True)
    password = db.Column('password', db.String(60), nullable=False)
    rgr_date = db.Column('registration_date', db.DateTime, default=datetime.utcnow)

    # SQLAlchemy Relationship patterns - Admin have one to many relationship with posts
    posts = db.relationship('Post', backref='admin_poster', lazy=False)

    # SQLAlchemy Relationship patterns - Admin have one to many relationship with comment
    comments = db.relationship('Comment', backref='admin_comment', lazy=False)

    # SQLAlchemy Relationship patterns - Admin have one to many relationship with like
    likes = db.relationship('Like', backref='admin_like', lazy=False)

    # SQLAlchemy Relationship patterns - Admin have one to many relationship with user
    users = db.relationship('User', backref='admin_user', lazy=False)

    # # SQLAlchemy Relationship patterns - Blog post have one to many relationship with Media
    # medias = db.relationship('Media', backref='admin_media', lazy=False)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.img}', '{self.rgr_date}')"


# Blog-post and category association - Relationship pattern N:N
blog_category = db.Table('blog_category',
                        db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                        db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
)


# Blog-post and tag association - Relationship pattern N:N
blog_tag = db.Table('blog_tag',
                        db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
                        db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

class Tag(db.Model):
    """stores a list of tags that can be associated with blog posts"""
    __tablename__ = "tags"

    id = db.Column('id', db.Integer, primary_key=True)
    tag = db.Column('tag', db.String(50), nullable=False, unique=True)

    # N:N relationship - Post
    posts_tag = db.relationship('Post', secondary=blog_tag, back_populates='tags_post', lazy=True)


    def __repr__(self):
            return f"User('{self.tag}')"


class Post(db.Model):
    """Stores information about individual blog posts"""
    __tablename__ = "posts"

    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('title', db.String(50), nullable=False)
    content = db.Column('content', db.Text, nullable=False)
    date_posted = db.Column('date_posted', db.DateTime, nullable=False, default=datetime.utcnow)
    img = db.Column('image', db.String(30), nullable=False, default='blogrammer.png')
    read_time = db.Column('read_time', db.String(10), nullable=False)

    # Foreign key relationship with User
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    # Foreign key relationship with Admin
    admin_id = db.Column('admin_id', db.Integer, db.ForeignKey('admins.id', ondelete="CASCADE"))

    # SQLAlchemy Relationship patterns - Blog post have one to many relationship with comment
    comments = db.relationship('Comment', backref='post_comment', lazy=False)

    # SQLAlchemy Relationship patterns - Blog post have one to many relationship with like
    likes = db.relationship('Like', backref='post_like', lazy=False)

    # # SQLAlchemy Relationship patterns - Blog post have one to many relationship with Media
    # medias = db.relationship('Media', backref='post_media', lazy=False)

    # N:N relationship - Category
    categories_post = db.relationship('Category', secondary=blog_category, back_populates='posts_category', lazy=True)

    # N:N relationship - Tag
    tags_post = db.relationship('Tag', secondary=blog_tag, back_populates='posts_tag', lazy=True)


    def __repr__(self):
            return f"User('{self.title}', '{self.content}', '{self.date_posted}', '{self.read_time}')"


class Category(db.Model):
    """Stores a list of blog post categories"""
    __tablename__ = "categories"

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(50), nullable=False)

    # N:N relationship
    posts_category = db.relationship('Post', secondary=blog_category, back_populates='categories_post', lazy=True)

    def __repr__(self):
        return f"Category('{self.name}')"


class Comment(db.Model):
    """Stores user comments on blog posts"""
    __tablename__ = "comments"

    id = db.Column('id', db.Integer, primary_key=True)
    timestamp = db.Column('time', db.DateTime, default=datetime.utcnow)
    text = db.Column('text', db.Text, nullable=False)

    # Foreign key relationship with User
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin_id = db.Column('admin_id', db.Integer, db.ForeignKey('admins.id'))

    # Foreign key relationship with Post
    post_id = db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), nullable=False)


    def __repr__(self):
        return f"User('{self.text}', '{self.timestamp}')"


class Like(db.Model):
    """Tracks the likes for blog posts"""
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    like = db.Column('like', db.String(50), nullable=False, unique=True)

    # Foreign key relationship with User
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin_id = db.Column('admin_id', db.Integer, db.ForeignKey('admins.id'))

    # Foreign key relationship with Post
    post_id = db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), nullable=False)


    def __repr__(self):
        return f"User('{self.like}')"

# class Media(db.Model):
#     """A table used to store the video and image files"""
#     __tablename__ = "medias"

#     id = db.Column('ID', db.Integer, primary_key=True)
#     img = db.Column('Img', db.String(30), nullable=False, default='blogrammer.png')
#     description = db.Column('Description', db.Text)

#     # Foreign key relationship with Post
#     post_id = db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))

#     # Foreign key relationship with Admin
#     admin_id = db.Column('admin_id', db.Integer, db.ForeignKey('admins.id'))

#     # Foreign key relationship with User
#     user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))


#     def __repr__(self):
#         return f"User('{self.img}', '{self.description}')"
    
