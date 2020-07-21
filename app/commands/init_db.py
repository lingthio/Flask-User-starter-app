# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import os
import shutil
import logging

from flask_script import Command

from flask import current_app as c_app
from app import app, db
from app.models.data_pool_models import Image, ManualSegmentation, AutomaticSegmentation
from app.models.project_models import Project
from app.models.user_models import User, Role

from app.controllers import user_controller, project_controller, data_pool_controller

from tqdm import trange
import numpy as np
import nibabel as nib

logging.getLogger().setLevel(logging.INFO)

class InitDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_db()
        print('Database has been initialized.')


def init_db():
    """ Initialize the database."""
    db.drop_all()
    db.create_all()
    setup_example_data()


def setup_example_data(n_projects=2, n_images_per_project=50):
    """ Set up example projects with users, images and segmentations """

    # Adding roles
    admin_role = find_or_create_role('admin', u'Admin')
    user_role = find_or_create_role('user', u'User')

    # Add users
    admin = user_controller.find_or_create_user('Admin', 'Admin', 'admin@issm.org', 'admin', [admin_role, user_role])
    reviewer = user_controller.find_or_create_user('Reviewer', 'Reviewer', 'reviewer@issm.org', 'reviewer', [user_role])
    user = user_controller.find_or_create_user('User', 'User', 'user@issm.org', 'user', [user_role])

    # Create project sample data
    projects = []
    for project_index in range(n_projects):

        short_name = "proj_" + str(project_index)
        long_name = "Project_" + str(project_index)

        project = project_controller.create_project(short_name=short_name, long_name=long_name, admins = [admin], reviewers = [reviewer], users = [user])

        projects.append(project)

        automatic_segmentation_model = data_pool_controller.create_automatic_segmentation_model(project_id = project.id)

        for i in trange(n_images_per_project, desc='generating sample data'):

            image = data_pool_controller.create_image(project = project, name = f'Image_{project_index}_{i}')
            man_seg = data_pool_controller.create_manual_segmentation(project = project, image_id = image.id)
            auto_seg = data_pool_controller.create_automatic_segmentation(project = project, image_id = image.id, model_id = automatic_segmentation_model.id)

            # image = Image(project=project, name=f'Image_{project_index}_{i}')
            # man_seg = ManualSegmentation(project=project, image=image)
            # auto_seg = AutomaticSegmentation(project=project, image=image)

            # db.session.add_all([image, man_seg, auto_seg])
            # db.session.flush()

            auto_seg.nii = nib.Nifti1Image(np.zeros((100,100,100)), np.eye(4))
            man_seg.nii = nib.Nifti1Image(np.zeros((100,100,100)), np.eye(4))
            image.nii = nib.Nifti1Image(np.zeros((100,100,100)), np.eye(4))

            db.session.commit()


"""
Find existing role or create new role
"""
def find_or_create_role(name, label):
    role = Role.query.filter(Role.name == name).first()

    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
        db.session.commit()

    return role

