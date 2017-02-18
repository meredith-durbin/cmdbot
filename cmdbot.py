from __future__ import division, print_function

import glob
import numpy as np
import twitter
import cfg

from cmdbotlib import check_new_tweet
from cmdbotlib import get_wcs, get_pix, get_coords, get_brick, get_cpath
from cmdbotlib import read_table, plotcmd

def run():
    api = twitter.Api(consumer_key        = cfg.CONSUMER_KEY,
                      consumer_secret     = cfg.CONSUMER_SECRET,
                      access_token_key    = cfg.ACCESS_TOKEN,
                      access_token_secret = cfg.ACCESS_TOKEN_SECRET)

    statuses = api.GetUserTimeline(user_id=2990633947, screen_name='AndromedaBot')
    most_recent = statuses[0].AsDict()
    status_id = str(most_recent[u'id'])
    new_tweet = check_new_tweet(status_id)

    if new_tweet:
        txt = most_recent['text']
        wcs = get_wcs('m31avm.xml')
        pix = get_pix(txt)
        coords = get_coords(wcs, *pix)
        brick = get_brick(*coords)
        print('Brick {}'.format(brick))
        cpath = get_cpath(coords)
        t = read_table(brick)
        print('Stars in full table: {}'.format(len(t)))
        plotcmd(t, cpath)

if __name__ == '__main__':
    run()