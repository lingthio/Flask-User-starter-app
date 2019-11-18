# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import datetime

from flask import current_app
from flask_script import Command

from app import db
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
    projects = db.session.query(Project).all()
    images = db.session.query(Image).all()
    segmenations = db.session.query(AutomaticSegmentation).all()
    print("")


def setup_example_data():
    """ Set up example projects with users, images and segmentations """

    # Adding roles
    admin_role = find_or_create_role('admin', u'Admin')
    segmenter_role = find_or_create_role('segmenter', u'Segmenter')

    # Add users
    admin = find_or_create_user(u'Admin', u'Example', u'admin@example.com', 'Password1', admin_role)
    segmenter = find_or_create_user(u'Member', u'Example', u'member@example.com', 'Password1',
                                    segmenter_role)

    # Create projects
    for project_index in range(3):
        project = Project(short_name="proj_" + str(project_index),
                          name="Project_" + str(project_index), active=True)
        db.session.add(project)

        # Add Images and segmentations
        images = [Image(project=project, name="Image_" + str(i)) for i in range(10)]
        man_segmentations = [ManualSegmentation(project=project, image=image) for image in images]
        auto_segmentations = [AutomaticSegmentation(project=project, image=image) for image in images]
        db.session.add_all(images + man_segmentations + auto_segmentations)

    db.session.commit()


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role


def find_or_create_user(first_name, last_name, email, password, role=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    active=True)
        if role:
            user.roles.append(role)
        db.session.add(user)
    return user

