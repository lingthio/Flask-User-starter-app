import json
import os

from app import db, current_project

from app.models.project_models import Project
from app.models.user_models import User
from app.models.data_pool_models import Image, ManualSegmentation, Message, Modality, ContrastType

# MESSAGES

def get_all_messages_for_manual_segmentation(manual_segmentation_id = None):

    if manual_segmentation_id is None:
        return None

    messages = Message.query.filter(Message.manual_segmentation_id == manual_segmentation_id).all()

    return messages

# END MESSAGES

# MODALITY

def get_all_modalities_for_project(project_id = None):

    if project_id is None:
        return None

    modalities = Modality.query.filter(Modality.project_id == project_id).all()

    return modalities

"""
Finds a Modality by it's id

If the id is not provided, logs error and returns None
"""
def find_modality(id = None):

    if id:
        modality = Modality.query.get(id)
    else:
        app.logger.error("No parameters given for modality search")
        
        return None

    return modality

"""
Creates a new Modality object in the database with the given parameters
"""
def create_modality(name = None, project_id = None):

    modality = Modality(name = name, project_id = project_id)

    db.session.add(modality)
    db.session.commit()

    return modality

"""
Deletes a modality object
"""
def delete_modality(modality):

    if modality:
        db.session.delete(modality)
        db.session.commit()

    return modality

# END MODALITY

# CONTRAST_TYPE

def get_all_contrast_types_for_project(project_id = None):

    if project_id is None:
        return None

    modalities = ContrastType.query.filter(ContrastType.project_id == project_id).all()

    return modalities

"""
Finds an existing contrast type object in the database by it's id

If no id is provided, log's error and returns None
"""
def find_contrast_type(id = None):

    if id:
        contrast_type = ContrastType.query.get(id)
    else:
        app.logger.error("No parameters given for contrast type search")
        
        return None

    return contrast_type

"""
Creates a contrast type object with the given parameters
"""
def create_contrast_type(name = None, project_id = None):

    contrast_type = ContrastType(name = name, project_id = project_id)

    db.session.add(contrast_type)
    db.session.commit()

    return contrast_type

"""
Deletes an existing contrast type object
"""
def delete_contrast_type(contrast_type):

    if contrast_type:
        db.session.delete(contrast_type)
        db.session.commit()

    return contrast_type

# END CONTRAST_TYPE