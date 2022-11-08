from crypt import methods
from hashlib import new
import imp
import os
import re
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, check_permissions, requires_auth
from .auth.auth import get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.route('/')
def index():
    return('Hello world')


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES


@app.route('/drinks', strict_slashes=False)
def get_drinks():
    """returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure"""
    drinks = Drink.query.all()
    drink = [d.short() for d in drinks]
    return jsonify({
        "sucess": True,
        "drinks": drink
    }), 200


@app.route('/drinks-detail', strict_slashes=False)
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure"""
    drinks = Drink.query.all()
    drinks = [d.long() for d in drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    """endpoint to add new drink to the cafe"""
    if not request.get_json():
        abort(404)
    data = request.get_json()
    recipe = [data]
    new_drink = Drink()
    new_drink.title = data['title']
    new_drink.recipe = json.dumps(recipe)
    new_drink.insert()
    return jsonify({
        "success": True,
        "drinks": [new_drink.long()]
    })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    """endpoint to update drinks"""
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not request.get_json():
        abort(404)
    if not drink:
        abort(404)
    data = request.get_json()
    try:
        drink_title = data.get('title')
        drink_recipe = data.get('recipe')
        if drink_title:
            drink.title = drink_title
        if drink_recipe:
            drink.recipe = json.dumps(drink_recipe)
        drink.update()
    except Exception:
        abort(400)
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not id:
        abort(404)
    drink.delete()
    return jsonify({
        "success": True,
        'delete': id
    }), 200


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found():
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
