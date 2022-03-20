from datetime import datetime
from todolist import db, loginManager
from flask_login import UserMixin

@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    lists = db.relationship('List', backref='owner', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"User('{self.name}','{self.email}','{self.image_file}')"

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modified_on = db.Column(db.DateTime, nullable=True)
    is_important = db.Column(db.Integer, nullable=False, default=0)
    color = db.Column(db.String(20), nullable=False, default='light')
    is_archived = db.Column(db.Integer, nullable=False, default=0)
    tasks = db.relationship('Task', backref='collection', lazy=True, cascade="all, delete-orphan")
    

    def __repr__(self):
        return f"List '{self.title}','{self.created_on}'"


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_completed = db.Column(db.Integer, nullable=False, default=0)
    completed_on = db.Column(db.DateTime, nullable=True)
    modified_on = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"Task '{self.content}','{self.created_on}'"