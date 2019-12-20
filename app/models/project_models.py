from datetime import datetime
from sqlalchemy import event
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

    def __repr__(self):
        return f'{self.short_name}'

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in Project.__table__.columns}
        return result


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
