from datetime import datetime
from sqlalchemy import event
from app import db
from .user_models import User


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.Unicode(16), nullable=False, server_default=u'', unique=True)
    name       = db.Column(db.Unicode(255), nullable=False, server_default=u'')
    active     = db.Column(db.Boolean(), nullable=False, server_default='1')
    inset_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Relationships
    admins   = db.relationship('User', secondary='projects_admins',
                               backref=db.backref('admin_for_project', lazy='dynamic'))
    reviwers = db.relationship('User', secondary='projects_reviewers',
                               backref=db.backref('reviewer_for_project', lazy='dynamic'))
    users    = db.relationship('User', secondary='projects_users',
                               backref=db.backref('user_for_project', lazy='dynamic'))
    def __repr__(self):
        return f'{self.short_name}'


class ProjectsAdmins(db.Model):
    __tablename__ = 'projects_admins'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('projects.id', ondelete='CASCADE'))


class ProjectsReviwers(db.Model):
    __tablename__ = 'projects_reviewers'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('projects.id', ondelete='CASCADE'))


class ProjectsUsers(db.Model):
    __tablename__ = 'projects_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('projects.id', ondelete='CASCADE'))