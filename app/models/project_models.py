import os
from datetime import datetime

from sqlalchemy import event
from flask import current_app as app

from app import db
from . import user_models
from . import data_pool_models


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.Unicode(16), nullable=False, server_default=u'', unique=True)
    long_name       = db.Column(db.Unicode(255), nullable=False, server_default=u'')
    description = db.Column(db.Unicode(255), nullable=False, server_default=u'')
    active     = db.Column(db.Boolean(), nullable=False, server_default='1')
    insert_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Relationships
    admins    = db.relationship('user_models.User', secondary='projects_admins',
                               backref=db.backref('admin_for_project', lazy='dynamic'))
    reviewers = db.relationship('user_models.User', secondary='projects_reviewers',
                               backref=db.backref('reviewer_for_project', lazy='dynamic'))
    users     = db.relationship('user_models.User', secondary='projects_users',
                               backref=db.backref('user_for_project', lazy='dynamic'))

    data_pool_objects = db.relationship('data_pool_models.DataPool', back_populates='project', cascade="all, delete-orphan")
    modalities = db.relationship('data_pool_models.Modality', back_populates='project', cascade="all, delete-orphan")
    contrast_types = db.relationship('data_pool_models.ContrastType', back_populates='project', cascade="all, delete-orphan")
    automatic_segmentation_models = db.relationship('data_pool_models.AutomaticSegmentationModel', back_populates='project', cascade="all, delete-orphan")

    def __repr__(self):
        return f'{self.short_name}'

    def as_dict(self):
        # Project meta data
        result = {c.name: getattr(self, c.name) for c in Project.__table__.columns}

        # Users
        result["users"] = []
        result["users"].extend((u.as_dict(), "admin") for u in self.admins)
        result["users"].extend((u.as_dict(), "review") for u in self.reviewers)
        result["users"].extend((u.as_dict(), "segmentation") for u in self.users)

        # Modalities and contrast_types
        result["modalities"] = [m.name for m in self.modalities]
        result["contrast_types"] = [c.name for c in self.contrast_types]
        result["automatic_segmentation_models"] = [m.as_dict() for m in self.automatic_segmentation_models]
        return result
    
    """
    Returns a path where the requested image can be found or stored depending on the type of the image.

    The valid types include:
        'raw' => Raw case images, e.g. when a new case is created
        'manual_segmentation' => Result of the manual segmentation of a user
        'automatic_segmentation' => Result of the automatic segmentation via a machine learning model
                                    In this case, the model needs to be defined. 
                                    The model then defines the concrete directory of the image
    """
    def get_image_path(self, image_type = 'raw', model_id = None, image_id = None):

        if image_id is None:
            app.logger.error("No image id provided")
            return None

        image_dir = None

        if image_type == 'raw':
            image_dir = os.path.join(app.config['DATA_PATH'], self.short_name, "raw")
        elif image_type == 'manual_segmentation':
            image_dir = os.path.join(app.config['DATA_PATH'], self.short_name, "manual_segmentation")
        elif image_type == 'automatic_segmentation':
            if model_id is None:
                app.logger.error("No model id provided")
                return None

            image_dir = os.path.join(app.config['DATA_PATH'], self.short_name, "automatic_segmentation", f"model_{model_id}")
        else:
            app.logger.error(f"Image type {image_type} is not recognized. Returning none")
            return None

        if not os.path.exists(image_dir):
            os.makedirs(image_dir, exist_ok = True)

        return os.path.join(image_dir, f'{image_id}.nii.gz')


    @property
    def role_admins(self):
        return self.admins


    @property
    def role_reviewers(self):
        return self.admins + self.reviewers


    @property
    def role_users(self):
        return self.admins + self.reviewers + self.users


class ProjectsAdmins(db.Model):
    __tablename__ = 'projects_admins'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    project_id = db.Column(db.Integer(), db.ForeignKey('projects.id', ondelete='CASCADE'))


class ProjectsReviewers(db.Model):
    __tablename__ = 'projects_reviewers'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    project_id = db.Column(db.Integer(), db.ForeignKey('projects.id', ondelete='CASCADE'))


class ProjectsUsers(db.Model):
    __tablename__ = 'projects_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    project_id = db.Column(db.Integer(), db.ForeignKey('projects.id', ondelete='CASCADE'))
