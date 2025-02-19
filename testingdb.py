import sqlite3

connection = sqlite3.connect("storynodes.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM ")