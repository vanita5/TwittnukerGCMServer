import os, binascii
from dateutil import parser as dateparser
from bottle import run, get, post, delete, install, HTTPError, request
from bottle_sqlite import SQLitePlugin
from dbsetup import init_db
from google_auth import gauth
from app_conf import DBNAME, DEBUG
from app_gcm import send_notification

init_db(DBNAME)
install(SQLitePlugin(dbfile=DBNAME))

install(gauth)

def prnt(s):
    if DEBUG:
        print s

def settings_to_dict(row):
    resp = dict(accountid = row['accountid'],
                # Convert integer to boolean
                nmentions = (row['nmentions'] == 1),
                ndms = (row['ndms'] == 1),
                nfollower = (row['nfollower'] == 1))

    prnt('Response: ' + str(resp))
    return resp

def account_from_db(db, accountid, userid):
    prnt('\nCreate response...')
    args = [accountid, userid]

    stmt = "SELECT * FROM ACCOUNTS WHERE accountid IS ? AND userid IS ?"

    response = db.execute(stmt, args).fetchone()
    return settings_to_dict(response)

@get('/')
@get('/settings')
def get_settings(db, userid):
    '''Return a list of the settings per twitter account to show in the app'''
    prnt('GET: /settings')
    args = [userid]

    settings = []

    stmt = 'SELECT * FROM accounts WHERE userid IS ?'
    
    for row in db.execute(stmt, args):
        settings.append(settings_to_dict(row))

    prnt('GOT SETTINGS: ' + settings)
    return dict(settings = settings)

@post('/settings')
def set_settings(db, userid):
    '''Set settings in the db and apply them (TODO)'''
    prnt('POST: /settings')
    prnt('Data: ' + str(request.json))
    if 'application/json' not in request.content_type:
        return HTTPError(415, "Only json is accepted")

    # Check required fields
    if ('accountid' not in request.json or request.json['accountid'] is None
        or len(request.json['accountid']) < 1):
        return HTTPError(400, "Must specify an account.")

    if ('nmentions' not in request.json or request.json['nmentions'] is None
        or len(request.json['nmentions']) < 1):
        request.json['nmentions'] = 0

    if ('ndms' not in request.json or request.json['ndms'] is None
        or len(request.json['ndms']) < 1):
        request.json['ndms'] = 0

    if ('nfollower' not in request.json or request.json['nfollower'] is None
        or len(request.json['nfollower']) < 1):
        request.json['nfollower'] = 0

    args = [request.json['nmentions'],
            request.json['ndms'],
            request.json['nfollower'],
            userid,
            request.json['accountid']]
    stmt = 'UPDATE accounts SET nmentions = ?, ndms = ?, nfollower = ? WHERE userid IS ? AND accountid IS ?'

    db.execute(stmt, args)

    if db.total_changes > 0:
        return {}
    else:
        return HTTPError(500, "Updating settings failed!")


@post('/registergcm')
def register_gcm(db, userid):
    '''Adds a registration id for a user to the database.
    Returns nothing.'''
    prnt('POST: /registergcm')
    prnt('Data: ' + str(request.json))
    if 'application/json' not in request.content_type:
        return HTTPError(415, "Request needs to be JSON")

    # Check required fields
    if ('regid' not in request.json or request.json['regid'] is None
        or len(request.json['regid']) < 1):
        return HTTPError(400, "No registration id was given")

    db.execute('INSERT INTO gcm (userid, regid) VALUES(?, ?)',
               [userid, request.json['regid']])

    if db.total_changes > 0:
        return {}
    else:
        return HTTPError(500, "Registration failed!")

@post('/unregistergcm')
def unregister_gcm(db, userid):
    '''Completely removes the user from the notification service'''
    prnt('POST: /unregistergcm')
    prnt('Data: ' + str(request.json))
    if 'application/json' not in request.content_type:
        return HTTPError(415, "Request needs to be JSON")

    # Check required fields
    if ('regid' not in request.json or request.json['regid'] is None
        or len(request.json['regid']) < 1):
        return HTTPError(400, "No registration id was given")

    db.execute('DELETE FROM gcm WHERE userid IS ? AND regid IS ?', [userid, request.json['regid']])
    # TODO Remove user from Twitter stream
    
    if db.total_changes > 0:
        return {}
    else:
        return HTTPError(500, "User does not exist or has already been removed.")

@post('/removeaccount')
def remove_account(db, userid):
    '''Remove a Twitter account from monitoring'''
    prnt('POST: /removeaccount')
    prnt('Data: ' + str(request.json))
    if 'application/json' not in request.content_type:
        return HTTPError(415, "Request needs to be JSON")

    # Check required fields
    if ('accountid' not in request.json or request.json['accountid'] is None
        or len(request.json['accountid']) < 1):
        return HTTPError(400, "No account id was given!")

    args = [userid,
            request.json['accountid']]
    stmt = 'DELETE FROM accounts WHERE userid IS ? AND accountid IS ?'

    db.execute(stmt, args)

    if db.total_changes > 0:
        # TODO remove account from user stream
        return {}
    else:
        return HTTPError(500, "Account could not be romved or has already been removed.")

@post('/addaccount')
def add_account(db, userid):
    '''Adds a Twitter account id to monitor'''
    prnt('POST: /addaccount')
    prnt('Data: ' + str(request.json))
    if 'application/json' not in request.content_type:
        return HTTPError(415, "Request needs to be JSON")

    # Check required fields
    if ('accountid' not in request.json or request.json['accountid'] is None
        or len(request.json['accountid']) < 1):
        return HTTPError(400, "No account id was given!")

    args = [userid,
            request.json['accountid']]
    stmt = 'INSERT INTO accounts (userid, accountid) VALUES(?, ?)'

    db.execute(stmt, args)

    if db.total_changes > 0:
        # TODO add account to user stream
        # TODO Return new Account
        return account_from_db(db, request.json['accountid'], userid)
    else:
        prnt('NO CHANGES ON DB')
        return HTTPError(500, "Account id could not be added to the database.")

if __name__ == '__main__':
    run(host = '0.0.0.0', port = 5050, reloader = True, debug = True)
