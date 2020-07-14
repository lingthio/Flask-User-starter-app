import io
import json
import os
import logging
from datetime import datetime
from dateutil.parser import parse as parse_date_string
import traceback
import zipfile
from gzip import GzipFile

import flask
import nibabel
from flask import Blueprint, request, redirect, jsonify, flash
from flask_user import login_required
from sqlalchemy import or_, asc, desc
from sqlalchemy import DateTime, Date
from nibabel import FileHolder, Nifti1Image
from nibabel.dataobj_images import DataobjImage
from nibabel.filebasedimages import SerializableImage

from app import app, db, current_project
from app.models.data_pool_models import Image, ManualSegmentation, Message, Modality, ContrastType
from app.utils import project_admin_required, project_reviewer_required, project_user_required

from app.controllers import data_pool_controller

# Define the blueprint: 'data_pool_service', set its url prefix: app.url/data_pool
data_pool_service = Blueprint('data_pool_service', __name__, url_prefix='/data_pool')

"""
Get all entries of the DataPool tables according to the project, role and user
"""
@data_pool_service.route('/project/<int:project_id>/datatable', methods = ['PUT', 'POST'])
@project_user_required
def images_datatable(project_id):

    app.logger.info("images_datatable")
    # See https://datatables.net/manual/server-side for all included parameters
    datatable_parameters = json.loads(request.data)

    offset = datatable_parameters["start"]
    limit = datatable_parameters["length"]

    # Build query
    query = db.session.query(Image)

    # only Images to requested project_id
    filter_query = query.filter(Image.project_id == project_id)
    # Database JOIN on Manual Segmentation
    filter_query = filter_query.join(ManualSegmentation, Image.id == ManualSegmentation.image_id)
    # Database Outter JOIN Modality and ContrastType
    filter_query = filter_query.join(Modality, isouter=True).join(ContrastType, isouter=True)

    r = request
    #if role == "segmentation":
    #    # Find assigned and open cases
    #    filter_query = filter_query.filter(
    #        or_(ManualSegmentation.assignee_id == current_user.id,
    #            ManualSegmentation.status.in_(["open_for_segmentation", "submitted", "rejected"])))
    #if role == "validation":
    #    # Find submitted cases
    #    filter_query = filter_query.filter(
    #        ManualSegmentation.status == "submitted")

    # Add sorting
    order_by_directives = datatable_parameters["order"]

    # only take the first column we should order by
    first_order_by = order_by_directives[0]
    first_order_by_column_id = first_order_by["column"]
    first_order_by_dir = first_order_by["dir"]

    columns = datatable_parameters["columns"]

    first_oder_by_column = columns[first_order_by_column_id]
    first_oder_by_column_name = first_oder_by_column["name"]

    app.logger.info(f"Order by {first_oder_by_column_name} {first_order_by_dir}")

    sorting_direction = asc if first_order_by_dir == "asc" else desc

    # Ordering only enabled for columns "status", "name", "image_valid"
    if first_oder_by_column_name == "status":
        filter_query = filter_query.order_by(sorting_direction(ManualSegmentation.status))
    elif first_oder_by_column_name == "name":
        filter_query = filter_query.order_by(sorting_direction(Image.name))
    elif first_oder_by_column_name == "image_valid":
        filter_query = filter_query.order_by(sorting_direction(Image.is_valid))

    # Searching
    searchable_columns = [Image.name, Image.patient_name, Modality.name, ContrastType.name, Image.accession_number]
    search_input = datatable_parameters["search"]["value"]
    if search_input != "":
        # Search in all searchable columns
        filters = [column.like(f"%{search_input}%") for column in searchable_columns]
        filter_query = filter_query.filter(or_(*filters))

    # Limit records
    records = filter_query.slice(offset, offset + limit).all()
    records_total = query.count()
    records_filtered = filter_query.count()

    # Also attach the project and its users of the project
    project_users = [user.as_dict() for user in current_project.users]

    contrast_types_dict = [{'label': cm.name, 'value': cm.id} for cm in current_project.contrast_types]
    contrast_types_dict.insert(0, {'label': 'NA', 'value': None})

    data = [record.as_dict() for record in records]
    for entry in data:
        # dummy fields for image / mask upload
        entry['upload_image'] = None
        entry['upload_mask'] = None
        entry['new_message'] = None

    response = {
        'draw': datatable_parameters["draw"],
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'project_users': project_users,
        'data': data,
        'options': {'contrast_type': contrast_types_dict}
    }

    return jsonify(response)


@data_pool_service.route('/project/<int:project_id>/case/update', methods=['POST'])
@login_required
def update_case_meta_data(project_id):
    """
    View for handling changes to datapool objects (assignments etc.)
    """

    data = request.form
    app.logger.info('---------------')
    app.logger.info(request.data)
    app.logger.info(request.form)
    app.logger.info('===============')
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    image_object = request.json
    segmentation_object = image_object["manual_segmentation"]

    # Find the image and segmentation object
    image = db.session.query(Image).filter(Image.id == case_id).first()
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


@data_pool_service.route('/project/<int:project_id>/case/<int:case_id>/send_message', methods=['GET'])
@login_required
def message(project_id, case_id):
    """
    Handle new messages appended to segmentations
    """
    r = request
    manual_segmentation = db.session.query(ManualSegmentation).filter(ManualSegmentation.image_id == case_id).first()
    message = request.values["messageText"]
    message = Message(user=current_user, date=datetime.now(), message=message,
                      manual_segmentation=manual_segmentation, manual_segmentation_id=manual_segmentation.id)
    manual_segmentation.messages.append(message)
    db.session.commit()

    message = jsonify(message.as_dict())
    return message


@data_pool_service.route('/project/<int:project_id>/case/upload', methods=['POST'])
@login_required
def upload_case(project_id):
    """
    Central endpoint to upload images
    """

    # Make sure file is actually included
    if 'image' not in request.files:
        flash('No file appended', category='error')
        return redirect(request.referrer)

    # Make sure it is a valid nifti
    image_file = request.files['image']
    try:
        fh = FileHolder(fileobj=GzipFile(fileobj=image_file))
        image_nifti = Nifti1Image.from_file_map({'header': fh, 'image': fh})
    except:
        traceback.print_exc()
        flash('File is not a valid nifti', category='error')
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    # Save image to correct path
    r = request
    image_path = os.path.join(app.config['DATA_PATH'], current_project.short_name, "images", image_file.filename)
    if os.path.exists(image_path):
        flash('File already exists', category="error")
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}
    nibabel.save(image_nifti, image_path)

    # Create entry for db (with empty segmentation)
    image = Image(project=current_project, name=image_file.filename)
    segmentation = ManualSegmentation(image=image, project=current_project)

    # Parse attributes
    attributes = json.loads(request.form['attributes'])
    for attribute, value in attributes.items():
        if hasattr(image, attribute) and value != "":
            setattr(image, attribute, value)

    db.session.add(image)
    db.session.add(segmentation)
    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@data_pool_service.route('/project/<int:project_id>/case/<int:case_id>/delete', methods=["POST"])
@login_required
def delete_case(project_id, case_id):
    """
    Delete an image.
    """

    data = json.loads(request.data)
    image = db.session.query(Image).filter(Image.id == case_id).first()
    image_path = os.path.join(app.config['DATA_PATH'], project.short_name, "images", image.name)
    segmentation_path = os.path.join(app.config['DATA_PATH'], current_project.short_name, "masks", image.name)
    db.session.query(Image).filter(Image.id == image.id).delete()
    if os.path.exists(image_path):
        os.remove(image_path)
    if os.path.exists(segmentation_path):
        os.remove(segmentation_path)

    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@data_pool_service.route('/project/<int:project_id>/case/<int:case_id>/upload_segmentation', methods=['POST'])
@login_required
def upload_case_segmentation(project_id, case_id):
    """
    Central endpoint to upload segmentations
    """

    # Make sure file is actually included
    if 'segmentation' not in request.files:
        flash('No file appended', category="error")
        return redirect(request.referrer)

        # Make sure it is a valid nifti
    segmentation_file = request.files["segmentation"]
    try:
        fh = FileHolder(fileobj=GzipFile(fileobj=segmentation_file))
        segmentation_nifti = Nifti1Image.from_file_map({'header': fh, 'image': fh})
    except:
        traceback.print_exc()
        flash('File is not a valid nifti', category="error")
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    # Make sure corresponding image exists
    image_name = request.headers["image_name"]
    image_path = os.path.join(app.config['DATA_PATH'], current_project.short_name, "images", image_name)

    if not os.path.exists(image_path):
        flash('No corresponding image found', category="error")
        return redirect(request.referrer)

    # Make sure that sizes match
    image_nifti = nibabel.load(image_path)
    if image_nifti.shape[:-1] != segmentation_nifti.shape[:-1]:
        flash('Image dimensions do not match segmentation dimensions', category="error")
        return redirect(request.referrer)

    # Update database
    image = db.session.query(Image).filter(Image.name == segmentation_file.filename).first()
    if image is None:
        flash('No corresponding image found', category="error")
        return redirect(request.referrer)
    segmentation = db.session.query(ManualSegmentation).filter(ManualSegmentation.image == image).first()
    if segmentation is None:
        segmentation = ManualSegmentation(project=current_project, image=image)
        db.session.add(segmentation)

    # Save file
    segmentation_path = os.path.join(app.config['DATA_PATH'], current_project.short_name, "masks",
                                     segmentation_file.filename)
    nibabel.save(segmentation_nifti, segmentation_path)

    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@data_pool_service.route('/project/<int:project_id>/case/<int:case_id>/download', methods=['GET'])
@login_required
def download_case(project_id, case_id):
    """
    Central endpoint to download image data and segmentations, if available
    """
    # Retrieve image and project data
    r = request
    image = db.session.query(Image).filter(Image.id == case_id).filter(Image.project_id == current_project.id).first()

    # Create zip file
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        z.write(image.__get_fn__(), 'image.nii.gz')
        if image.manual_segmentation != None:
            z.write(image.manual_segmentation.__get_fn__(), 'mask.nii.gz')
    data.seek(0)

    # Download file
    return flask.send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='data.zip'
    )
