#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Twittnuker GCM Push Server
#
#
#    @author: vanita5
#    @website: http://vanita5.de/twittnuker/push
#    @mail: twittnuker@vanita5.de
#
##################################################

import tweepy
import KEYS
from app_gcm import *
import logging
import sqlite3 as sql
from app_conf import DBNAME

DEBUG = True

def prnt(string):
    if DEBUG:
        print string

#Logging
logging.basicConfig(filename = 'logfile.log', level=logging.INFO)
logging.info('Program started')
log = logging.getLogger('module')

#OAuth
prnt('[API]:')
try:
    auth = tweepy.OAuthHandler(KEYS.apikey, KEYS.apisecret)
    auth.set_access_token(KEYS.accesstoken, KEYS.accesstokensecret)
    api = tweepy.API(auth)
    ME = api.me()
    prnt('OK\n')
except Exception, e:
    log.exception('Auth')
    print 'Authentication Failed!'
    exit()

def is_mention(status):
    if hasattr(status, 'retweeted_status'):
        return False
    for mention in status.entities['user_mentions']:
        if mention['screen_name'] == ME.screen_name:
            return True
    return False

def is_follower(event):
    return event.event == "follow" and event.target['screen_name'] == ME.screen_name

def is_favorite(event):
    return event.event == "favorite" and event.target['screen_name'] == ME.screen_name
    
def is_retweet(status):
    return hasattr(status, 'retweeted_status') and status.retweeted_status.author.screen_name == ME.screen_name

class StreamListener(tweepy.StreamListener):

    def __init__(self):
        super(StreamListener, self).__init__()
        db = sql.connect(DBNAME)
        db.row_factory = sql.Row

        user = db.execute('SELECT * FROM gcm').fetchone()
        self.userid =user['userid'] #TODO Choose the right user

    def on_status(self, status):
        try:
            if is_mention(status):
                send_notification(self.userid, ME.id, status.author.screen_name, status.text, status.author.profile_image_url, 'type_mention')
            elif is_retweet(status):
                send_notification(self.userid, ME.id, status.author.screen_name, status.retweeted_status.text, status.author.profile_image_url, 'type_retweet')

        except Exception, e:
            log.exception('on_status Error\n')
            pass

    def on_event(self, event):
        try:
            if is_follower(event):
                send_notification(self.userid, ME.id, event.source['screen_name'], '', event.source['profile_image_url'], 'type_new_follower')
            elif is_favorite(event):
                send_notification(self.userid, ME.id, event.source['screen_name'], event.target_object['text'], event.source['profile_image_url'], 
'type_favorite')
            else:
                return True

        except Exception, e:
            log.exception('on_status Error\n')
            pass

    def on_error(self, status_code):
        print str(status_code)
        if status_code == 420:
            print "Sending Notification..."
            send_notification(self.userid, ME.id, '', '', '', 'type_error_420')
        return True

    def on_timeout(self):
        return True

logging.info('Launching Stream...')
streamer = tweepy.Stream(auth, StreamListener(), timeout=60)
streamer.userstream()

logging.info('Stream ended somehow...')
#TODO In this case we could notify the user, that his twitter stream has crashed!
exit()
