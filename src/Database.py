import sqlite3

def get_db():
    db_filename = "../sql/database.sqlite3"
    connection = sqlite3.connect(str(db_filename))
    # backwards compatibility thing?
    connection.execute("PRAGMA foreign_keys = ON")
    return connection