import base64
import json
import os

from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import game_controller

pjdir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
#  新版本的部份預設為none，會有異常，再設置True即可。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#  設置sqlite檔案路徑
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(pjdir, 'data.sqlite')
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)
db = SQLAlchemy(app)


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/games', methods=["GET"])
def get_games():
    games = game_controller.get_games()
    return jsonify(games)


@app.route("/new", methods=["POST"])
def insert_game():
    # game_details = request.get_json()
    # name = game_details["name"]
    # price = game_details["price"]
    # rate = game_details["rate"]
    # result = game_controller.insert_game(name, price, rate)
    # return jsonify(result)
    data = {
        # 'compUUID': 'A1923',
        'storeLocation': 'Area1',
        'compName': '風扇22',
        'compTypeNo': 'B001',
        'factoryProdNo': 'FAC001',
        'oseProdNo': 'oseP01',
        'inventoryCount': 50,
        'inventorySafeCount': 20,
        'compLabel': '標籤01',
        'compSerialNo': 'ser001',
        'comment': '我是註解，寫了一些註解 :D'
    }
    comp = Components(**data)
    db.session.add(comp)
    db.session.commit()
    print(comp.compUUID)

    with open("test.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    comp_pic = CompPic(compUUID=comp.compUUID, imgSource=encoded_string)
    db.session.add(comp_pic)
    db.session.commit()
    return comp


@app.route("/game", methods=["PUT"])
def update_game():
    game_details = request.get_json()
    id = game_details["id"]
    name = game_details["name"]
    price = game_details["price"]
    rate = game_details["rate"]
    result = game_controller.update_game(id, name, price, rate)
    return jsonify(result)


@app.route("/game/<id>", methods=["DELETE"])
def delete_game(id):
    result = game_controller.delete_game(id)
    return jsonify(result)


@app.route("/game/<id>", methods=["GET"])
def get_game_by_id(id):
    game = game_controller.get_by_id(id)
    return jsonify(game)


"""
Enable CORS. Disable it if you don't need CORS
"""


@app.after_request
def after_request(response):
    response.headers[
        "Access-Control-Allow-Origin"] = "*"  # <- You can change "*" for a domain for example "http://localhost"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response.headers[
        "Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    return response


class Components(db.Model):
    compUUID = db.Column(db.Integer, nullable=False, primary_key=True)
    storeLocation = db.Column(db.String(100), nullable=True)
    compName = db.Column(db.String(30), unique=True, nullable=False)
    compTypeNo = db.Column(db.String(100), nullable=True)
    factoryProdNo = db.Column(db.String(100), nullable=True)
    oseProdNo = db.Column(db.String(100), nullable=True)
    inventoryCount = db.Column(db.Integer, nullable=True)
    inventorySafeCount = db.Column(db.Integer, nullable=True)
    compLabel = db.Column(db.String(10), nullable=True)
    compSerialNo = db.Column(db.String(10), nullable=True)
    comment = db.Column(db.String(500), nullable=True)

    createTime = db.Column(db.DateTime, default=datetime.now)
    updateTime = db.Column(db.DateTime, onupdate=datetime.now, default=datetime.now)

    def __init__(self, storeLocation, compName, compTypeNo, factoryProdNo, oseProdNo, inventoryCount,
                 inventorySafeCount, compLabel, compSerialNo, comment):
        self.storeLocation = storeLocation
        self.compName = compName
        self.compTypeNo = compTypeNo
        self.factoryProdNo = factoryProdNo
        self.oseProdNo = oseProdNo
        self.inventoryCount = inventoryCount
        self.inventorySafeCount = inventorySafeCount
        self.compLabel = compLabel
        self.compSerialNo = compSerialNo
        self.comment = comment


class CompPic(db.Model):
    compUUID = db.Column(db.Integer, nullable=False, primary_key=True)
    imgSource = db.Column(db.BLOB, nullable=True)

    def __init__(self, compUUID, imgSource):
        self.compUUID = compUUID
        self.imgSource = imgSource


class User(db.Model):
    account = db.Column(db.BLOB, nullable=False, primary_key=True)

    def __init__(self, compUUID, imgSource):
        self.compUUID = compUUID
        self.imgSource = imgSource


if __name__ == "__main__":
    # create_tables()
    db.create_all()
    """
    Here you can change debug and port
    Remember that, in order to make this API functional, you must set debug in False
    """
    app.run(host='127.0.0.1', port=8000, debug=False)
