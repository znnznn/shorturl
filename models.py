import datetime

from flask_login import UserMixin

from shorturl import db, login_manager


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_url = db.Column(db.String, nullable=False)
    key = db.Column(db.String(25), unique=True, nullable=False)
    clicks = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return self.key


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100))
    create_at = db.Column(db.Date, default=datetime.datetime.now)
    url = db.relationship('Url', backref='user', lazy=True)

    def __repr__(self):
        return self.email


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def obj_add(obj):
    db.session.add(obj)
    db.session.commit()


def obj_delete(obj):
    db.session.delete(obj)
    db.session.commit()