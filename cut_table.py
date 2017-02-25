#!/usr/bin/env python

from astropy.table import Table
import pandas as pd
import glob

def cut_table(tpath):
    t = Table.read(tpath)
    df = t.to_pandas()
    df_cut = df_cut = df.filter(regex="^ra$|^dec$|f475w_vega|f814w_vega|f475w_gst|f814w_gst")
    df_cut2 = df_cut[df_cut.filter(regex='gst').sum(axis=1)==2]
    df_cut2 = df_cut2.drop(df_cut.filter(regex='gst'), axis=1)
    df_cut2.to_hdf(tpath.replace('.fits','.hdf5'), key='data', mode='w', complevel=9, complib='zlib')

if __name__ == '__main__':
    for i in glob.glob('hlsp/hlsp*.fits'):
        cut_table(i)