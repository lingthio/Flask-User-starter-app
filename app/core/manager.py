# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from app import manager


@manager.command
def init_db():
    from app.startup.create_users import create_users

    create_users()