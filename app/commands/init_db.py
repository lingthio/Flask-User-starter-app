# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import os
import shutil

from flask_script import Command

from flask import current_app as c_app
from app import db
from app.models.data_pool_models import Image, ManualSegmentation, AutomaticSegmentation
from app.models.project_models import Project
from app.models.user_models import User, Role

from tqdm import trange
import numpy as np
import nibabel as nib


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
    admin = find_or_create_user('Admin', 'Admin', 'admin@issm.org', 'admin', [admin_role, user_role])
    reviewer = find_or_create_user('Reviewer', 'Reviewer', 'reviewer@issm.org', 'reviewer', [user_role])
    user = find_or_create_user('User', 'User', 'user@issm.org', 'user', [user_role])

    # Create project sample data
    projects = []
    for project_index in range(n_projects):
        project = Project(short_name="proj_" + str(project_index),
                          long_name="Project_" + str(project_index), active=True)
        project.admins.append(admin)
        project.reviewers.append(reviewer)
        project.users.append(user)
        projects.append(project)
        db.session.add(project)


        for i in trange(n_images_per_project, desc='generating sample data'):
            image = Image(project=project, name=f'Image_{project_index}_{i}')
            man_seg = ManualSegmentation(project=project, image=image)
            auto_seg = AutomaticSegmentation(project=project, image=image)

            db.session.add_all([image, man_seg, auto_seg])
            db.session.flush()

            auto_seg.nii = nib.Nifti1Image(np.zeros((100,100,100)), np.eye(4))
            man_seg.nii = nib.Nifti1Image(np.zeros((100,100,100)), np.eye(4))
            image.nii = nib.Nifti1Image(np.zeros((100,100,100)), np.eye(4))

            db.session.commit()


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role


def find_or_create_user(first_name, last_name, email, password, roles=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    active=True)
        if roles:
            user.roles.extend(roles)
        db.session.add(user)
    return user
