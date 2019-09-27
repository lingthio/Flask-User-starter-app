from sqlalchemy import event
from app import db
from .user_models import User

# Define the User data model. Make sure to add the flask_user.UserMixin !!
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)

    short_name = db.Column(db.Unicode(16), nullable=False, server_default=u'', unique=True)
    name       = db.Column(db.Unicode(255), nullable=False, server_default=u'')
    active     = db.Column(db.Boolean(), nullable=False, server_default='0')

    # Relationships
    admins   = db.relationship('User', secondary='projects_admins',
                               backref=db.backref('admin_for_project', lazy='dynamic'))
    reviwers = db.relationship('User', secondary='projects_reviewers',
                               backref=db.backref('reviewer_for_project', lazy='dynamic'))
    
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
