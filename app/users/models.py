# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user import UserMixin
from app.app_and_db import db

# Define the User model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_profile_id = db.Column(db.Integer(), db.ForeignKey('user_profile.id', ondelete='CASCADE'))

    # Flask-User fields
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

    # Relationships
    user_profile = db.relationship('UserProfile', uselist=False, backref="user")


# Define the UserProfile model
#   The User model contains login-related fields
#   The UserProfile model contains additional User fields
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False, server_default='')
    last_name = db.Column(db.String(50), nullable=False, server_default='')

    # def full_name(self):
    #     """ Return 'first_name last_name' """
    #     # Handle records with an empty first_name or an empty last_name
    #     name = self.first_name
    #     name += ' ' if self.first_name and self.last_name else ''
    #     name += self.last_name
    #     return name


# Define the Role model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))


# Define the UserRoles association model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

    # Relationships
    user = db.relationship('User', backref='roles')
    role = db.relationship('Role', backref='users')

