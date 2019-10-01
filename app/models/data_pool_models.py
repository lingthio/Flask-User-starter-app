from datetime import datetime
from sqlalchemy import event
from app import db
from .user_models import User
from .project_models import Project


class DataPool(db.Model):
    __tablename__ = 'data_pool'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    name = db.Column(db.Unicode(255), nullable=False, server_default=u'')
    inset_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Relationships
    project = db.relationship('Project', backref=db.backref('data_pool', lazy='dynamic'))

    __mapper_args__ = {
        'polymorphic_identity':'datapool',
        'polymorphic_on': type
    }


class Image(DataPool):
    __tablename__ = 'data_pool_images'
    id = db.Column(db.Integer, db.ForeignKey('data_pool.id'), primary_key=True)

    institution        = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    accession_number   = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    study_date         = db.Column(db.DateTime, nullable=True, server_default=u'')
    study_name         = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    study_instance_uid = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    series_name        = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    series_number      = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    series_instance_uid = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    patient_id         = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    patient_dob        = db.Column(db.Date, nullable=True, server_default=u'')
    #contrast_type      = na, nat, art, ven, mixed
    #body_region        = 
    #modality           = # ct, mr, xr ...
    #split              = # training, testing ...
    

    __mapper_args__ = {
        'polymorphic_identity':'image',
    }


class ManualSegmentation(DataPool):
    __tablename__ = 'data_pool_manual_segmentation'
    id = db.Column(db.Integer, db.ForeignKey('data_pool.id'), primary_key=True)

    #status = na, assigned, submitted, remitted, accepted

    assignee_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_date   = db.Column(db.DateTime, nullable=True)
    validated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    validation_date = db.Column(db.DateTime, nullable=True)


    # Relationships
    #assignee     = db.relationship('User', backref=db.backref('assigned_segmentations', lazy='dynamic'))
    #validated_by = db.relationship('User', backref=db.backref('validated_segmentations', lazy='dynamic'))
    
    __mapper_args__ = {
        'polymorphic_identity':'manual_segmentation',
    }


class AutomaticSegmentation(DataPool):
    __tablename__ = 'data_pool_automatic_segmentation'
    id = db.Column(db.Integer, db.ForeignKey('data_pool.id'), primary_key=True)

    #model_id     = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=True)

    # Relationships
    # ToDo
    
    __mapper_args__ = {
        'polymorphic_identity':'automatic_segmentation',
    }