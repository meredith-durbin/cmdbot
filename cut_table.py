#!/usr/bin/env python

from astropy.table import Table
import pandas as pd
import glob
import os

def cut_table(tpath):
    t = Table.read(tpath)
    df = t.to_pandas()
    df_cut = df_cut = df.filter(regex="^ra$|^dec$|f475w_vega|f814w_vega|f475w_gst|f814w_gst")
    df_cut2 = df_cut[(df_cut.filter(regex='gst').sum(axis=1)==2)]
    df_cut2 = df_cut2.drop(df_cut.filter(regex='gst'), axis=1)
    df_cut2.to_hdf(tpath.replace('.fits','.hdf5'), key='data', mode='w', complevel=9, complib='zlib')

def combine_tables(dflist):
    df0 = pd.read_hdf(dflist[0], key='data')
    for i in dflist[1:]:
        df1 = pd.read_hdf(i, key='data')
        df0 = pd.concat([df0, df1], ignore_index=True)
    df0 = df0[(df0.f475w_vega < 99) & (df0.f814w_vega < 99)]
    df0.to_hdf('hlsp/gst.hdf5', mode='w', key='data', complevel=9, complib='zlib')

if __name__ == '__main__':
    for i in glob.glob('hlsp/hlsp*.fits'):
        hdfpath = i.replace('.fits','.hdf5')
        if not os.path.exists(hdfpath):
            cut_table(i)
            print('Made table {}'.format(i))
    dflist = glob.glob('hlsp/hlsp*.hdf5')
    combine_tables(dflist)
    print('Finished combining tables.')
    exit()
