from flask import Blueprint, render_template, jsonify, request
from app import db
from app.models.data_pool_models import Image, DataPool

data_blueprint = Blueprint('bp_data', __name__, template_folder='templates')


@data_blueprint.route("/data_test")
def show_data():
    """
    Show a Datatables table with all columns and rows of the Image table from the db
    :return:
    """
    columns = DataPool.__table__.columns.keys() + Image.__table__.columns.keys()
    return render_template('main/data_page.html', columns=columns)


@data_blueprint.route("/api/data_test")
def get_data():
    """
    Get all entries of the Image table in json format
    """
    all_entries = db.session.query(Image).all()
    data = {
        "data": [entry.as_dict() for entry in all_entries]
    }
    return jsonify(data)
