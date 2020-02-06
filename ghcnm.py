'''

GHCNM.py makes it easier to work with station data from 
[Global Historical Climatology Network Monthly (GHCNM) 
Version 3](https://www.ncdc.noaa.gov/ghcnm/v3.php).

What can ghcnm.py do?
Extract station data from the GHCN-M dat file and provide the user with 
a labelled Pandas DataFrame with relevent metadata.  This makes it easy 
and fast to filter by station, country, or by years etc


GHCNM README: ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v3/README


ghcnm.py
---------

Author: Dr Scott Hosking (British Antarctic Survey)
Creation Date:   16th August 2016 
      updates:   6th February 2020 (move to v4 of GHCN-monthly data)

'''

import numpy as np
import pandas as pd

### Set value to flag missing data points
missing_id = '-9999'


def get_stn_metadata(meta_fname):

    ### Sanity Checks
    if (meta_fname.endswith('.inv') == False):
        raise ValueError('filename does not look correct')
    version = meta_fname.split('/')[-1].split('.')[2]
    if (version != 'v4'):
        raise ValueError('This filename appears to be for GHCN-M '+version+ \
                                    '. This has only been tested for v4')

    df = pd.read_fwf(meta_fname, colspecs=[(0,2), (0,12), (12,21), (21,31), 
                                                (31,38), (38,69)], 
                        names=['country_codes','station',
                                'lat','lon','elev','name'])

    df['country'] = country_name_from_code(df['country_codes'])

    df = df.drop(columns=['country_codes'])

    return df


def country_name_from_code(country_codes, country_codes_file=None):
    '''
    Convert country-codes to country-names
    https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm-countries.txt
    '''
    if country_codes_file == None:
        country_codes_file = 'ghcnm-countries.txt'
    cc = pd.read_fwf(country_codes_file, widths=[3,45], 
                                                names=['Code','Name'])
    cc = cc.set_index('Code')
    country_names = cc.loc[country_codes,'Name'].values
    return country_names


def get_data(data_fname, my_stns):

    ##############################
    # Sanity Checks
    ##############################
    if (data_fname.endswith('.dat') == False):
        raise ValueError('filename does not look correct')
    version = data_fname.split('/')[-1].split('.')[2]
    if (version != 'v4'):
        raise ValueError('This filename appears to be for GHCN-M '+version+ \
                                    '. This has only been tested for v4')

    ##############################
    # read in whole data file
    ##############################
    colspecs = [(0,2),(0,11),(11,15),(15,19)]      
    names    = ['country_code','station','year','variable']

    i = 19
    for m in range(1,13):

        mon = str(m)
        colspecs_tmp = [(i,i+5),     (i+5,i+6),    (i+6,i+7),    (i+7,i+8)   ]
        names_tmp    = ['VALUE'+mon, 'DMFLAG'+mon, 'QCFLAG'+mon, 'DSFLAG'+mon]

        for j in range(0,4):
            colspecs.append(colspecs_tmp[j]) 
            names.append(names_tmp[j])

        i = i+8

    df = pd.read_fwf(data_fname, colspecs=colspecs, names=names)        

    ##############################
    # filter rows based on my_stns
    ##############################
    df = df[df['station'].isin(my_stns.station.values).values]

    ##############################
    # Add in metadata
    ##############################

    for col in ['lat','lon','elev','name','country']:
        df[col] = '-9999' # to do!!
    
    ##############################
    # Reformat dataframe to create monthly data (each row is a month)
    ############################## 
    df_m = pd.DataFrame(columns=['country_code','station','lat','lon','elev','name','country','variable','year','value','dmflag','qcflag','dsflag'])

    for m in range(1,13):
        df_tmp = df[['country_code','station','lat','lon','elev','name','country',
                        'variable','year','VALUE'+str(m), 'DMFLAG'+str(m), 'QCFLAG'+str(m), 'DSFLAG'+str(m)]]
        df_tmp['date'] = df_tmp['year']*100.+m
        df_tmp = df_tmp.rename(columns={'VALUE'+str(m) :'value' ,
                               'DMFLAG'+str(m):'dmflag',
                               'QCFLAG'+str(m):'qcflag',
                               'DSFLAG'+str(m):'dsflag'
                              })
        df_m = pd.concat( [df_m, df_tmp] )

    df_m = df_m[['country_code','station','variable','lat','lon','elev','name','country','date','value','dmflag','qcflag','dsflag']]
    df_m['date'] = df_m['date'].astype(int)
    df_m = df_m.sort_values(by=['station','date'])        
    
    if 'ghcnm.tavg.' in data_fname:
        df_m['value'] = df_m['value'] / 100.
    
    return df_m