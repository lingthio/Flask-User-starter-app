from os import path, makedirs
import enum
from datetime import datetime
from sqlalchemy import Enum, UniqueConstraint
from app import db
from flask import current_app as c_app
import nibabel as nib


class StatusEnum(enum.Enum):
    new = 'new'
    open_for_segmentation = 'open_for_segmentation'
    assigned = 'assigned'
    submitted = 'submitted'
    rejected = 'rejected'
    valid = 'valid'


class SplitEnum(enum.Enum):
    train = 'train'
    validation = 'validation'
    test = 'test'


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    manual_segmentation_id = db.Column(db.Integer, db.ForeignKey('data_pool_manual_segmentations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(500))

    user = db.relationship('user_models.User', foreign_keys=user_id)
    manual_segmentation = db.relationship('ManualSegmentation', foreign_keys=manual_segmentation_id, uselist=False)

    def as_dict(self):
        return dict(
            user=self.user.as_dict(),
            date=self.date,
            message=self.message
        )


class Modality(db.Model):
    __tablename__ = 'modality'
    __table_args__ = (UniqueConstraint('name', 'project_id'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, )

    project = db.relationship('project_models.Project', back_populates='modalities')


class ContrastType(db.Model):
    __tablename__ = 'contrast_type'
    __table_args__ = (UniqueConstraint('name', 'project_id'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, )

    project = db.relationship('project_models.Project', back_populates='contrast_types')


class DataPool(db.Model):
    __tablename__ = 'data_pool'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, )
    type = db.Column(db.String(50), nullable=False)

    insert_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Relationships
    project = db.relationship('project_models.Project', back_populates='data_pool_objects')

    __mapper_args__ = {
        'polymorphic_identity': 'datapool',
        'polymorphic_on': type
    }

    def __get_fn__(self):
        assert self.id != None, 'you need to flush or commit the data pool object before accessing nifti data'
        basepath = path.join(c_app.config['DATA_PATH'], self.project.short_name)
        if not path.exists(basepath):
            makedirs(basepath, exist_ok=True)
        return path.join(basepath, f'{self.id}.nii.gz')

    def __get_nii__(self):
        return nib.load(self.__get_fn__())
    
    def __set_nii__(self, nii):
        nii.to_filename(self.__get_fn__())
        nii.uncache()
    
    nii = property(__get_nii__, __set_nii__)



class Image(DataPool):
    __tablename__ = 'data_pool_images'
    id = db.Column(db.Integer, db.ForeignKey('data_pool.id'), primary_key=True)
    name = db.Column(db.Unicode(255), nullable=False, server_default='', unique=True)

    institution = db.Column(db.Unicode(255), nullable=True, server_default='')
    accession_number = db.Column(db.Unicode(255), nullable=True, server_default='')
    study_date = db.Column(db.DateTime, nullable=True, default=datetime.now)
    study_name = db.Column(db.Unicode(255), nullable=True, server_default='')
    study_instance_uid = db.Column(db.Unicode(255), nullable=True, server_default='')
    study_number = db.Column(db.Unicode(255), nullable=True, server_default='')
    study_description = db.Column(db.Unicode(255), nullable=True, server_default='')

    series_name = db.Column(db.Unicode(255), nullable=True, server_default='')
    series_number = db.Column(db.Unicode(255), nullable=True, server_default='')
    series_instance_uid = db.Column(db.Unicode(255), nullable=True, server_default='')
    series_description = db.Column(db.Unicode(255), nullable=True, server_default='')

    patient_name = db.Column(db.Unicode(255), nullable=True, server_default='')
    patient_dob = db.Column(db.Date, nullable=True, default=datetime.now)
    split = db.Column(Enum(SplitEnum), nullable=True)
    body_region = db.Column(db.Unicode(255), nullable=True, server_default='')

    contrast_type_id = db.Column(db.ForeignKey('contrast_type.id'), nullable=True, server_default='')
    modality_id = db.Column(db.ForeignKey('modality.id'), nullable=True, server_default='')

    custom_1 = db.Column(db.Unicode(255), nullable=True, server_default='')
    custom_2 = db.Column(db.Unicode(255), nullable=True, server_default='')
    custom_3 = db.Column(db.Unicode(255), nullable=True, server_default='')

    # Relationships
    manual_segmentation = db.relationship('ManualSegmentation', uselist=False,
                                          foreign_keys='ManualSegmentation.image_id',
                                          back_populates='image',
                                          cascade='all, delete-orphan',
                                          passive_deletes=True)
    automatic_segmentation = db.relationship('AutomaticSegmentation', uselist=False,
                                             foreign_keys='AutomaticSegmentation.image_id',
                                             back_populates='image',
                                             cascade='all, delete-orphan',
                                             passive_deletes=True)
    contrast_type = db.relationship('ContrastType', foreign_keys=[contrast_type_id], uselist=False)
    modality = db.relationship('Modality', foreign_keys=[modality_id], uselist=False)

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in DataPool.__table__.columns + Image.__table__.columns}
        if self.manual_segmentation is not None:
            result['manual_segmentation'] = self.manual_segmentation.as_dict()
        if self.automatic_segmentation is not None:
            result['automatic_segmentation'] = self.automatic_segmentation.as_dict()
        if result['split'] is not None:
            result['split'] = self.split.value
        result['project'] = self.project.long_name
        result['modality'] = '' if self.modality is None else self.modality.name
        result['contrast_type'] = '' if self.contrast_type is None else self.contrast_type.name
        return result

    __mapper_args__ = {
        'polymorphic_identity': 'image',
    }


class ManualSegmentation(DataPool):
    __tablename__ = 'data_pool_manual_segmentations'
    id = db.Column(db.Integer, db.ForeignKey('data_pool.id'), primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('data_pool_images.id', ondelete='CASCADE'),
                         nullable=False, unique=True)

    status = db.Column(Enum(StatusEnum), nullable=False, default='new')
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_date = db.Column(db.DateTime, nullable=True)
    validated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    validation_date = db.Column(db.DateTime, nullable=True)

    # Relationships
    image = db.relationship('Image', foreign_keys=[image_id],
                            uselist=False, back_populates='manual_segmentation')
    assignee = db.relationship('user_models.User', foreign_keys=[assignee_id],
                               back_populates='segmentations_assigned')
    validated_by = db.relationship('user_models.User', foreign_keys=[validated_by_id],
                                   back_populates='segmentations_validated')
    messages = db.relationship('Message', foreign_keys=[Message.manual_segmentation_id])

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in
                  DataPool.__table__.columns + ManualSegmentation.__table__.columns}

        if self.assignee is not None:
            result['assignee'] = self.assignee.as_dict()
        if self.validated_by is not None:
            result['validated_by'] = self.validated_by.as_dict()
        if self.status is not None:
            result['status'] = self.status.value
        result['messages'] = [m.as_dict() for m in self.messages]
        return result

    __mapper_args__ = {
        'polymorphic_identity': 'manual_segmentation',
    }


class AutomaticSegmentation(DataPool):
    __tablename__ = 'data_pool_automatic_segmentations'
    id = db.Column(db.Integer, db.ForeignKey('data_pool.id', ondelete='CASCADE'), primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('data_pool_images.id', ondelete='CASCADE'),
                         nullable=False, unique=True)

    # model_id     = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=True)

    # Relationships
    image = db.relationship('Image', foreign_keys=[image_id],
                            uselist=False, back_populates='automatic_segmentation')

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in
                  DataPool.__table__.columns + AutomaticSegmentation.__table__.columns}
        return result

    __mapper_args__ = {
        'polymorphic_identity': 'automatic_segmentation',
    }
