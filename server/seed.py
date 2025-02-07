#!/usr/bin/env python3

from random import randint, choice as rc
from faker import Faker
from app import app
from models import db, Recipe, User

fake = Faker()

with app.app_context():
    print("Deleting all records...")
    Recipe.query.delete()
    User.query.delete()

    print("Creating users...")
    users = []
    for _ in range(10):
        user = User(
            username=fake.first_name(),
            bio=fake.paragraph(nb_sentences=3),
            image_url=fake.image_url(),
        )
        user.password_hash = "password123" 
        users.append(user)

    db.session.add_all(users)
    db.session.commit() 

    print("Creating recipes...")
    recipes = []
    for _ in range(20):
        user = rc(users)  
        recipe = Recipe(
            title=fake.sentence(),
            instructions=fake.paragraph(nb_sentences=10),
            minutes_to_complete=randint(15, 90),
            user_id=user.id, 
        )
        recipes.append(recipe)

    db.session.add_all(recipes)
    db.session.commit()
    print("Database seeded successfully!")




