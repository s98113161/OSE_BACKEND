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

from sqlalchemy.exc import IntegrityError
from sqlalchemy_serializer import SerializerMixin

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

pjdir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
#  新版本的部份預設為none，會有異常，再設置True即可。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#  設置sqlite檔案路徑
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(pjdir, 'data.sqlite')
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
# for file upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

jwt = JWTManager(app)
db = SQLAlchemy(app)

""" JWT """


# === GEN JWT TOKEN ====
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("userID", None)
    password = request.json.get("userPWD", None)
    if username == "admin" or password == "admin":
        additional_claims = {"role": "admin", "chName": "羅大佑"}
    elif username == "user" and password == "user":
        additional_claims = {"role": "user", "chName": "陳使用"}
    else:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=username, additional_claims=additional_claims)
    return jsonify(access_token=access_token)


# === 測試保護URL ====
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


""" Components Controller """


# 新增 Components
@app.route("/components", methods=["POST"])
@jwt_required()
def insert_comp():
    data = request.get_json()
    comp = Components(**data)
    comp.createUser = get_jwt_identity()
    db.session.add(comp)
    try:
        db.session.commit()
    except IntegrityError:
        return "key值產品名稱不能重複", 500

    return comp.to_dict()


# 取得 Components
@app.route("/components", methods=["GET"])
@jwt_required()
def get_comps():
    uuid = request.args.get('uuid')
    if uuid is None:
        comps = Components.query.all()
        result = []
        for u in comps:
            result.append(u.to_dict())
        return jsonify(result)
    else:
        result = db.session.query(Components).filter(Components.compUUID == uuid).first()
        return result.to_dict()


# 更新 Components
@app.route("/components", methods=["PATCH"])
@jwt_required()
def update_comps():
    data = request.get_json()
    comp = Components(**data)
    # 轉成DICT
    comp_dic = comp.to_dict()
    # 移除新增時間，避免誤刪
    comp_dic.pop("createTime")
    comp_dic.pop("updateTime")
    print(comp_dic)
    result = db.session.query(Components).filter(Components.compUUID == comp_dic.get("compUUID")).update(comp_dic)
    db.session.commit()
    print(result)
    return comp_dic


# 移除 Components
@app.route("/components", methods=["DELETE"])
@jwt_required()
def delete_comps():
    uuid = request.args.get('uuid')
    if uuid is None:
        return "uuid is required.", 400
    else:
        result = Components.query.filter_by(compUUID=uuid).delete()
        print(result)
        db.session.commit()
        return str(result)


# 取得 Components images
@app.route("/components/image", methods=["GET"])
@jwt_required()
def get_comps_images():
    uuid = request.args.get('uuid')
    if uuid is None:
        return "uuid is required.", 400
    else:
        comppics = db.session.query(CompPic).filter(CompPic.compUUID == uuid).all()
        result = []
        for u in comppics:
            result.append(u.to_dict())
        return jsonify(result)


# 上傳 Components images
@app.route("/components/image", methods=["POST"])
@jwt_required()
def upload_comps_images():
    uuid = request.args.get('uuid')
    if uuid is None:
        return "uuid is required.", 400
    f = request.files['file']
    # 把 file 讀成 base64
    encoded_string = base64.b64encode(f.read())
    comp_pic = CompPic(compUUID=uuid, imgSource=encoded_string)
    db.session.add(comp_pic)
    db.session.commit()
    return 'ok', 200


# 移除 特定 Components 的特定 images
@app.route("/components/image", methods=["DELETE"])
@jwt_required()
def delete_comps_spec_image():
    uuid = request.args.get('uuid')
    imguuid = request.args.get('imguuid')
    if uuid is None or imguuid is None:
        return "uuid and imguuid is required.", 400
    result = CompPic.query.filter_by(compUUID=uuid, compPicUUID=imguuid).delete()
    print(result)
    db.session.commit()
    return str(result), 200


"""
Enable CORS. Disable it if you don't need CORS
"""


@app.after_request
def after_request(response):
    response.headers[
        "Access-Control-Allow-Origin"] = "*"  # <- You can change "*" for a domain for example "http://localhost"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PATCH, PUT, DELETE"
    response.headers[
        "Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    return response


"""
模組定義區
"""


class Components(db.Model, SerializerMixin):
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
    createUser = db.Column(db.String(100), nullable=True)
    updateTime = db.Column(db.DateTime, onupdate=datetime.now, default=datetime.now)
    updateUser = db.Column(db.String(100), nullable=True)

    def __init__(self, compName, storeLocation="", compTypeNo="", factoryProdNo="", oseProdNo="", inventoryCount=0,
                 inventorySafeCount=0, compLabel="", compSerialNo="", comment="", compUUID=None, createTime="",
                 createUser="",
                 updateTime="", updateUser=""):
        self.compUUID = compUUID
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
        self.createUser = createUser
        self.updateUser = updateUser


class CompPic(db.Model, SerializerMixin):
    compPicUUID = db.Column(db.Integer, nullable=False, primary_key=True)
    compUUID = db.Column(db.Integer, nullable=False)
    imgSource = db.Column(db.BLOB, nullable=True)
    createTime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, compUUID, imgSource):
        self.compUUID = compUUID
        self.imgSource = imgSource


class CompInvHistory(db.Model, SerializerMixin):
    CompInvHistoryUUID = db.Column(db.Integer, nullable=False, primary_key=True)
    compUUID = db.Column(db.Integer, nullable=False)
    imgSource = db.Column(db.BLOB, nullable=True)
    takenUser = db.Column(db.BLOB, nullable=True)
    createTime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, compUUID, imgSource):
        self.compUUID = compUUID
        self.imgSource = imgSource


class User(db.Model, SerializerMixin):
    account = db.Column(db.String(100), nullable=False, primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    createTime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, account, password):
        self.account = account
        self.password = password


if __name__ == "__main__":
    # create_tables()
    db.create_all()
    """
    Here you can change debug and port
    Remember that, in order to make this API functional, you must set debug in False
    """
    app.run(host='127.0.0.1', port=8000, debug=False)
