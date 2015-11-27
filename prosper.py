import ConfigParser
import json
import os

import requests


class Prosper(object):

    def __init__(self, sandbox=False):
        self._base = self._baseurl(sandbox)
        self._creds()
        self._auth()

    def _auth(self):
        url = self._base + "security/oauth/token"
        data = dict(
            grant_type='password',
            client_id=self._client_id,
            client_secret=self._client_secret,
            username=self._username,
            password=self._password
        )

        r = requests.post(url, data=data)
        if r.status_code != 200:
            raise Exception("Failed to auth:: status_code=%d, response "
                            "text=%s" % (r.status_code, r.text))
        auth = json.loads(r.text)
        self._token_type = auth['token_type']
        self._token = auth['access_token']

    def _baseurl(self, sandbox):
        if sandbox:
            return "https://api.sandbox.prosper.com/v1/"

    def _creds(self):
        cfg = ConfigParser.RawConfigParser()

        creds_path = os.path.join(os.environ['HOME'], '.prosper.cfg')
        cfg.read([creds_path])

        self._client_id = cfg.get('DEFAULT', 'client_id')
        self._client_secret = cfg.get('DEFAULT', 'client_secret')
        self._username = cfg.get('DEFAULT', 'username')
        self._password = cfg.get('DEFAULT', 'password')

    def _get(self, path):
        url = self._base + path

        r = self._request(requests.get, url)
        if r.status_code != 200:
            raise Exception("GET failed with code %d, text %s" %
                            (r.status_code, r.text))

        return json.loads(r.text)

    def _request(self, request_fn, url):
        auth = "%s %s" % (self._token_type, self._token)
        headers = {
            'Authorization': auth,
            'Accept': 'application/json'
        }

        if headers is None:
            headers = {}

        return request_fn(url, headers=headers)


    def account(self):
        """Retrieve high level account information"""
        resp = self._get("accounts/prosper")
        print "Account info:"
        print resp

    def notes(self):
        """Retrieve information about notes owned"""
        resp = self._get("notes")
        print "Notes:"
        print resp



if __name__ == '__main__':
    prosper = Prosper(sandbox=True)
    prosper.account()
    prosper.notes()
