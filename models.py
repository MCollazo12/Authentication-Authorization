from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.init_app(app)


class User(db.Model):

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.Text(), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Registers a user"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        user = cls(
            username=username,
            password=hashed_utf8,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        
        db.session.add(user)
        return user
        

    @classmethod
    def authenticate(cls, username, password):
        """
        Validate that a user exists and their password is correct.
        Return the user if valid; else, False.
        """
        valid_usr = cls.query.filter_by(username=username).first()

        if valid_usr and bcrypt.check_password_hash(valid_usr.password, password):
            return valid_usr
        else:
            return False

class Feedback(db.Model):
    """ Feedback model"""
    
    __tablename__ = "feedback"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)
    
    user = db.relationship('User', backref='feedback')
    
    def __repr__(self):
        return f"<Feedback id={self.id} title={self.title} username={self.username}"