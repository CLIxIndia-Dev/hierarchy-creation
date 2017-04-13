import json
import requests

from copy import deepcopy
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from urllib import quote, unquote

from keys import KEYS

from exceptions import BaseException


class PermissionDenied(BaseException):
    pass


class AssessmentRequests(object):
    """
    Modified requests class that automatically handles the authorization part
    """
    def __init__(self, username='tsl-app@mit.edu', host='dev'):
        if username == '':
            username = 'tsl-app@mit.edu'
        self._pub_key = KEYS[host]['public_key']
        self._pri_key = KEYS[host]['secret_key']
        self._assessments_host = 'localhost:8080'
        if 'host' in KEYS:
            self._assessments_host = KEYS[host]['host']

        self._service = 'https://{0}'.format(self._assessments_host)

        self._sig_headers = ['request-line','Accept','Date','Host','X-Api-Proxy']
        self._headers = {
            'Host'                              : str(self._assessments_host),
            'content-type'                      : str('application/json'),
            'Accept'                            : str('application/json'),
            'X-Api-Key'                         : str(self._pub_key),
            'X-Api-Proxy'                       : str(username)
        }
        # self._auth = HTTPSignatureAuth(key_id=self._pub_key,
        #                                secret=self._pri_key,
        #                                algorithm='hmac-sha256',
        #                                headers=self._sig_headers)
        self.url = self._service

    def _get_now(self):
        return format_date_time(mktime(datetime.now().timetuple()))

    def _is_localhost(self):
        return 'localhost' in self._assessments_host

    def _update_headers(self, headers, url):
        now_headers = deepcopy(headers)
        now_headers['Date'] = self._get_now()
        now_headers['request-line'] = url
        return now_headers

    def delete(self, url):
        if '%40' in url:
            url = unquote(url)
        now_headers = self._update_headers(self._headers, url)

        url = self.url + url

        if url[-1] != '/' and '?' not in url:
            # when no query parameters, add trailing slash
            # url += '/'  # Assessment Service expects a trailing slash
            pass
        elif '?' in url and '/?' not in url:
            # with query parameters, check that there is a slash before the ?
            query_params = url.split('?')[-1]
            url = url.split('?')[0] + '/?' + query_params

        verify = True
        if self._is_localhost():
            verify = False

        req = requests.delete(url, verify=verify)
        if req.status_code in [200, 204]:
            try:
                return req.json()
            except (TypeError, ValueError):
                return req.content
        elif req.status_code == 403:
            raise PermissionDenied('Permission denied.')
        else:
            raise Exception('Request error ' + str(req.status_code) + ': ' + req.content)

    def get(self, url):
        if '%40' in url:
            url = unquote(url)
        now_headers = self._update_headers(self._headers, url)

        url = self.url + url

        if url[-1] != '/' and '?' not in url:
            # when no query parameters, add trailing slash
            # url += '/'  # Assessment Service expects a trailing slash
            pass
        elif '?' in url and '/?' not in url:
            # with query parameters, check that there is a slash before the ?
            # query_params = url.split('?')[-1]
            # url = url.split('?')[0] + '/?' + query_params
            # don't do this for qbank-lite, otherwise it thinks we're adding in
            # an itemId because of the trailing slash
            pass

        verify = True
        if self._is_localhost():
            verify = False

        req = requests.get(url, verify=verify)

        if req.status_code == 200:
            try:
                return req.json()
            except TypeError:
                return req.content
        elif req.status_code == 403:
            raise PermissionDenied('Permission denied.')
        else:
            raise Exception('Request error ' + str(req.status_code) + ': ' + req.content)

    def post(self, url, files=None, data=None, locale='en'):
        if '%40' in url:
            url = unquote(url)
        now_headers = self._update_headers(self._headers, url)

        url = self.url + url

        if files is None and data is None:
            raise TypeError
        verify = True
        if self._is_localhost():
            verify = False

        if data is not None:
            data = json.dumps(data)
            req = requests.post(url, data=data, headers={'content-type': 'application/json',
                                                         'x-api-locale': locale},
                                verify=verify)
        if files is not None:
            req = requests.post(url, files=files, verify=verify)

        if req.status_code in [200, 201]:
            try:
                return req.json()
            except ValueError:
                return req.content
        else:
            raise Exception('Request error ' + str(req.status_code) + ': ' + req.content)

    def put(self, url, files=None, data=None, locale='en'):
        if '%40' in url:
            url = unquote(url)
        now_headers = self._update_headers(self._headers, url)

        url = self.url + url

        if files is None and data is None:
            raise TypeError

        verify = True
        if self._is_localhost():
            verify = False

        if data is not None:
            data = json.dumps(data)
            req = requests.put(url, data=data, headers={'content-type': 'application/json',
                                                        'x-api-locale': locale},
                               verify=verify)
        if files is not None:
            req = requests.put(url, files=files, verify=verify)

        if req.status_code in [200, 201]:
            try:
                return req.json()
            except ValueError:
                return req.content
        else:
            raise Exception('Request error ' + str(req.status_code) + ': ' + req.content)
