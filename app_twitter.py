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
    for mention in  status.entities['user_mentions']:
        if mention['screen_name'] == ME.screen_name:
            return True
    return False

class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            if is_mention(status):
                send_notification('eliahwinkler2@gmail.com', ME.id, status.author.screen_name, status.text, 'type_mention')

        except Exception, e:
            log.exception('on_status Error\n')
            pass

    def on_error(self, status_code):
        return True

    def on_timeout(self):
        return True

logging.info('Launching Stream...')
streamer = tweepy.Stream(auth, StreamListener(), timeout=60)
streamer.userstream()

logging.info('Stream ended somehow...')
#TODO In this case we could notify the user, that his twitter stream has crashed!
exit()
