#!/usr/bin/env python3

from flask import request, session, jsonify, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_user = User(
                username=data["username"],
                image_url=data.get("image_url", ""),
                bio=data.get("bio", ""),
            )
            new_user.password_hash = data["password"]
            db.session.add(new_user)
            db.session.commit()

            session["user_id"] = new_user.id
            return make_response(new_user.to_dict(), 201)

        except IntegrityError:
            db.session.rollback()
            return make_response({"error": "Username already exists."}, 422)
        
        except Exception as e:
            return make_response({"error": str(e)}, 422)

api.add_resource(Signup, "/signup")

class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")  
        if not user_id:
            return make_response({"error": "Unauthorized"}, 401) 
        
        user = db.session.get(User, user_id)  
        if user is None:  
            return make_response({"error": "Unauthorized"}, 401)

        return make_response(user.to_dict(), 200)


api.add_resource(CheckSession, "/check_session")

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data["username"]).first()

        if user and user.authenticate(data["password"]):
            session["user_id"] = user.id
            return make_response(user.to_dict(), 200)
        return make_response({"error": "Invalid username or password"}, 401)

api.add_resource(Login, "/login")

class Logout(Resource):
    def delete(self):
        if "user_id" not in session or session.get("user_id") is None :
            return make_response({"error": "Unauthorized"}, 401)  

        session.pop("user_id", None)
        return "", 204  

api.add_resource(Logout, "/logout")

class RecipeIndex(Resource):
    def get(self):
        if "user_id" not in session or session.get("user_id") is None:
            return make_response({"error": "Unauthorized"}, 401) 
        
        recipes = [recipe.to_dict() for recipe in Recipe.query.all()]
        return make_response(jsonify(recipes), 200)


    def post(self):
        if "user_id" not in session:
            return make_response({"error": "Unauthorized"}, 401)

        data = request.get_json()
        try:
            new_recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=session["user_id"],
            )
            db.session.add(new_recipe)
            db.session.commit()
            return make_response(new_recipe.to_dict(), 201)
        except Exception as e:
            return make_response({"error": str(e)}, 422)

api.add_resource(RecipeIndex, "/recipes")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
