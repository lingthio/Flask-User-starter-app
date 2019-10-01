from flask import Blueprint, redirect, render_template, current_app
from flask import request, url_for
from flask_user import current_user, login_required, roles_required
from app import db, flask_admin
from flask_admin.contrib.sqla import ModelView
from app.models.user_models import User, Role
from app.models.project_models import Project
from app.models.data_pool_models import DataPool


admin_blueprint = Blueprint('bp_admin', __name__, template_folder='templates')

# The Admin page is accessible to users with the 'admin' role
@admin_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('main/admin_page.html')

flask_admin.add_view(ModelView(User, db.session))
flask_admin.add_view(ModelView(Role, db.session))
flask_admin.add_view(ModelView(Project, db.session))
flask_admin.add_view(ModelView(DataPool, db.session))