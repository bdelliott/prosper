import ConfigParser
import json
import os

import requests


class Prosper(object):

    def __init__(self, sandbox=False):
        self._base = self._baseurl(sandbox)
        self._creds(sandbox)
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
        else:
            return "https://api.prosper.com/v1/"

    def _creds(self, sandbox):
        cfg = ConfigParser.RawConfigParser()

        if sandbox:
            section = 'api_sandbox'
        else:
            section = 'api'

        creds_path = os.path.join(os.environ['HOME'], '.prosper.cfg')
        cfg.read([creds_path])

        self._client_id = cfg.get(section, 'client_id')
        self._client_secret = cfg.get(section, 'client_secret')
        self._username = cfg.get(section, 'username')
        self._password = cfg.get(section, 'password')

    def _get(self, path, **params):
        url = self._base + path

        r = self._request(requests.get, url, params=params)
        if r.status_code != 200:
            raise Exception("GET failed with code %d, text %s" %
                            (r.status_code, r.text))

        return json.loads(r.text)

    def _request(self, request_fn, url, params=None):
        auth = "%s %s" % (self._token_type, self._token)
        headers = {
            'Authorization': auth,
            'Accept': 'application/json'
        }

        if headers is None:
            headers = {}

        return request_fn(url, headers=headers, params=params)


    def account(self):
        """Retrieve high level account information"""
        return self._get("accounts/prosper")

    def notes(self):
        """Retrieve information about notes owned

        NOTE - the api defaults to a `limit` of 25 notes in one response.
        NOTE - `limit` also maxes at 25.  doh.
        """

        # just retrieve all the pages.
        notes = []
        offset = 0
        while True:
            #print "retrieving 25, starting form %d" % offset
            resp = self._get("notes/", offset=offset)
            notes.extend(resp['result'])
            total = resp['total_count']
            offset += resp['result_count']

            if offset == total:
                break

        return notes
