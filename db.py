import sqlite3
DATABASE_NAME = "games.db"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


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
        CREATE TABLE IF NOT EXISTS Componets(
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
    db = get_db()
    cursor = db.cursor()
    for table in tables:
        cursor.execute(table)
