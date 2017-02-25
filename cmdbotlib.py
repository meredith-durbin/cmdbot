#!/usr/bin/env python

import matplotlib
matplotlib.use('agg')
import matplotlib.path as mplPath
import matplotlib.pyplot as plt
import glob
import numpy as np
import os
import pandas as pd
from astroML.plotting import scatter_contour
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from aesthetics import aestheticize

def check_new_tweet(status_id, recentfile):
    if os.path.isfile(recentfile):
        with open(recentfile) as f:
            prev_id = f.read()
        if status_id == prev_id:
            new_tweet = False
        elif status_id != prev_id:
            new_tweet = True
    else:
        new_tweet = True
    return new_tweet

def get_wcs(wcsfile):
    with open(wcsfile) as f:
        wcs = WCS(header=f.read())
    return wcs

def get_pix(pxstr, full_height=22230):
    c1 = pxstr.split(': ')[1].split('. ')
    x,y = map(float, c1[0].split(','))
    w,h = map(float, [c1[1].split('x')[0], c1[1].split('x')[1][:-1]])
    return np.array([x, full_height-y, w, h])

def get_coords(wcs, xc, yc, w, h):
    ra0,dec0 = wcs.all_pix2world(xc,yc,0)
    ra1,dec1 = wcs.all_pix2world(xc,yc-h,0)
    ra2,dec2 = wcs.all_pix2world(xc+w,yc-h,0)
    ra3,dec3 = wcs.all_pix2world(xc+w,yc,0)
    ra = np.hstack([ra0,ra1,ra2,ra3,ra0])
    dec = np.hstack([dec0,dec1,dec2,dec3,dec0])
    return ra, dec

def get_cpath(coords):
    cpath = mplPath.Path(np.array([coords[0],coords[1]]).T)
    return cpath

def plotcmd(cpath, txt, blue='f475w', red='f814w', y='f814w'):
    aestheticize()
    df = pd.read_hdf('hlsp/final_cut.hdf5', key='data')
    f1 = blue.lower() + '_vega'
    f2 = red.lower() + '_vega'
    f3 = y.lower() + '_vega'
    inpath = cpath.contains_points(np.array([df['ra'].values, df['dec'].values]).astype(float).T)
    nstars = inpath.sum()
    if nstars == 0:
        raise Exception('Nothing found in image region.')
    print('Number of stars found in region: {}'.format(nstars))
    df_cut = df[inpath]
    if df_cut.shape[0] == 0:
        raise Exception('Empty dataframe.')
    fig, ax = plt.subplots(1, 1, figsize=(6, 4.5))
    ax.plot(df_cut[f1]-df_cut[f2], df_cut[f3], 'k.', ms=4, alpha=0.)
    xl = ax.get_xlim()
    yl = ax.get_ylim()
    sc = scatter_contour(df_cut[f1]-df_cut[f2], df_cut[f3],
                         ax = ax, threshold=100, log_counts=False,
                         plot_args={'color':'k', 'alpha':0.2},
                         histogram2d_args={'bins':40},
                         contour_args={'cmap':'viridis', 'zorder':100})
    levels = sc[-1].levels
    labels = ['Fewer\nstars','More\nstars']
    cb = fig.colorbar(sc[-1])
    cb.set_ticks([levels[0],levels[-1]])
    cb.set_ticklabels(labels)
    ax.set_xlim(xl)
    ax.set_ylim(yl)
    ax.invert_yaxis()
    ax.set_xlabel('{} - {}'.format(blue.upper(), red.upper()))
    ax.set_ylabel('{}'.format(y.upper()))
    title_str = txt.split(': ')[1].split('. ')[0]
    coo = SkyCoord(*cpath.vertices[0], unit='deg')
    coo_str = coo.to_string('hmsdms')
    ax.set_title('{} ({})'.format(title_str, coo_str))
    fig.tight_layout()
    fig.set_dpi(300)
    fig.savefig('cmd.png', dpi=300)
