"""
This module handles upload and download of case data (actual image data and segmentations) and offers the
following endpoints:
    /data/upload_image_data
    /data/upload_segmentation_data
    /data/download_case_data
"""

import io
import json
import os
import traceback
import zipfile
from gzip import GzipFile

import flask
import nibabel
from flask import request, redirect, flash
from flask_user import login_required
from nibabel import FileHolder, Nifti1Image
from nibabel.dataobj_images import DataobjImage
from nibabel.filebasedimages import SerializableImage

from app import app
from app import db, local_settings
from app.models.data_pool_models import Image, ManualSegmentation
from app.models.project_models import Project


@app.route("/data/upload_image_data", methods=['POST'])
@login_required
def upload_image_data():
    """
    Central endpoint to upload images

    Request Parameters:
        project_id: project id that this data belongs to
    """
    # Fetch the project this request belongs to

    project_id = int(request.headers["project_id"])
    project = db.session.query(Project).filter(Project.id == project_id).first()

    # Make sure file is actually included
    if "image" not in request.files:
        flash('No file appended', category="error")
        return redirect(request.referrer)

    # Make sure it is a valid nifti
    image_file = request.files["image"]
    try:
        fh = FileHolder(fileobj=GzipFile(fileobj=image_file))
        image_nifti = Nifti1Image.from_file_map({'header': fh, 'image': fh})
    except:
        traceback.print_exc()
        flash('File is not a valid nifti', category="error")
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}

    # Save image to correct path
    image_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "images", image_file.filename)
    if os.path.exists(image_path):
        flash('File already exists', category="error")
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}
    nibabel.save(image_nifti, image_path)

    # Add entry to db (with empty segmentation)
    image = Image(project=project, name=image_file.filename)
    segmentation = ManualSegmentation(image=image, project=project)
    db.session.add(image)
    db.session.add(segmentation)
    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/data/upload_segmentation_data", methods=['POST'])
@login_required
def upload_segmentation_data():
    """
    Central endpoint to upload segmentations

    Request Parameters:
        project_id: project id that this data belongs to
        image_name: name of the corresponding image
    """
    # Fetch the project this request belongs to
    project_id = int(request.headers["project_id"])
    project = db.session.query(Project).filter(Project.id == project_id).first()

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
    image_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "images", image_name)

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
        segmentation = ManualSegmentation(project=project, image=image)
        db.session.add(segmentation)

    # Save file
    segmentation_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "masks",
                                     segmentation_file.filename)
    nibabel.save(segmentation_nifti, segmentation_path)

    db.session.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/data/download_case_data", methods=['GET'])
@login_required
def download_case_data():
    """
    Central endpoint to download image data and segmentations, if available

    Request Parameters:
        project_id: project id that this data belongs to
        image_name: name of the image
    """
    # Retrieve image and project data
    r = request
    image_name = request.headers["image_name"]
    project_id = request.headers["project_id"]
    image = db.session.query(Image).filter(Image.name == image_name).filter(Image.project_id == project_id).first()
    project = image.project

    # Find corresponding files
    image_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "images", image.name)
    segmentation_path = os.path.join(local_settings.DATA_DIRECTORY, project.short_name, "masks", image.name)

    if not os.path.exists(image_path):
        flash("Image does not exist", category="error")

    # Create zip file
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        z.write(image_path, image.name)
        if os.path.exists(segmentation_path):
            z.write(segmentation_path, "mask.nii.gz")
    data.seek(0)

    # Download file
    return flask.send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='data.zip'
    )
