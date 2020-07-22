import logging

from flask import current_app as app

from app import db

from app.models.user_models import User, Role

"""
Retrieves ALL users from the database
"""
def get_all_users():
    users = db.session.query(User).all()

    return users

"""
Tries to find a user by id and if id is not given, email

If non of those parameters are set, prints error and returns None
"""
def find_user(id=None, email=None):

    if id:
        user = User.query.get(id)
    elif email:
        user = User.query.filter(User.email == email).first()
    else:
        app.logger.error("No parameters given for user search")
        
        return None
    

    return user

"""
Creates a new user by given parameters

@param roles this is the Flask-User parameter roles, not the ISSM roles. Therefore this can be Admin (Technical Admin) or User
"""
def create_user(first_name, last_name, email, password, roles=None):

    user = User(email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                active=True)

    if roles:
        user.roles.extend(roles)
    else:
        user_role = Role.query.filter(Role.name == 'user').first()
        if user_role is not None:
            user.roles.append(user_role)

    db.session.add(user)
    db.session.commit()

    return user

"""
Only disables a user (so he can't login?)
"""
def disable_user(user):

    if user:
        user.active = False
        db.session.add(user)
        db.session.commit()

        return True
    else:
        return False

"""
Deletes a user for good
"""
def delete_user(user):

    if user:
        db.session.delete(user)
        db.session.commit()

        return True
    else:
        return False

"""
Tries to find an existing user by mail and if he does not exist, creates him
"""
def find_or_create_user(first_name, last_name, email, password, roles=None):
    
    user = find_user(email=email)

    if not user:
        user = create_user(first_name=first_name, last_name=last_name, email=email, password=password, roles=roles)

    return user