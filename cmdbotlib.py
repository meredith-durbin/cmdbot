from __future__ import division
import matplotlib
matplotlib.use('agg')
import matplotlib.path as mplPath
import matplotlib.pyplot as plt
import glob
import numpy as np
import os
from astroML.plotting import scatter_contour
from astropy.table import Table
from pyavm import AVM
from aesthetics import aestheticize

def check_new_tweet(status_id, recentfile='most_recent.txt'):
    if os.path.exists(recentfile):
        with open(recentfile) as f:
            prev_id = f.read()
        if status_id == prev_id:
            new_tweet = False
        elif status_id != prev_id:
            new_tweet = True
            with open(recentfile,'w') as f:
                f.write(status_id)
    else:
        new_tweet = True
        with open(recentfile,'w') as f:
            f.write(status_id)
    return new_tweet

def get_wcs(avmfile):
    avm = AVM.from_xml_file(avmfile)
    wcs = avm.to_wcs()
    return wcs

def get_pix(pxstr):
    c1 = pxstr.split(': ')[1].split('. ')
    xc,yc = map(float, c1[0].split(','))
    w,h = map(float, [c1[1].split('x')[0], c1[1].split('x')[1][:-1]])
    return xc, yc, w, h

def get_coords(wcs, xc, yc, w, h):
    rac,decc = wcs.all_pix2world(xc,yc,0)
    ra0,dec0 = wcs.all_pix2world(xc-w/2,yc-w/2,0)
    ra1,dec1 = wcs.all_pix2world(xc-w/2,yc+w/2,0)
    ra2,dec2 = wcs.all_pix2world(xc+w/2,yc+w/2,0)
    ra3,dec3 = wcs.all_pix2world(xc+w/2,yc-w/2,0)
    ra = np.hstack([ra0,ra1,ra2,ra3,ra0])
    dec = np.hstack([dec0,dec1,dec2,dec3,dec0])
    return ra, dec, rac, decc

def get_brick(ra,dec,rac,decc):
    inside = []
    for i in glob.glob('footprints/F160W_*_footprint.txt'):
        fp = np.loadtxt(i,unpack=True)
        path = mplPath.Path(fp.T)
        radec = np.asarray([ra,dec]).T
        inside.append([i] + list(path.contains_points(radec)))
    inside = np.array(inside)
    where = np.where(inside == 'True')[0]
    ndict = {'2':[],'3':[],'4':[],'5':[]}
    for i in np.unique(where):
        brick = inside[i,0].split('_')[1]
        for j in range(2, 6):
            if list(where).count(i) == j:
                ndict[str(j)].append(brick)
    brick = None
    for i in range(2, 6):
        n = str(7-i)
        if len(ndict[n]) > 0:
            brick = ndict[n][0]
            break
    return brick

def get_cpath(coords):
    cpath = mplPath.Path(np.array([coords[0],coords[1]]).T)
    return cpath

def read_table(brick):
    tablestr = 'hlsp/hlsp_phat_hst_wfc3-uvis-acs-wfc-wfc3-ir_?????-m31'
    tablestr += '-b{}_f275w-f336w-f475w-f814w-f110w-f160w_v2_st.fits'.format(brick)
    table = glob.glob(tablestr)[0]
    t = Table.read(table)
    return t

def plotcmd(t, cpath, blue='f475w', red='f814w', y='f814w'):
    aestheticize()
    f1 = blue.lower() + '_vega'
    f2 = red.lower() + '_vega'
    f3 = y.lower() + '_vega'
    g1 = blue.lower() + '_gst'
    g2 = red.lower() + '_gst'
    inpath = cpath.contains_points(np.array([t['ra'],t['dec']]).astype(float).T)
    if not (True in inpath):
        raise Exception('Nothing found in image region.')
    t_cut = t[inpath & t[g1] & t[g2] & (t[f1] < 99) & (t[f2] < 99)]
    if len(t_cut) == 0:
        raise Exception('Empty table.')
    fig, ax = plt.subplots(1,1,figsize=(6,4))
    ax.plot(t_cut[f1]-t_cut[f2],t_cut[f3],'k.',ms=4, alpha=0.)
    xl = ax.get_xlim()
    yl = ax.get_ylim()
    sc = scatter_contour(t_cut[f1]-t_cut[f2], t_cut[f3],
                         ax = ax, threshold=100, log_counts=False,
                         plot_args={'color':'k', 'alpha':0.2},
                         histogram2d_args={'bins':40},
                         contour_args={'cmap':'viridis'})
    levels = sc[-1].levels
    labels = ['{:.0f}'.format(l) for l in levels]
    cb = fig.colorbar(sc[-1], label='Star density')
    cb.set_ticklabels(labels)
    ax.set_xlim(xl)
    ax.set_ylim(yl)
    ax.invert_yaxis()
    ax.set_xlabel('{} - {}'.format(blue.upper(), red.upper()))
    ax.set_ylabel('{}'.format(y.upper()))
    fig.tight_layout()
    fig.set_dpi(144)
    fig.savefig('cmd.png', dpi=144)
