import json
import os
from datetime import datetime

from dateutil.parser import parse as parse_date_string
from flask import request, jsonify, redirect
from flask_login import current_user
from flask_user import login_required


from app import app
from app import db
from app.models.user_models import User


@app.route("/data/all_users", methods=['GET'])
@login_required
def all_users():
    """
    View that returns all users of the database
    """
    r = request
    users = db.session.query(User).all()
    data = {
        "data": [user.as_dict() for user in users],
    }
    return jsonify(data)


@app.route("/data/delete_user")
@login_required
def delete_user():
    """
    Delete user with specified id from database
    """
    r = request
    user_id = request.headers["user_id"]
    db.session.query(User).filter(User.id == user_id).delete()
    db.session.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/data/new_user", methods=["POST"])
@login_required
def new_user():
    """
    Add new user
    """
    form = request.form
    first_name = form["first_name"]
    last_name = form["last_name"]
    email = form["email"]
    password = form["password"]

    user = User(first_name=first_name, last_name=last_name, email=email, password=password, active=True)
    db.session.add(user)
    db.session.commit()

    return redirect(request.referrer)


