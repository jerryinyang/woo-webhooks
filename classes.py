class API_Account:
    def __init__(self, name : str, api_key : str, api_secret : str):
        self.name = name
        self.api_key = api_key
        self.api_secret = api_secret

    def getName(self):
        return self.name

    def getKey(self):
        return self.api_key

    def getSecret(self):
        return self.api_secret
    
    def __repr__(self):
        return f"Name: {self.name}, Key: {self.api_key}"

class PayloadRequest:
    def __init__(self, type, url, headers, data, timestamp):
        self.type = type
        self.url = url
        self.headers = headers
        self.data = data
        self.timestamp = timestamp
    
    def getData(self):
        return self.type, self.url, self.headers, self.data

class RequestLog:
    def __init__(self, timestamp, command, response):
        self.timestamp = timestamp
        self.command = command
        self.response = response
    
    def setLog(self, _attr, value):
        if _attr == 'timestamp':
            self.timestamp = value
        elif _attr == 'command':
            self.command = value
        else:
            self.response = value

        return self._age
    
    def getLog(self):
        return {
            'timestamp' : self.timestamp,
            'command' : self.command,
            'response' : self.response
        }