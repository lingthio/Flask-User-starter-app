from flask import Blueprint, redirect, render_template, current_app
from flask import request, url_for
from flask.json import jsonify
from flask_user import current_user, login_required, roles_required
from app import db, flask_admin
from flask_admin.contrib.sqla import ModelView
from app.models.user_models import User, Role
from app.models.project_models import Project
from app.models.data_pool_models import DataPool, Image

admin_blueprint = Blueprint('bp_admin', __name__, template_folder='templates')


# The Admin page is accessible to users with the 'admin' role
@admin_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    projects = db.session.query(Project).all()
    projects = [p.name for p in projects]

    users = db.session.query(User).all()
    users = [u.first_name + " " + u.last_name for u in users]

    return render_template('main/admin_page.html', projects=projects, users=users)


@admin_blueprint.route("/admin/data")
def get_data():
    """
    Get all entries of the Image table in json format
    """
    all_entries = db.session.query(Image).all()
    data = {
        "data": [entry.as_dict() for entry in all_entries]
    }
    return jsonify(data)

flask_admin.add_view(ModelView(User, db.session))
flask_admin.add_view(ModelView(Role, db.session))
flask_admin.add_view(ModelView(Project, db.session))
flask_admin.add_view(ModelView(DataPool, db.session))