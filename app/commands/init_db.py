# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import datetime
import os

from flask import current_app
from flask_script import Command

from app import db, settings
from app.models.data_pool_models import Image, DataPool, ManualSegmentation, StatusEnum, AutomaticSegmentation
from app.models.project_models import Project
from app.models.user_models import User, Role


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


def setup_example_data(n_projects=10, n_images_per_project=80):
    """ Set up example projects with users, images and segmentations """

    # Adding roles
    admin_role = find_or_create_role('admin', u'Admin')
    user_role = find_or_create_role('user', u'User')

    # Add users
    admin = find_or_create_user('Hinrich', 'Winther', 'hinrich@hinrich.com', 'hinrich', [admin_role, user_role])
    reviewer = find_or_create_user('Nils', 'Nommensen', 'nils@nils.com', 'nils', [user_role])
    user = find_or_create_user('Tobias', 'Blaaaa', 'tobias@tobias.com', 'tobias', [user_role])

    # Create projects
    projects = []
    for project_index in range(n_projects):
        project = Project(short_name="proj_" + str(project_index),
                          long_name="Project_" + str(project_index), active=True)
        project.admins.append(admin)
        project.reviewers.append(reviewer)
        project.users.append(user)
        projects.append(project)
        db.session.add(project)

        # Add Images and segmentations
        images = [Image(project=project, name="Image_" + str(i) + ".nii.gz") for i in range(n_images_per_project)]
        man_segmentations = [ManualSegmentation(project=project, image=image) for image in images]
        auto_segmentations = [AutomaticSegmentation(project=project, image=image) for image in images]
        db.session.add_all(images + man_segmentations + auto_segmentations)

        # Create fake data
        for image in images:
            # Create directories
            image_directory_path = os.path.join(settings.DATA_PATH, project.short_name, "images")
            segmentation_directory_path = os.path.join(settings.DATA_PATH, project.short_name, "masks")
            if not os.path.exists(image_directory_path):
                os.makedirs(image_directory_path, exist_ok=True)
            if not os.path.exists(segmentation_directory_path):
                os.makedirs(segmentation_directory_path, exist_ok=True)

            # Create fake images and segmentations
            for directory_path in [image_directory_path, segmentation_directory_path]:
                file_path = os.path.join(directory_path, image.name)
                open(file_path, 'a').close()

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

