from http.server import BaseHTTPRequestHandler as ReqHandle
from http.server import HTTPServer as HttpServer
from urllib.parse import parse_qs
import json
from db import OfficerDB
from http import cookies
from session_store import SessionStore
from passlib.hash import bcrypt
import sys

gSessionStore = SessionStore()

class MyReqHandle(ReqHandle):

    def end_headers(self):
        self.send_cookie()
        # self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Origin", '*') 
        self.send_header("Access-Control-Allow-Credentials", "true")
        ReqHandle.end_headers(self)

    def load_cookie(self):
        # read header
        # capture cookie or create if nonexistant
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers['Cookie'])
        else:
            self.cookie = cookies.SimpleCookie()

    def send_cookie(self):
        # write header, send cookie (if any)
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())
    
    def load_session_data(self):
        self.load_cookie()

        if "sessionID" in self.cookie:
            sessionID = self.cookie["sessionID"].value
            self.sessionData = gSessionStore.getSessionData(sessionID)

            if self.sessionData == None:
                sessionID = gSessionStore.createSession()
                self.sessionData = gSessionStore.getSessionData(sessionID)
                self.cookie['sessionID'] = sessionID

        else:
            sessionID = gSessionStore.createSession()
            self.sessionData = gSessionStore.getSessionData(sessionID)
            self.cookie['sessionID'] = sessionID

    def handleNotFound(self):
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(bytes('Not Found', 'utf-8'))
    
    def handleRetrieveMember(self, o_id):
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            return

        db = OfficerDB()
        officers = db.getOfficer(o_id)
        if officers:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(officers), 'utf-8'))
        else:
            self.handleNotFound()

    def handleRetrieveCollection(self):
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            print('userID not existing in get')
            return

        db = OfficerDB()
        officers = db.getAllOfficers()

        if officers:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            self.wfile.write(bytes(json.dumps(officers), 'utf-8'))
        else:
            self.handleNotFound()

    def handleCreate(self):
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            print("userID not existing in create")
            return
        
        length = self.headers['Content-Length']
        body = self.rfile.read(int(length)).decode('utf-8')
        parsed_body = parse_qs(body)

        name = parsed_body['name'][0]
        rank = parsed_body['rank'][0]
        station = parsed_body['station'][0]
        ship = parsed_body['ship'][0]
        species = parsed_body['species'][0]

        db = OfficerDB()
        db.insertOfficer(name, rank, station, ship, species)

        self.send_response(201)
        self.end_headers()
    
    def handleDeleteMember(self, oID):
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            return
        
        db = OfficerDB()
        db.deleteOfficer(oID)

        self.send_response(200)
        self.end_headers()

    def handleUpdateMember(self, oID):
        if "userID" not in self.sessionData:
            self.send_response(401)
            self.end_headers()
            return

        length = self.headers['Content-Length']
        body = self.rfile.read(int(length)).decode('utf-8')
        parsed_body = parse_qs(body)

        name = parsed_body['name'][0]
        rank = parsed_body['rank'][0]
        station = parsed_body['station'][0]
        ship = parsed_body['ship'][0]
        species = parsed_body['species'][0]

        db = OfficerDB()
        db.updateOfficer(name, rank, station, ship, species, oID)

        self.send_response(200)
        self.end_headers()
    
    def handleUserCreate(self):
        #get data from body
        #check to see if user exists
        #create user if not exists
        #if user exists send error
        #error code 422

        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode('utf-8')
        pBody = parse_qs(body)

        fName = pBody['fName'][0]
        lName = pBody['lName'][0]
        email = pBody['email'][0]
        password = pBody['pass'][0]

        db = OfficerDB()
        user = db.getUserEmail(email)

        if user == None:
            hashed_password = bcrypt.hash(password)

            db = OfficerDB()
            db.registerUser(fName, lName, email, hashed_password)

            user = db.getUserEmail(email)

            self.send_response(201)
            self.end_headers()
            
        else:
            self.send_response(422)
            self.end_headers()

    def handleSessionCreate(self):
        #read email and pass from body
        #First check to see if email exists in database
        #user = db.getOneUserByEmail()
        #If exists:
            #use bcrypt.verify() to check given password against db password
            #if password matches:
                #201
            #else:
                #401
        #else:
            #401
        
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode('utf-8')

        pBody = parse_qs(body)
        email = pBody['email'][0]
        userPass = pBody['password'][0]

        db = OfficerDB()
        user = db.getUserEmail(email)
        print(user)
        # name = "{0}, {1}".format(user['lName'].upper(), user['fName'].upper())

        if user != None:
            if bcrypt.verify(userPass, user['pass']):
                self.sessionData['userID'] = user['id']
                self.send_response(201)
                self.end_headers()
                # self.wfile.write(bytes(json.dumps(name), 'utf-8'))
            else:
                self.send_response(401)
                self.end_headers()
        else:
            self.send_response(401)
            self.end_headers()

    def do_OPTIONS(self):
        self.load_session_data()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Accept, Content-Type, Origin")
        self.end_headers()
    
    def do_GET(self):
        self.load_session_data()
        path_parts = self.path.split('/')
        resource = path_parts[1]
        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None
        
        if resource == 'officers' and identifier == None:
            self.handleRetrieveCollection()
            print(self.sessionData)
        elif resource == 'officers' and identifier != None:
            self.handleRetrieveMember(identifier)
        else:
            self.handleNotFound()
    
    def do_POST(self):
        self.load_session_data()
        if self.path == '/officers':
            self.handleCreate()
        elif self.path == '/users':
            self.handleUserCreate()
        elif self.path =='/sessions':
            self.handleSessionCreate()
        else:
            self.handleNotFound()
    
    def do_DELETE(self):
        self.load_session_data()
        path_parts = self.path.split('/')
        resource = path_parts[1]
        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None
        
        if resource == 'officers' and identifier != None:
            self.handleDeleteMember(identifier)
        else:
            self.handleNotFound()
    
    def do_PUT(self):
        self.load_session_data()
        path_parts = self.path.split('/')
        resource = path_parts[1]
        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None

        if resource == 'officers' and identifier != None:
            self.handleUpdateMember(identifier)
        else:
            self.handleNotFound()

def main():
   
    db = OfficerDB()
    db.createOfficersTable()
    db.createUsersTable()
    db = None

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HttpServer(listen, MyReqHandle)
    print("listening on", "{}:{}".format(*listen))
    server.serve_forever()
    

main()
