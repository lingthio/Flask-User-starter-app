import datetime
from flask import current_app
from app.users.models import User, UserAuth


def init_db(app, db):
    # Automatically create all DB tables in app/app.sqlite file
    db.create_all()

    add_user(app, db, 'manager', 'Manager', 'User', 'manager@example.com', 'manager')
    db.session.commit()


def add_user(app, db, username, first_name, last_name, email, password):
    user_auth = UserAuth.query.filter(UserAuth.username == username).first()
    if not user_auth:
        user_auth = UserAuth(username=username, password=app.user_manager.hash_password(password))
        user = User(
            is_enabled=True,
            first_name=first_name,
            last_name=last_name,
            email=email,
            confirmed_at=datetime.datetime.now(),
            user_auth=user_auth
        )
        db.session.add(user_auth)
        db.session.add(user)


