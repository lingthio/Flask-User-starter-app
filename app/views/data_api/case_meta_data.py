import json
import os
from datetime import datetime

from dateutil.parser import parse as parse_date_string
from flask import request, jsonify
from flask_login import current_user
from flask_user import login_required
from sqlalchemy import DateTime, Date

from app import app, local_settings
from app import db
from app.models.data_pool_models import Image, ManualSegmentation, Message, Modality, ContrastType
from app.models.project_models import Project


@app.route("/data/update_image_meta_data", methods=['POST'])
@login_required
def update_image_meta_data():
    """
    View for handling changes to datapool objects (assignments etc.)
    """
    image_object = request.json
    segmentation_object = image_object["manual_segmentation"]

    # Find the image and segmentation object
    image = db.session.query(Image).filter(Image.id == image_object["id"]).first()
    manual_segmentation = image.manual_segmentation

    # Update values for image
    for column in Image.__table__.columns:
        column_name = column.name
        if column_name in image_object:
            value = image_object[column_name]
            if value is None:
                continue
            if value is not None and type(column.type) == DateTime or type(column.type) == Date:
                value = datetime.strptime(image_object[column_name], '%a, %d %b %Y %H:%M:%S %Z')
            setattr(image, column_name, value)

    # Contrast type and modality
    modality_name = image_object["modality"]
    modality = db.session.query(Modality).filter(Modality.name == modality_name).filter(
        Modality.project_id == image.project_id).first()
    image.modality = modality

    contrast_type_name = image_object["contrast_type"]
    contrast_type = db.session.query(ContrastType).filter(ContrastType.name == contrast_type_name).filter(
        ContrastType.project_id == image.project_id).first()

    image.contrast_type = contrast_type

    # Update values for segmentation
    for column in ManualSegmentation.__table__.columns:
        column_name = column.name
        value = segmentation_object[column_name]
        if value is not None and type(column.type) == DateTime or type(column.type) == Date:
            value = parse_date_string(value)

        setattr(manual_segmentation, column_name, value)

    # Append messages
    if "new_message" in segmentation_object:
        message = segmentation_object["new_message"]
        message = Message(user=current_user, date=datetime.now(), message=message,
                          manual_segmentation=manual_segmentation, manual_segmentation_id=manual_segmentation.id)
        manual_segmentation.messages.append(message)

    db.session.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/data/send_message", methods=['GET'])
@login_required
def send_message():
    """
    Handle new messages appended to segmentations
    """
    r = request
    image_id = request.headers["image_id"]
    manual_segmentation = db.session.query(ManualSegmentation).filter(ManualSegmentation.image_id == image_id).first()
    message = request.values["messageText"]
    message = Message(user=current_user, date=datetime.now(), message=message,
                      manual_segmentation=manual_segmentation, manual_segmentation_id=manual_segmentation.id)
    manual_segmentation.messages.append(message)
    db.session.commit()

    message = jsonify(message.as_dict())
    return message


@app.route("/data/delete_image", methods=["POST"])
@login_required
def delete_image():
    """
    Delete an image.

    @param image_id: database id of the image
    """

    data = json.loads(request.data)
    image_id = data["id"]
    image = db.session.query(Image).filter(Image.id == image_id).first()
    project = db.session.query(Project).filter(Project.id == image.project_id).first()
    image_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "images", image.name)
    segmentation_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "masks", image.name)
    db.session.query(Image).filter(Image.id == image.id).delete()
    if os.path.exists(image_path):
        os.remove(image_path)
    if os.path.exists(segmentation_path):
        os.remove(segmentation_path)

    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
