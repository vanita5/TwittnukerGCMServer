from __future__ import print_function
from bottle import request, HTTPError
from httplib2 import Http
from app_conf import DEBUG
import json

def prnt(s):
    if DEBUG:
        print(s)


def validate_token(access_token):
	'''Validates access token
	Returns email address of the user or None'''
	
	h = Http()
	resp, cont = h.request("https://www.googleapis.com/oauth2/v2/userinfo",
				headers = {'Host':'www.googleapis.com',
					   'Authorization':access_token})

	if not resp['status'] == '200':
		return None

	data = json.loads(cont)
        
	return data['email']

def gauth(fn):
	'''Decorator that checks Bottle requests to
	contain an id-token in the request header.
	userid will be None if the
	authentication failed, and have an id otherwise.
	
	Use like so:
	bottle.install(guath)'''

	def _wrap(*args, **kwargs):
		if 'Authorization' not in request.headers:
			return HTTPError(401, 'Unauthorized')

		userid = validate_token(request.headers['Authorization'])
		if userid is None:
                        prnt('UNAUTHORIZED')
			return HTTPError(401, "Unauthorized")
                prnt('VALIDATED: ' + userid)

		return fn(userid=userid, *args, **kwargs)
	return _wrap
