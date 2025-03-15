import requests
import json
from http.client import HTTPConnection
import logging

log = logging.getLogger('urllib3')
log.setLevel(logging.DEBUG)

# logging from urllib3 to console
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

# print statements from `http.client.HTTPConnection` to console/stdout
HTTPConnection.debuglevel = 1

class SynoServer:
    def __init__(self, host):
        self.host = host
        self.session_token = None
        self.session_sid = None
        self.session_did = None
        self.session_account_name = None

        self.client = requests.Session()
        self.client.verify=False
        self.SYNO_API_AUTH = "SYNO.API.Auth"
        request_url = host + "/webapi/entry.cgi?api=SYNO.API.Info&version=1&method=query"
        self.apiInfo = self.client.get(request_url).json()


    def login(self, username, password):
        auth_path = self.apiInfo['data'][self.SYNO_API_AUTH]['path']
        request_url= self.host + "/webapi/" + auth_path

        params={
            "api":self.SYNO_API_AUTH,
            "version":str(7),
            "method":"login",
            "account":username,
            "passwd":password,
            "enable_syno_token":"yes",
            "format":"cookie"
        }

        auth_response = self.client.get(request_url, params=params)

        print(json.dumps(auth_response.json()))
        self.session_token = auth_response.json()['data']['synotoken']
        self.session_sid = auth_response.json()['data']['sid']
        self.session_did = auth_response.json()['data']['device_id']
        self.session_account_name = auth_response.json()['data']['account']
        self.client.headers.update({"X-SYNO-TOKEN":self.session_token})

    def logout(self):
        auth_path = self.apiInfo['data'][self.SYNO_API_AUTH]['path']
        request_url= self.host + "/webapi/" + auth_path + "?version=7&method=logout"
        request_url+="&synotoken=" + self.session_token
        request_url+="&sid="+self.session_sid
        print("LOGOUT REQUEST: " + request_url)
        self.client.get(request_url)


