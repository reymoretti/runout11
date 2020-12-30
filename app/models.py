from app import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from flask import session


class Customer(db.Model, UserMixin):
    __tablename__='Customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False,  index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    shopping_list = db.relationship('OfferInShoppingList', backref='list', lazy=True, cascade="all, delete")

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod #we want token to be the only argument
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Customer.query.get(user_id)

    def __repr__(self):
        return "Customer(%r, %r, %r)" % (self.username, self.email, self.image_file)

class Foodseller(db.Model, UserMixin):
    __tablename__ = 'Foodseller'
    id = db.Column(db.Integer, primary_key=True)
    foodsellerName = db.Column(db.String(20), unique=True, nullable=False,  index=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    city = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    opening_hours = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    offers = db.relationship('Offer', backref='seller', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Foodseller.query.get(user_id)

    def __repr__(self):
        return "Foodseller(%r, %r, %r)" % (self.foodsellerName, self.image_file, self.email)


class Offer(db.Model):
    __tablename__ = 'Offer'
    id = db.Column(db.Integer, primary_key=True)
    offer_name = db.Column(db.String(20), nullable=False, index=True)
    brand = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100))
    exp_date = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Float, nullable=False)
    percentage_discount = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    foodseller_id = db.Column(db.Integer, db.ForeignKey('Foodseller.id'), nullable=False)
    shopping_list = db.relationship('OfferInShoppingList', backref='alist', lazy=True, cascade="all, delete")

    def __repr__(self):
        return "Offer(%r, %r, %r)" % (self.offer_name, self.foodseller_id, self.exp_date)

class OfferInShoppingList(db.Model):
    __tablename__ = 'OfferInShoppingList'
    id = db.Column(db.Integer, primary_key=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('Offer.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customer.id'), nullable=False)

    def __repr__(self):
        return "OfferInShoppingList(%r, %r)" % (self.offer_id, self.customer_id)

@login_manager.user_loader
def load_user(user_id):
    if session['type'] == 'customer':
        return Customer.query.get(int(user_id))
    elif session['type'] == 'foodseller':
        return Foodseller.query.get(int(user_id))
    else:
        return None




