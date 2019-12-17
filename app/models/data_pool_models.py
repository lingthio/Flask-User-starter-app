import enum
from datetime import datetime

from sqlalchemy import Enum

from app import db


class StatusEnum(enum.Enum):
    na = 'na'
    assigned = 'assigned'
    submitted = 'submitted'
    remitted = 'remitted'
    valid = 'valid'


class SplitEnum(enum.Enum):
    train = "train"
    validation = "validation"
    test = "test"


class DataPool(db.Model):
    __tablename__ = 'data_pool'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, )
    type = db.Column(db.String(50), nullable=False)

    name = db.Column(db.Unicode(255), nullable=False, server_default=u'')
    insert_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Relationships
    project = db.relationship('project_models.Project', back_populates='data_pool_objects')
    # project = db.relationship('Project', backref=db.backref('data_pool', lazy='dynamic'))

    __mapper_args__ = {
        'polymorphic_identity': 'datapool',
        'polymorphic_on': type
    }


class Image(DataPool):
    __tablename__ = 'data_pool_images'
    id = db.Column(db.Integer, db.ForeignKey('data_pool.id'), primary_key=True)

    institution = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    accession_number = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    study_date = db.Column(db.DateTime, nullable=True, default=datetime.now)
    study_name = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    study_instance_uid = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    series_name = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    series_number = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    series_instance_uid = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    patient_id = db.Column(db.Unicode(255), nullable=True, server_default=u'')
    patient_dob = db.Column(db.Date, nullable=True, default=datetime.now)
    split = db.Column(Enum(SplitEnum), nullable=True)
    is_valid = db.Column(db.Boolean, nullable=False, default=False)
    # contrast_type      = na, nat, art, ven, mixed
    # body_region        =
    # modality           = # ct, mr, xr ...
    # split              = # training, testing ...

    # Relationships
    manual_segmentation = db.relationship('ManualSegmentation', uselist=False,
                                          foreign_keys='ManualSegmentation.image_id',
                                          back_populates='image',
                                          cascade="all, delete-orphan",
                                          passive_deletes=True)
    automatic_segmentation = db.relationship('AutomaticSegmentation', uselist=False,
                                             foreign_keys='AutomaticSegmentation.image_id',
                                             back_populates='image',
                                             cascade="all, delete-orphan",
                                             passive_deletes=True)

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in DataPool.__table__.columns + Image.__table__.columns}
        if self.manual_segmentation is not None:
            result["manual_segmentation"] = self.manual_segmentation.as_dict()
        if self.automatic_segmentation is not None:
            result["automatic_segmentation"] = self.automatic_segmentation.as_dict()
        if result["split"] is not None:
            result["split"] = self.split.value
        result["project"] = self.project.long_name
        return result

    __mapper_args__ = {
        'polymorphic_identity': 'image',
    }


class ManualSegmentation(DataPool):
    __tablename__ = 'data_pool_manual_segmentations'
    id = db.Column(db.Integer, db.ForeignKey('data_pool.id'), primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('data_pool_images.id', ondelete='CASCADE'),
                         nullable=False, unique=True)

    status = db.Column(Enum(StatusEnum), nullable=False, default="na")
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

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in
                  DataPool.__table__.columns + ManualSegmentation.__table__.columns}

        if self.assignee is not None:
            result["assignee"] = self.assignee.as_dict()
        if self.validated_by is not None:
            result["validated_by"] = self.validated_by.as_dict()
        if self.status is not None:
            result["status"] = self.status.value
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
