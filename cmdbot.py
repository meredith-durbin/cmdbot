#!/usr/bin/env python

import numpy as np
from twitter import Twitter, OAuth
import auth

from cmdbotlib import check_new_tweet
from cmdbotlib import get_wcs, get_pix, get_coords, get_cpath
from cmdbotlib import plotcmd

def run():
    oauth = OAuth(auth.ACCESS_TOKEN, auth.ACCESS_TOKEN_SECRET,
                  auth.CONSUMER_KEY, auth.CONSUMER_SECRET)
    api = Twitter(auth=oauth)

    statuses = api.statuses.user_timeline(user_id=2990633947, screen_name='AndromedaBot')
    most_recent = statuses[0]
    print('Most recent tweet: {}'.format(most_recent[u'created_at']))
    status_id = most_recent[u'id']
    recentfile = 'most_recent.txt'
    new_tweet = check_new_tweet(str(status_id), recentfile)

    if new_tweet:
        print('New @AndromedaBot tweet found!')
        txt = most_recent['text'].split(' http')[0]
        wcs = get_wcs('wcs.head')
        pix = get_pix(txt)
        coords = get_coords(wcs, *pix)
        cpath = get_cpath(coords)
        result = False
        try:
            plotcmd(cpath, txt, blue='f475w', red='f814w', y='f814w')
            result = True
        except Exception:
            print("Something borked. Sorry!")
        if result:
            with open("cmd.png", "rb") as imagefile:
                imagedata = imagefile.read()
            t_upload = Twitter(domain='upload.twitter.com', auth=oauth)
            img_id = t_upload.media.upload(media=imagedata)["media_id_string"]
            api.statuses.update(status='.@AndromedaBot: "{}"'.format(txt),
                media_ids=img_id, in_reply_to_status_id=status_id)
            print('Tweet posted')
            with open(recentfile,'w') as f:
                f.write(str(status_id))

    else:
        print('No new @AndromedaBot tweets found.')
        exit()

if __name__ == '__main__':
    run()