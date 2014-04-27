'''Call from a file which requires the stuff as
from app_conf import GCM_API_KEY
from app_conf import DBNAME'''

'''The KEYS file has to be generated!'''
from KEYS import GCM_KEY

DEBUG = True
DBNAME = 'twittnuker_backend.db'
GCM_API_KEY = GCM_KEY
