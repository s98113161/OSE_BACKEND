import inspect
import sqlite3
import sys
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

DATABASE_NAME = "games.db"
#  取得目前文件資料夾路徑
pjdir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
#  新版本的部份預設為none，會有異常，再設置True即可。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#  設置sqlite檔案路徑
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(pjdir, 'data.sqlite')

db = SQLAlchemy(app)


def get_conn():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


def getDB():
    return db


def create_tables():
    tables = [
        """CREATE TABLE IF NOT EXISTS games(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
				price REAL NOT NULL,
				rate INTEGER NOT NULL
            )
            """,
        """
        CREATE TABLE IF NOT EXISTS Components(
            StoreLocation    TEXT,
            CompName    TEXT UNIQUE,
            CompTypeNo    TEXT,
            FactoryProdNo    TEXT,
            OSEProdNo    TEXT,
            InventoryCount    INTEGER,
            InventorySafeCount    INTEGER,
            CompLabel    TEXT,
            CompSerialNo    TEXT,
            Comment    TEXT,
            CompUUID    INTEGER,
            InstallMachine    TEXT,
            PRIMARY KEY("CompUUID" AUTOINCREMENT) 
    );""",
        """CREATE TABLE IF NOT EXISTS CompPic (
	    CompUUID	INTEGER UNIQUE,
	    ImgSource	BLOB
    );"""
    ]
    conn = get_conn()
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(table)


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
    comment = db.Column(db.String(100), nullable=True)

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
