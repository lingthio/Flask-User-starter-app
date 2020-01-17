import json
from datetime import datetime

from dateutil.parser import parse as parse_date_string
from flask import request
from flask_login import current_user
from flask_user import login_required
from sqlalchemy import DateTime, Date

from app import app
from app import db
from app.models.data_pool_models import Image, ManualSegmentation, Message


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
        value = image_object[column_name]
        if value is None:
            continue
        if value is not None and type(column.type) == DateTime or type(column.type) == Date:
            value = datetime.strptime(image_object[column_name], '%a, %d %b %Y %H:%M:%S %Z')
        setattr(image, column_name, value)

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
