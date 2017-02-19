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
    recentfile = 'most_recent.txt'
    new_tweet = check_new_tweet(str(status_id), recentfile)

    if new_tweet:
        print('New @AndromedaBot tweet found!')
        txt = most_recent['text'].split(' http')[0]
        wcs = get_wcs('m31avm.xml')
        pix = get_pix(txt)
        coords = get_coords(wcs, *pix)
        bricks = get_brick(*coords)
        print('Bricks {}'.format(bricks))
        if bricks is not None:
            cpath = get_cpath(coords)
            result = None
            while result is None:
                for brick in bricks:
                    try:
                        t = read_table(brick)
                        plotcmd(t, cpath, txt)
                        result = True
                    except Exception:
                        print("Brick {} didn't work. Trying another.".format(brick))
                        if bricks.index(brick) == (len(bricks) - 1):
                            result = False
                            print("Couldn't find photometry. Sorry!")
            if result != False:
                api.PostUpdate('.@AndromedaBot: "{}"'.format(txt),
                    media='cmd.png', in_reply_to_status_id=status_id)
                print('Tweet posted')
                with open(recentfile,'w') as f:
                    f.write(str(status_id))

    else:
        print('No new @AndromedaBot tweets found.')

if __name__ == '__main__':
    run()