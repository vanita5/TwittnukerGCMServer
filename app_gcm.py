from __future__ import print_function, division
from threading import Thread
from functools import wraps
import sqlite3 as sql
from gcm import GCM
from app_conf import GCM_API_KEY, DBNAME
from dbsetup import init_db


#init_db(DBNAME)

gcm = GCM(GCM_API_KEY)

def to_dict(row):
    return dict(sha=row['sha'],
                accountid=row['accountid'],
                timestamp=row['timestamp'])

def async(func):
    '''Runs the decorated function in a separate thread.
    Returns the thread.
    '''
    @wraps(func)
    def async_func(*args, **kwargs):
        t = Thread(target = func, args = args, kwargs = kwargs)
        t.start()
        return t

    return async_func

# TODO Send Push Notification

@async
def send_notification(userid, account_id, from_user, message):
    data = dict(account = account_id,
                fromuser = from_user,
                msg = message)
    print("Data:", data)

    db = _get_db()
    
    # Get devices
    regrows = db.execute('SELECT * FROM gcm WHERE userid IS ?', [userid]).fetchall()
    if len(regrows) < 1:
        return

    reg_ids = []
    for row in regrows:
        reg_ids.append(row['regid'])

    if len(reg_ids) < 1:
        return

    print("Sending to:", len(reg_ids))
    _send(userid, reg_ids, data)
    

def _get_db():
    db = sql.connect(DBNAME)
    db.row_factory = sql.Row
    return db


def _remove_regid(userid, regid):
    db = _get_db()
    with db:
        c = db.cursor()
        c.execute('DELETE FROM gcm WHERE userid IS ? AND regid IS ?',
                  [userid, regid])


def _replace_regid(userid, oldid, newid):
    db = _get_db()
    with db:
        c = db.cursor()
        c.execute('UPDATE gcm SET regid=? WHERE userid IS ? AND regid IS ?',
                  [newid, userid, oldid])


def _send(userid, rids, data):
    '''Send the data using GCM'''
    response = gcm.json_request(registration_ids=rids,
                                data=data)
    # A device has switched registration id
    if 'canonical' in response:
        for reg_id, canonical_id in response['canonical'].items():
            # Repace reg_id with canonical_id in your database
            _replace_regid(userid, reg_id, canonical_id)

    # Handling errors
    if 'errors' in response:
        for error, reg_ids in response['errors'].items():
            # Check for errors and act accordingly
            if error is 'NotRegistered':
                # Remove reg_ids from database
                for regid in reg_ids:
                    _remove_regid(userid, regid)



