from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash



Team = db.Table('Team',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('pokemon_id', db.Integer, db.ForeignKey('pokemon.id'))                
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String)
    team = db.relationship('Pokemon', secondary=Team, backref='users')
    created_on = db.Column(db.DateTime, default=datetime.utcnow())

    # hashes our password when user signs up
    def hash_password(self, signup_password):
        return generate_password_hash(signup_password)
    
    # This method will assign our columns with their respective values
    def from_dict(self, user_data):
        self.first_name = user_data['first_name']
        self.last_name = user_data['last_name']
        self.email = user_data['email']
        self.password = self.hash_password(user_data['password'])


class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    sprite = db.Column(db.String)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    defense = db.Column(db.Integer)

    # This method will assign our columns with their respective values
    def from_dict(self, pokemon_data):
        self.id = pokemon_data['id']
        self.name = pokemon_data['name']
        self.sprite = pokemon_data['sprite']
        self.hp = pokemon_data['hp']
        self.attack = pokemon_data['attack']
        self.defense = pokemon_data['defense']




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)