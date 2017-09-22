import uuid
import src.models.users.constants as UserConstants
from src.common.database import Database
from src.common.utils import Utils
import src.models.users.errors as UserErrors
from src.models.alerts.alert import Alert


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<User {}>".format(self.email)

    @staticmethod
    def is_login_valid(email, password):
        """
        This method verifies that an email-password combo is valid or not
        checks that email exists and that the password associated to that email is correct
        :param email: the user's email
        :param password: a sha512 hashed password
        :return: true of valid, false if not
        """
        user_data=Database.find_one(UserConstants.COLLECTION, {"email": email})  # password in sha512 -> pbkdf2_sha512
        if user_data is None:
            # tell the user email doesn't exist
            raise UserErrors.UserNotExistsError("Your user does not exist.")
        if not Utils.check_hashed_password(password, user_data['password']):
            # tell the user that their password is wrong
            raise UserErrors.IncorrectPasswordError("The password you entered is incorrect.")

        return True

    @staticmethod
    def register_user(email, password):
        user_data = Database.find_one(UserConstants.COLLECTION, {"email": email})

        if user_data is not None:
            raise UserErrors.UserAlreadyRegisteredError("The e-mail you used to register already exists.")
        if not Utils.email_is_valid(email):
            raise UserErrors.InvalidEmailError("The e-mail you entered does not have the right format.")

        User(email, Utils.hash_password(password)).save_to_db()

        return True

    def save_to_db(self):
        Database.insert(UserConstants.COLLECTION, self.json())

    def json(self):
        return {
            "_id": self._id,
            "email": self.email,
            "password": self.password
        }

    @classmethod
    def find_by_email(cls, email):
        return cls(**Database.find_one(UserConstants.COLLECTION, {'email': email}))

    def get_alerts(self):
        return Alert.find_by_user_email(self.email)
