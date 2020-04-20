import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class OfficerDB:

    def __init__(self):
        self.connection = sqlite3.connect('officers.db')
        self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()
    
    def insertOfficer(self, name, rank, station, ship, species):
        data = [name, rank, station, ship, species]
        self.cursor.execute('INSERT INTO officers (name, rank, station, ship, species) VALUES (?, ?, ?, ?, ?)', data)
        self.connection.commit()
    
    def getAllOfficers(self):
        self.cursor.execute('SELECT * FROM officers')
        officers = self.cursor.fetchall()
        return officers
    
    def getOfficer(self, o_id):
        data = [o_id]
        self.cursor.execute('SELECT * FROM officers WHERE id = ?', data)
        return self.cursor.fetchone()
    
    def updateOfficer(self, name, rank, station, ship, species, oID):
        data = [name, rank, station, ship, species, oID]
        self.cursor.execute('UPDATE officers SET name = ?, rank = ?, station = ?, ship = ?, species = ? WHERE id = ?', data)
        self.connection.commit()
    
    def deleteOfficer(self, oID):
        data = [oID]
        self.cursor.execute('DELETE FROM officers WHERE id = ?', data)
        self.connection.commit()
    
    def getUserEmail(self, email):
        data = [email]
        self.cursor.execute("SELECT * FROM users WHERE email = ?", data)
        result = self.cursor.fetchone()
        return result
    
    def registerUser(self, fName, lName, email, password):
        data = [fName, lName, email, password]
        self.cursor.execute("INSERT INTO users (fName, lName, email, pass) VALUES (?, ?, ?, ?)", data)
        self.connection.commit()