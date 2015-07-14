from __future__ import print_function
import datetime

from app import db, create_app, create_users


def reset_db(app, db):
    """
    Drop all tables, then Create all tables
    """

    # Drop all tables
    print('Dropping all tables')
    db.drop_all()

    # Create all tables
    print('Creating all tables')
    db.create_all()

    print(create_users)
    create_users()


# Initialize the app and reset the database
if __name__ == "__main__":
    app = create_app()
    reset_db(app, db)
