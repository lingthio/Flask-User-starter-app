from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, SelectField
from wtforms.validators import DataRequired


class ProjectForm(FlaskForm):
    """
    Form class for the project overview page.
    """
    short_name = StringField('short_name')
    long_name = StringField('long_name')
    description = StringField('description')

    users = FieldList(SelectField('users'))
    roles = FieldList(SelectField('roles'))

    delete_project = SubmitField('Delete Projects')
    cancel = SubmitField('Cancel')
    save_changes = SubmitField('Save Changes')
