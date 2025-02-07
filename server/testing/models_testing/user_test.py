from sqlalchemy.exc import IntegrityError
import pytest

from app import app
from models import db, User, Recipe

class TestUser:
    '''User in models.py'''

    def test_has_attributes(self):
        '''has attributes username, _password_hash, image_url, and bio.'''

        with app.app_context():
            User.query.delete()
            db.session.commit()

            user = User(
                username="Liz",
                image_url="https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg",
                bio="""Dame Elizabeth Rosemond Taylor DBE (February 27, 1932""" + \
                    """ - March 23, 2011) was a British-American actress. """ + \
                    """She began her career as a child actress in the early""" + \
                    """ 1940s and was one of the most popular stars of """ + \
                    """classical Hollywood cinema in the 1950s."""
            )

            user.password_hash = "whosafraidofvirginiawoolf"  

            db.session.add(user)
            db.session.commit()

            created_user = User.query.filter_by(username="Liz").first()

            assert created_user is not None 
            assert created_user.username == "Liz"
            assert created_user.image_url == "https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg"
            assert created_user.bio.startswith("Dame Elizabeth Rosemond Taylor")  

            assert created_user._password_hash is not None  

            with pytest.raises(AttributeError):  
                created_user.password_hash


    def test_requires_username(self):
        '''requires each record to have a username.'''

        with app.app_context():

            User.query.delete()
            db.session.commit()

            user = User()
            with pytest.raises(IntegrityError):
                db.session.add(user)
                db.session.commit()

    def test_requires_unique_username(self):
        '''requires each record to have a username.'''

        with app.app_context():

            User.query.delete()
            db.session.commit()

            user_1 = User(username="Ben")
            user_2 = User(username="Ben")

            with pytest.raises(IntegrityError):
                db.session.add_all([user_1, user_2])
                db.session.commit()

    def test_has_list_of_recipes(self):
      '''has records with lists of recipes records attached.'''

      with app.app_context():
        Recipe.query.delete()
        User.query.delete()
        db.session.commit()

        user = User(username="Prabhdip")
        user.password_hash = "securepassword"
        db.session.add(user)
        db.session.commit()  

        recipe_1 = Recipe(
            title="Delicious Shed Ham",
            instructions="A very long set of instructions that exceed 50 characters...",
            minutes_to_complete=60,
            user_id=user.id  
        )

        recipe_2 = Recipe(
            title="Hasty Party Ham",
            instructions="Another long set of instructions that exceed 50 characters...",
            minutes_to_complete=30,
            user_id=user.id  
        )

        db.session.add_all([recipe_1, recipe_2])
        db.session.commit()  

        assert user.id is not None
        assert recipe_1.id is not None
        assert recipe_2.id is not None

        assert recipe_1 in user.recipes
        assert recipe_2 in user.recipes
