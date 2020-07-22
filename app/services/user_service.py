import json
import os
from datetime import datetime
import logging

from dateutil.parser import parse as parse_date_string
from flask import Blueprint, request, jsonify, redirect
from flask_login import current_user
from flask_user import login_required

from app import app, db
from app.models.user_models import User

from app.controllers import user_controller

from app.utils import technical_admin_required, project_admin_required, project_reviewer_required, project_user_required


# Define the blueprint: 'user_service', set its url prefix: app.url/user
user_service = Blueprint('user_service', __name__, url_prefix='/user')

"""
Returns all users of the database
"""
@user_service.route("/all", methods=['GET'])
@login_required
def all_users():

    users = user_controller.get_all_users()

    data = {
        "users": [user.as_dict() for user in users],
    }

    return jsonify(data)

"""
Add new user
"""
@user_service.route("", methods=["POST"])
@login_required
@technical_admin_required
def new_user():

    # check, if the request is fired by a form or by ajax call
    is_form_request = hasattr(request, 'form')

    app.logger.info("Creating user")

    user_data = None
    if is_form_request:
        user_data = request.form
    else:
        user_data = json.loads(request.data)
        
    first_name = user_data["first_name"]
    last_name = user_data["last_name"]
    email = user_data["email"]
    password = user_data["password"]

    user = user_controller.find_or_create_user(first_name=first_name, last_name=last_name, email=email, password=password)

    data = {
        "user": user.as_dict()
    }

    if is_form_request:
        # when request fired by form, send user to the same page where the form is
        return redirect(request.referrer)
    else:
        # else send him the user object which has been created (or not created, in that case the member "user" of data is null)
        return jsonify(data)

"""
Delete user with specified id from database
"""
@user_service.route("", methods=['GET'])
@login_required
def get_user_by_id():

    # url encoded parameters
    # example: /api/user?id=1 , /api/user?email=admin@issm.org
    user_id = request.args.get('id')
    user_email = request.args.get('email')

    app.logger.info(f"get_user_by_id: getting user by id {user_id} or email {user_email}")

    user = user_controller.find_user(id=user_id, email=user_email)

    app.logger.info(f"user exist {user != None}")

    data = {
        "user": user.as_dict()
    }

    return jsonify(data)


"""
Delete user with specified id from database
"""
@user_service.route("", methods=['DELETE'])
@login_required
@technical_admin_required
def delete_user_by_id():

    user_id = request.args.get('id')
    app.logger.info(f"delete_user_by_id: deleting user by id {user_id}")

    user = user_controller.find_user(id=user_id)

    if user:
        is_user_deleted = user_controller.delete_user(user)
    else:
        is_user_deleted = False

    app.logger.info(f"deleted {is_user_deleted}")

    data = {
        "success": is_user_deleted
    }

    return jsonify(data)

