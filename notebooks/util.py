import os
import re
import socket

import cftime
import scipy.io as sio
import numpy as np

import pandas as pd

def is_ncar_host():
    """Determine if host is an NCAR machine."""
    hostname = socket.getfqdn()
    
    return any([re.compile(ncar_host).search(hostname) 
                for ncar_host in ['cheyenne', 'casper', 'hobart']])


def track_mat2py(file_track):
    """
    long_name = {'x' : 'longitude',
             'y' : 'latitude',
             'amp' : 'amplitude',
             'area' : 'area',
             'u'    : 'rotational velocity',
             'age'  : 'age',
             'Ls'   : 'feature radius',
             'id'   : 'ID',
             'cyc'  : 'polarity (1:=anticycle, -1:=cyclone)',
             'year' : 'Year',
             'mon'  : 'Month',
             'day'  : 'Day'}
    """
    #-- read .mat
    matdata = sio.loadmat(file_track,
                          struct_as_record = False,
                          squeeze_me = True)
    data = matdata['eddies']

    # u: azimuthal speed   
    fld = ['x', 'y', 'amp', 'area', 'u', 'age', 'Ls', 'id', 'cyc', 'track_day']
    eddy = {}
    for f in fld:
        if any([f == ff for ff in ['id', 'cyc']]) :
            eddy[f] = getattr(data, f).astype(int)

        elif f == 'age':
            eddy[f] = getattr(data, f).astype(float) * 5.

        elif f == 'track_day':
            ymmdd = getattr(data,f).astype(float)
            year = np.round(ymmdd / 1.0e4).astype(int)
            mon = np.round((ymmdd - year * 1.0e4) / 1e2).astype(int)
            day = np.round((ymmdd - year * 1.0e4 - mon * 1e2)).astype(int)
            eddy['year'] = year
            eddy['mon'] = mon
            eddy['day'] = day 
        else:
            eddy[f] = getattr(data, f).astype(float)
            
    return pd.DataFrame(eddy)