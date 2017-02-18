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
    status_id = most_recent[u'id']
    new_tweet = check_new_tweet(str(status_id))

    if new_tweet:
        print('New @AndromedaBot tweet found!')
        txt = most_recent['text'].split(' http')[0]
        wcs = get_wcs('m31avm.xml')
        pix = get_pix(txt)
        coords = get_coords(wcs, *pix)
        brick = get_brick(*coords)
        print('Brick {}'.format(brick))
        if brick is not None:
            cpath = get_cpath(coords)
            t = read_table(brick)
            plotcmd(t, cpath, txt)
            api.PostUpdate('.@AndromedaBot: "{}"'.format(txt),
                media='cmd.png', in_reply_to_status_id=status_id)
            print('Tweet posted')
    else:
        print('No new @AndromedaBot tweets found.')

if __name__ == '__main__':
    run()