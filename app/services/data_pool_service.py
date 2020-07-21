import io
import json
import os
import re
import logging
import traceback

from datetime import datetime
from dateutil.parser import parse as parse_date_string
import zipfile
from gzip import GzipFile

import flask
import nibabel
from flask import Blueprint, request, redirect, jsonify, flash
from flask_user import login_required
from flask_login import current_user
from sqlalchemy import or_, asc, desc
from sqlalchemy import DateTime, Date
from nibabel import FileHolder, Nifti1Image
from nibabel.dataobj_images import DataobjImage
from nibabel.filebasedimages import SerializableImage

from app import app, db, current_project
from app.models.config import DATE_FORMAT, DATETIME_FORMAT
from app.models.data_pool_models import StatusEnum, SplitEnum, Image, ManualSegmentation, AutomaticSegmentation, Message, Modality, ContrastType

from app.utils import is_project_reviewer, is_project_user, technical_admin_required, project_admin_required, project_reviewer_required, project_user_required

from app.controllers import data_pool_controller, project_controller, user_controller

# Define the blueprint: 'data_pool_service', set its url prefix: app.url/data_pool
data_pool_service = Blueprint('data_pool_service', __name__, url_prefix='/data_pool')

"""
Get all Status values for Images
"""
@data_pool_service.route("/statusEnum/all")
@login_required
def get_all_image_status_values():

    data = {
        "status_enum": [statusEnum.as_dict() for statusEnum in StatusEnum]
    }

    return jsonify(data)

"""
Get all Split values for Images
"""
@data_pool_service.route("/splitEnum/all")
@login_required
def get_all_image_split_values():

    data = {
        "split_enum": [splitEnum.as_dict() for splitEnum in SplitEnum]
    }

    return jsonify(data)

"""
Get all Modalities of a project
"""
@data_pool_service.route("/project/<int:project_id>/modalities")
@login_required
def get_modalities_of_project(project_id):

    modalities = data_pool_controller.get_all_modalities_for_project(project_id = project_id)

    data = {
        "modalities": [modality.as_dict() for modality in modalities]
    }

    return jsonify(data)

"""
Get all ContrastTypes of a project
"""
@data_pool_service.route("/project/<int:project_id>/contrast_types")
@login_required
def get_contrast_types_of_project(project_id):

    contrast_types = data_pool_controller.get_all_contrast_types_for_project(project_id = project_id)

    data = {
        "contrast_types": [contrast_type.as_dict() for contrast_type in contrast_types]
    }

    return jsonify(data)

"""
Get all entries of the DataPool tables according to the project, role and user
"""
@data_pool_service.route('/project/<int:project_id>/datatable', methods = ['POST'])
@project_user_required
def images_datatable(project_id):

    project = project_controller.find_project(id = project_id)

    if project is None:
        return {
            'success': False,
            'error': "No valid project id provided", 
            'message': "The project id provided in the url /project/PROJECT_ID/case/image is not a valid project id"
        }, 400

    app.logger.info("images_datatable")
    # See https://datatables.net/manual/server-side for all included parameters
    datatable_parameters = json.loads(request.data)

    offset = datatable_parameters["start"]
    limit = datatable_parameters["length"]

    app.logger.info(f"Requested {offset} - {offset + limit}")

    # Build query
    query = db.session.query(Image)

    # only Images to requested project_id
    filter_query = query.filter(Image.project_id == project_id)
    # Database JOIN on Manual Segmentation
    filter_query = filter_query.join(ManualSegmentation, Image.id == ManualSegmentation.image_id, isouter=True)
    # Database Outter JOIN Modality and ContrastType
    filter_query = filter_query.join(Modality, isouter=True).join(ContrastType, isouter=True)

    # if the current user is only a user of the project, filter not-queued images and those, which are not assigned to him
    app.logger.info(f"User is at least reviewer in project: {is_project_reviewer(project)}")
    if not is_project_reviewer(project):
        filter_query = filter_query.filter((ManualSegmentation.status == StatusEnum.queued) | (ManualSegmentation.assignee_id == current_user.id))

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

    if (len(records) > 0):
        app.logger.info(records[0].as_dict())

    # Also attach the project and its users of the project
    project_users = [user.as_dict() for user in current_project.users]

    # uncomment if options should be provided serverside for select fields
    # this has the issue in the edit dialog, that the current value is not preselected
    # see datatable_util.js and cases.html files for the frontend solution to this 
    # (loading select options from server and select the correct value on 'initEdit' call of Editor)

    #contrast_types_dict = [{'label': cm.name, 'value': cm.id} for cm in current_project.contrast_types]
    #modalities_dict = [{'label': m.name, 'value': m.id} for m in current_project.modalities]

    #status_dict = [{'label': s.value, 'value': s.name} for s in StatusEnum]
    #split_dict = [{'label': s.value, 'value': s.name} for s in SplitEnum]

    # TODO add values for these fields
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
        # where is this options defined/documented?
        'options': {
            # 'contrast_type': contrast_types_dict,
            # 'modality': modalities_dict,
            # 'status': status_dict,
            # 'split': split_dict
        }
    }

    return jsonify(response)

"""
Endpoint to upload a new case or update an existing one (a nifti image)
"""
@data_pool_service.route('/project/<int:project_id>/case/image', methods=['POST'])
@login_required
@project_admin_required
def upload_case(project_id):

    project = project_controller.find_project(id = project_id)

    if project is None:
        return {
            'success': False,
            'error': "No valid project id provided", 
            'message': "The project id provided in the url /project/PROJECT_ID/case/image is not a valid project id"
        }, 400

    # app.logger.info(f"For field {request.__dict__}")

    update_case = False

    # Check if this upload is an update of an existing case
    if 'id' in request.form and request.form['id']:
        update_case = True
        image_id = request.form['id']

    app.logger.info(f"Uploaded files: {request.files}")

    # Make sure file is actually included
    if 'upload' not in request.files:
        flash('No file appended', category='error')
        return {
            'success': False,
            'error': "No image appended", 
            'message': "The HTTP POST Request needs to include a file named image in the appended files"
        }, 400

    # Make sure it is a valid nifti
    image_file = request.files['upload']
    try:
        fh = FileHolder(fileobj=GzipFile(fileobj=image_file, mode='rb'))
        image_nifti = Nifti1Image.from_file_map({'header': fh, 'image': fh})
    except:
        traceback.print_exc()
        flash('File is not a valid nifti', category='error')
        return {
            'success': False,
            'error': "No valid nifti file provided", 
            'message': "The uploaded file is not a valid nifti file"
        }, 400
    
    if update_case:
        image = data_pool_controller.find_image(id = image_id)
    else:
        # Create entry for db (with empty segmentation)
        image = data_pool_controller.create_image(project = project, name = image_file.filename)

    app.logger.info(f"Image: {image}")

    image_path = project.get_image_path(image_type = 'raw', image_id = image.id)

    app.logger.info(f"Image path: {image_path}")

    if os.path.exists(image_path):
        # Override file
        os.remove(image_path)

    nibabel.save(image_nifti, image_path)

    if not update_case:
        manual_segmentation = data_pool_controller.create_manual_segmentation(project = project, image_id = image.id)

    if image is not None:
        return {
            'success': True, 
            'upload': {'id': image.id},
            'files': {
                Image.__tablename__: {
                    f"{image.id}": image.as_dict()
                }
            }
        }, 200
    else:
        return {'success': False, 'error': "DB Image entry creation failed"}, 400

"""
Handling creation of metadata for cases/images (assignments etc.)
"""
@data_pool_service.route('/project/<int:project_id>/case', methods=['POST'])
@login_required
@project_admin_required
def create_case_meta_data(project_id):

    project = project_controller.find_project(id = project_id)

    if project is None:
        return {
            'success': False,
            'error': "No valid project id provided", 
            'message': "The project id provided in the url /project/PROJECT_ID/... is not a valid project id"
        }, 400

    app.logger.info(f"Project {project.short_name}: Creating case meta data")

    case_meta_data = get_case_data_from_request(request)

    if case_meta_data is None:
        app.logger.info(f"Data in json? {request.json}")
        return {'success': False}, 400

    image = None

    # Find or create the image and segmentation object
    if 'upload_image' in case_meta_data and case_meta_data['upload_image']:
        image = data_pool_controller.find_image(id = case_meta_data['upload_image'])
    else:
        image = data_pool_controller.create_image(project = project)
        manual_segmentation = data_pool_controller.create_manual_segmentation(project = project, image_id = image.id)

    ### Updatew image object ###
    data_pool_controller.update_image_from_map(image, case_meta_data)

    return {
        'success': True,
        'data': image.as_dict()
    }, 200

"""
Handling changes of meta data for cases/images (assignments etc.)
"""
@data_pool_service.route('/project/<int:project_id>/case', methods=['PUT'])
@login_required
@project_user_required
def update_case_meta_data(project_id):

    project = project_controller.find_project(id = project_id)

    if project is None:
        return {
            'success': False,
            'error': "No valid project id provided", 
            'message': "The project id provided in the url /project/PROJECT_ID/... is not a valid project id"
        }, 400

    case_ids = request.args.get('ids')

    if case_ids is None:
        return {
            'success': False,
            'error': "No valid case id(s) provided", 
            'message': "The case id provided in the url .../case?ids=CASE_ID1,CASE_ID2... is/are not valid case id(s)"
        }, 400

    # update all specified cases
    for case_id in case_ids.split(','):

        app.logger.info(f"Project {project.short_name}: Updating case {case_id}")

        update_case_meta_data = get_case_data_from_request(request)

        # Find the image and segmentation object
        image = data_pool_controller.find_image(id = case_id)

        ### Updatew image object ###
        data_pool_controller.update_image_from_map(image, update_case_meta_data)

        manual_segmentation = data_pool_controller.find_manual_segmentation(id = image.manual_segmentation.id)

        ### Update manual segmentation ###
        data_pool_controller.update_manual_segmentation_from_map(manual_segmentation, update_case_meta_data)

        # Append messages
        if "new_message" in update_case_meta_data:
            message = update_case_meta_data["new_message"]

            message = data_pool_controller.create_message(user = current_user, message = message, manual_segmentation = manual_segmentation)
            manual_segmentation.messages.append(message)

        ### Commit image object ###
        data_pool_controller.update_manual_segmentation(manual_segmentation)

    return {
        'success': True,
        'data': image.as_dict()
    }, 200

"""
Delete a case or multiple cases (delete image and segmentation data in project directory and from database)
"""
@data_pool_service.route('/project/<int:project_id>/case', methods=["DELETE"])
@login_required
@project_admin_required
def delete_case(project_id):

    project = project_controller.find_project(id = project_id)

    if project is None:
        return {
            'success': False,
            'error': "No valid project id provided", 
            'message': "The project id provided in the url /project/PROJECT_ID/... is not a valid project id"
        }, 400
    
    case_ids = request.args.get('ids')

    if case_ids is None:
        return {
            'success': False,
            'error': "No valid case id(s) provided", 
            'message': "The case id provided in the url .../case?ids=CASE_ID1,CASE_ID2... is/are not valid case id(s)"
        }, 400

    # for all specified images
    for case_id in case_ids.split(','):
        app.logger.info(f"Project {project.short_name}: Deleting case {case_id}")

        image = data_pool_controller.find_image(id = case_id)

        if image is None:
            return {
                'success': False,
                'error': "No valid case id provided", 
                'message': "The case id provided in the url .../case/CASE_ID... is not a valid case id"
            }, 400

        # delete all actual nifti images
        raw_image_path = project.get_image_path(image_type = 'raw', image_id = image.id)
        if os.path.exists(raw_image_path):
            os.remove(raw_image_path)

        manual_segmentation_image_path = project.get_image_path(image_type = 'manual_segmentation', image_id = image.id)
        if os.path.exists(manual_segmentation_image_path):
            os.remove(manual_segmentation_image_path)

        for segmentation_model in project.automatic_segmentation_models:
            automatic_segmentation_image_path = project.get_image_path(image_type = 'automatic_segmentation', 
                                                                        model_id = segmentation_model.id, 
                                                                        image_id = image.id)
            if os.path.exists(automatic_segmentation_image_path):
                os.remove(automatic_segmentation_image_path)
        
        # delete database object
        data_pool_controller.delete_image(image)

    return {'success': True}, 200

"""
Endpoint to upload a segmentation for a case (a nifti image)
"""
@data_pool_service.route('/project/<int:project_id>/case/segmentation', methods=['POST'])
@login_required
@project_user_required
def upload_segmentation(project_id):

    project = project_controller.find_project(id = project_id)

    if project is None:
        return {
            'success': False,
            'error': "No valid project id provided", 
            'message': "The project id provided in the url /project/PROJECT_ID/case/image is not a valid project id"
        }, 400

    image = None

    # Check if id is provided in form data, otherwise deny request
    if 'id' in request.form:
        case_id = request.form['id']
        image = data_pool_controller.find_image(id = case_id)

    if image is None:
        return {
            'success': False,
            'error': "No valid case id provided", 
            'message': "The case id provided in the url .../case/CASE_ID... is not a valid case id"
        }, 400

    app.logger.info(f"Uploaded files: {request.files}")

    # Make sure file is actually included
    if 'upload' not in request.files:
        flash('No file appended', category='error')
        return {
            'success': False,
            'error': "No image appended", 
            'message': "The HTTP POST Request needs to include a file named image in the appended files"
        }, 400

    # Make sure it is a valid nifti
    segmentation_image_file = request.files['upload']
    try:
        fh = FileHolder(fileobj=GzipFile(fileobj=segmentation_image_file, mode='rb'))
        segmentation_nifti = Nifti1Image.from_file_map({'header': fh, 'image': fh})
    except:
        traceback.print_exc()
        flash('File is not a valid nifti', category='error')
        return {
            'success': False,
            'error': "No valid nifti file provided", 
            'message': "The uploaded file is not a valid nifti file"
        }, 400

    # Make sure that sizes match
    image_path = project.get_image_path(image_type = 'raw', image_id = image.id)

    image_nifti = nibabel.load(image_path)
    if image_nifti.shape[:-1] != segmentation_nifti.shape[:-1]:
        flash('Image dimensions do not match segmentation dimensions', category="error")
        return {
            'success': False,
            'error': "Dimension mismatch", 
            'message': "The uploaded nifti image dimension does not match the dimension of the case image"
        }, 400

    # Check which kind of segmentation has been uploaded, automatic or manual
    segmentation_type = request.args.get('type')

    if (segmentation_type == 'manual'):

        manual_segmentation = data_pool_controller.find_manual_segmentation(project_id = project.id, image_id = image.id)

        if manual_segmentation is None:
            manual_segmentation = data_pool_controller.create_manual_segmentation(project = project, image_id = image.id)

        image_path = project.get_image_path(image_type = 'manual_segmentation', image_id = manual_segmentation.id)

        if os.path.exists(image_path):
            app.logger.info(f"Old image already exists at {image_path}. Deleting and replacing by new one.")
            os.remove(image_path)

        nibabel.save(segmentation_nifti, image_path)

        data_pool_controller.update_manual_segmentation(manual_segmentation)

        # to display the filename in the frontend
        manual_segmentation_dict = manual_segmentation.as_dict()
        manual_segmentation_dict['name'] = image_path.split('/')[-1]

        return {
            'success': True, 
            'upload': {'id': manual_segmentation.id},
            'files': {
                ManualSegmentation.__tablename__: {
                    f"{manual_segmentation.id}": manual_segmentation_dict
                }
            }
        }, 200

        # SEGMENTATION UPLOAD
        # segmentation = ManualSegmentation(image=image, project=current_project)

    elif (segmentation_type == 'automatic'):
        # if automatic segmentation is uploaded, the model id needs to be given from which the segmentation was created
        model_id = request.args.get('model_id')

        model = None

        if model_id is not None:
            model = data_pool_controller.find_model(id = model_id)

        if model_id is None or model is None:
            return {
                'success': False,
                'error': "Automatic segmentation upload: No valid model id provided", 
                'message': "Via the URL provide the parameter model_id=XY where XY is a valid model id"
            }, 400

        # TODO store image as automatic segmentation

        automatic_segmentation = data_pool_controller.find_automatic_segmentation(image_id = image.id, project_id = project.id)

        if automatic_segmentation is None:
            automatic_segmentation = data_pool_controller.create_automatic_segmentation(project = project, image_id = image.id, model_id = model.id)

        image_path = project.get_image_path(image_type = 'automatic_segmentation', model_id = model.id, image_id = automatic_segmentation.id)

        if os.path.exists(image_path):
            app.logger.info(f"Old image already exists at {image_path}. Deleting and replacing by new one.")
            os.remove(image_path)

        nibabel.save(segmentation_nifti, image_path)

        # to display the filename in the frontend
        automatic_segmentation_dict = automatic_segmentation.as_dict()
        automatic_segmentation_dict['name'] = image_path.split('/')[-1]

        return {
            'success': True, 
            'upload': {'id': automatic_segmentation.id},
            'files': {
                AutomaticSegmentation.__tablename__: {
                    f"{automatic_segmentation.id}": automatic_segmentation_dict
                }
            }
        }, 200

    else:
        app.logger.error(f"Segmentation upload: {segmentation_type} is no supported segmentation type")
        return {
                'success': False,
                'error': "No valid segmentation type provided", 
                'message': "Valid segmentation types are 'manual', 'automatic'"
            }, 400



@data_pool_service.route('/project/<int:project_id>/case/<int:case_id>/upload_segmentation', methods=['POST'])
@login_required
def upload_case_segmentation(project_id, case_id):
    """
    Central endpoint to upload segmentations
    """

    # Make sure file is actually included
    if 'upload' not in request.files:
        flash('No file appended', category="error")
        return redirect(request.referrer)

        # Make sure it is a valid nifti
    segmentation_file = request.files["upload"]
    try:
        fh = FileHolder(fileobj=GzipFile(fileobj=segmentation_file, mode='rb'))
        segmentation_nifti = Nifti1Image.from_file_map({'header': fh, 'image': fh})
    except:
        traceback.print_exc()
        flash('File is not a valid nifti', category="error")
        return {'success': False}, 400

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
    return {'success': True}, 200

"""
Endpoint to update status, messages and mask of manual segmentation

Needs the post data:
user_id = INT
message = '' (optional)
"""
@data_pool_service.route('/project/<int:project_id>/case/<int:case_id>/review', methods=['PUT','POST'])
@login_required
@project_user_required
def assign_or_submit_or_review(project_id, case_id):

    project = project_controller.find_project(id = project_id)

    if project is None:
        return {
            'success': False,
            'error': "No valid project id provided", 
            'message': "The project id provided in the url /project/PROJECT_ID/... is not a valid project id"
        }, 400

    image = data_pool_controller.find_image(id = case_id)
    manual_segmentation = image.manual_segmentation

    if image is None:
        return {
            'success': False,
            'error': "No valid case id provided", 
            'message': "The case id provided in the url .../case/ID... is not valid case id"
        }, 400

    user = current_user

    other_user_id = None
    message = None
    new_status = None

    # POST Parameter in json
    if request.json is not None:
        other_user_id = request.json['user_id']
        message = request.json['message']
    else:
        data = get_data_from_datatables_form(request)

        if 'status' in data:
            new_status = data['status']
            
        if 'new_message' in data:
            new_message = data['new_message']

            if new_message != '':
                message = new_message

    if other_user_id is not None:
        # check if user has the permission to do so
        if not is_project_reviewer(current_project):
            return {
                'success': False,
                'error': "Not permitted", 
                'message': "You are not permitted to assign the case to another user"
            }, 400
        
        user = user_controller.find_user(id = other_user_id)

        if user is None:
            return {
                'success': False,
                'error': "No valid user id provided",
            }, 400
    else:
        # check if user has the permission to do so
        if not is_project_user(current_project):
            return {
                'success': False,
                'error': "Not permitted", 
                'message': "You are not permitted to assign the case to another user"
            }, 400

    if manual_segmentation.status == StatusEnum.queued:
        # Case is meant to be assigned

        # assign case to user
        data_pool_controller.assign_manual_segmentation(manual_segmentation = manual_segmentation, assignee = user, message = message)

    elif manual_segmentation.status == StatusEnum.assigned:
        # Case is meant to be submitted or unclaimed

        if new_status == StatusEnum.submitted.name:

            # TODO handle submitted data
            app.logger.error(f"Submitting segmentations not implemented!")

            return {
                'success': False,
                'data': manual_segmentation.as_dict()
            }, 400

        elif new_status == StatusEnum.queued.name:

            if message is not None:
                message = data_pool_controller.create_message(user = user, message = message, manual_segmentation = image.manual_segmentation)

            data_pool_controller.unclaim_manual_segmentation(manual_segmentation = image.manual_segmentation, message = message)

        else:
            return {
                'success': False,
                'error': "No valid action provided", 
                'message': "The manual segmentation is currently assigned, you can specify the actions 'submit' and 'unclaim' with /review?action='...'"
            }, 400

    elif manual_segmentation.status == StatusEnum.submitted:
        # Case is meant to be rejected or accepted

        # TODO handle rejection or accepting
        app.logger.error(f"Rejecting and accepting segmentations not implemented!")

        return {
            'success': False,
            'data': manual_segmentation.as_dict()
        }, 400


    return {
        'success': True,
        'data': manual_segmentation.as_dict()
        }, 200

@data_pool_service.route('/project/<int:project_id>/case/<int:case_id>/send_message', methods=['GET'])
@login_required
@project_user_required
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


"""
Central endpoint to download image data and segmentations, if available
"""
@data_pool_service.route('/project/<int:project_id>/case/<int:case_id>/download', methods=['GET'])
@login_required
@project_user_required
def download_case(project_id, case_id):
    # Retrieve image and project data
    
    project = project_controller.find_project(id = project_id)

    if project is None:
        return {
            'success': False,
            'error': "No valid project id provided", 
            'message': "The project id provided in the url /project/PROJECT_ID/... is not a valid project id"
        }, 400

    image = data_pool_controller.find_image(id = case_id)
    manual_segmentation = image.manual_segmentation

    if image is None:
        return {
            'success': False,
            'error': "No valid case id provided", 
            'message': "The case id provided in the url .../case/ID... is not valid case id"
        }, 400

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
        attachment_filename=f'{project.short_name}_case_{image.id}.zip'
    )

"""
This should rather be done with accessor functions like here:
https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request

request.form.get('id')
request.form.get('manual_segmentation') etc. etc.
"""
def get_case_data_from_request(request):

    # check, if the request is fired by a form or by ajax call
    is_form_request = hasattr(request, 'form')

    app.logger.info(f"From form: {is_form_request}")

    case_meta_data = None

    if (is_form_request):

        app.logger.info(f"Formdata: {request.form}")

        case_meta_data = {}

        # Parsing of the HTML form data into case_meta_data
        field_name_start_with_regex = r'data\[\d+\]'

        for field in request.form:
            matcher = re.search(field_name_start_with_regex, field)
            if matcher:
                start_index = len(matcher.group(0)) + 1
                field_name = field[start_index : -1]
                case_meta_data[field_name] = request.form[field]
        
    else:
        app.logger.info(f"JSON Content: {request.json}")

        # TODO

        case_meta_data = request.json

    app.logger.info(f"Meta Data: {case_meta_data}")

    return case_meta_data

"""
This function may receive a request from a datatables call and is able to retrieve all data and 
pack it into a dictionary 'data'
The request should have the layout:
([data[1232131][id], 2], [data[1232131][manual_segmentation][id], 3], ...)
And the resulting dict is:
{
    id: 2,
    manual_segmentation: {
        id: 3
    }, 
    
    etc.
}
"""
def get_data_from_datatables_form(request):
    # Parsing of the HTML form data into case_meta_data
    field_name_start_with_regex = r'data\[\d+\]'

    data = {}

    for field in request.form:
        # app.logger.info(f"{field}")

        matcher = re.search(field_name_start_with_regex, field)
        if matcher:
            start_index = len(matcher.group(0)) + 1
            field_name = field[start_index : -1]
            keys = field_name.split('][')

            nested = data
            for key in keys[:-1]:
                if key not in nested:
                    app.logger.info(f"{key} is a new Object?")
                    nested[key] = {}
                nested = nested[key]

            nested[keys[-1]] = request.form[field]

    # uncomment to print data formatted
    # app.logger.info(json.dumps(data, indent=4))

    return data