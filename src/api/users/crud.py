from src import db
from src.api.users.models import User
import bcrypt


def get_all_users():
    return User.query.all()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_user_by_session_token(session_token):
    return User.query.filter_by(session_token=session_token).first()


def get_user_by_update_token(update_token):
    return User.query.filter(User.update_token == update_token).first()


def add_user(email, password):
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user


def update_user(user, email, password):
    user.password_digest = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=13)
    )
    user.email = email
    db.session.commit()
    return user


def verify_credentials(email, password):
    optional_user = get_user_by_email(email)
    if optional_user is None:
        return False, None

    return optional_user.verify_password(password), optional_user


def create_user(email, password):
    optional_user = get_user_by_email(email)

    if optional_user is not None:
        return False, optional_user

    user = User(email=email, password=password)

    db.session.add(user)
    db.session.commit()

    return True, user


def renew_session(update_token):
    user = get_user_by_update_token(update_token)

    if user is None:
        # DAO layer -> cannot return failures
        raise Exception("Invalid update token")

    user.renew_session()
    db.session.commit()
    return user
