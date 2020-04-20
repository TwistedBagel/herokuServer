# import sqlite3
import os
import psycopg2
import psycopg2.extras
import urllib.parse

class OfficerDB:

    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
                cursor_factory = psycopg2.extras.RealDictCursor,
                database = url.path[1:],
                user = url.username,
                password = url.password,
                host = url.hostname,
                port = url.port
        )

        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def createOfficersTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS officers (id SERIAL PRIMARY KEY, name VARCHAR(255), rank VARCHAR(255), station VARCHAR(255), ship VARCHAR(255), species VARCHAR(255)")
        self.connection.commit()
    
    def createUsersTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, fName VARCHAR(255), lName VARCHAR(255), email VARCHAR(255), pass VARCHAR(255)")
        self.connection.commit()

    def getAllOfficers(self):
        self.cursor.execute("SELECT * FROM officers ORDER BY id")
        return self.cursor.fetchall()

    def getOfficer(self, o_id):
        data = [o_id]
        self.cursor.execute("SELECT * FROM officers WHERE id = %s", data)
        return self.cursor.fetchone()
    
    def insertOfficer(self, name, rank, station, ship, species):
        data = [name, rank, station, ship, species]
        self.cursor.execute("INSERT INTO officers (name, rank, station, ship, species) VALUES (%s, %s, %s, %s, %s)", data)
        self.connection.commit()
        return None

    def updateOfficer(self, name, rank, station, ship, species, oID):
        data = [name, rank, station, ship, species, oID]
        self.cursor.execute("UPDATE officers SET name = %s, rank = %s, station = %s, ship = %s, species = %s WHERE id = %s", data)
        self.connection.commit()
        return None
    
    def deleteOfficer(self, oID):
        data = [oID]
        self.cursor.execute("DELETE FROM officers WHERE id = %s", data)
        self.connection.commit()
        return None
    
    def registerUser(self, fName, lName, email, password):
        data = [fName, lName, email, password]
        self.cursor.execute("INSERT INTO users (fName, lName, email, pass) VALUES (%s, %s, %s, %s)", data)
        self.connection.commit()
        return None
    
    def getUserEmail(self, email):
        data = [email]
        self.cursor.execute("SELECT * FROM users WHERE email = %s", data)
        return self.cursor.fetchone()
