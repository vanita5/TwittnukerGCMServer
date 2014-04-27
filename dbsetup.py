import sqlite3 as sql
import sys
from app_conf import DBNAME, DEBUG

def prnt(s):
    if DEBUG:
        print s

_CREATE_GCM_TABLE = \
'''CREATE TABLE IF NOT EXISTS gcm
  (_id INTEGER PRIMARY KEY,
  userid TEXT NOT NULL,
  regid TEXT NOT NULL,

  UNIQUE(userid, regid) ON CONFLICT REPLACE)
'''

_CREATE_TABLE = \
'''CREATE TABLE IF NOT EXISTS accounts
  (_id INTEGER PRIMARY KEY,
  userid TEXT NOT NULL,
  accountid TEXT NOT NULL,
  nmentions INTEGER NOT NULL DEFAULT 0,
  ndms INTEGER NOT NULL DEFAULT 0,
  nfollower INTEGER NOT NULL DEFAULT 0,
  
  UNIQUE(userid, accountid) ON CONFLICT REPLACE)
'''

def init_db(filename=DBNAME):
    prnt('INIT DATABSE...')
    con = sql.connect(filename)
    con.row_factory = sql.Row
    with con:
        cur = con.cursor()
        cur.execute(_CREATE_TABLE)
        cur.execute(_CREATE_GCM_TABLE)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        init_db(sys.argv[1])
    else:
        init_db()

