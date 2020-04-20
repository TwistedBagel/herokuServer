import os
import base64

class SessionStore:

    def __init__(self):
        self.sessions = {}

    def getSessionData(self, sessionID):
        if sessionID in self.sessions:
            return self.sessions[sessionID]
        else:
            return None
    
    def createSession(self):
        sessionID = self.generateSessionID()
        self.sessions[sessionID] = {}
        return sessionID

    def generateSessionID(self):
        rnum = os.urandom(32)
        rstring = base64.b64encode(rnum).decode('utf-8')
        return rstring