from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)  
    image_url = db.Column(db.String, nullable=True)
    bio = db.Column(db.String, nullable=True)

    recipes = relationship('Recipe', back_populates='user', cascade="all, delete-orphan")

    serialize_rules = ('-recipes.user',)

    @property
    def password_hash(self):
        raise AttributeError("Password is not accessible!")

    @password_hash.setter
    def password_hash(self, new_password):
        if not new_password:
            raise ValueError("Password cannot be empty") 
        self._password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f'<User {self.id}, {self.username}>'


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)  
    instructions = db.Column(db.String, nullable=False)  
    minutes_to_complete = db.Column(db.Integer, nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  

    user = relationship('User', back_populates='recipes')

    serialize_rules = ('-user.recipes',)

    @validates("instructions")
    def validate_instructions(self, key, value):
        if len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")  
        return value

    @validates("title", "minutes_to_complete", "user_id")
    def validate_required_fields(self, key, value):
        if not value:
            raise ValueError(f"{key} is required.")  
        return value

    def __repr__(self):
        return f'<Recipe {self.id}, {self.title}>'

