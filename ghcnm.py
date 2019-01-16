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
    if (version != 'v3'):
        raise ValueError('This filename appears to be for GHCN-M '+version+ \
                                    '. This has only been tested for v3')

    df = pd.read_fwf(meta_fname, colspecs=[(0,3), (0,12), (13,21), (21,31), 
                                                (31,38), (38,69)], 
                        names=['country_codes','station',
                                'lat','lon','elev','name'])

    df['country'] = country_name_from_code(df['country_codes'])

    df = df.drop(columns=['country_codes'])

    return df


def country_name_from_code(country_codes, country_codes_file=None):
    ### Convert country-codes to country-names
    if country_codes_file == None:
        url = 'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v3/country-codes'
        country_codes_file = url
    cc = pd.read_fwf(country_codes_file, widths=[4,45], 
                                                names=['Code','Name'])
    cc = cc.set_index('Code')
    country_names = cc.loc[country_codes,'Name'].values
    return country_names


def extract_countries(df, country_names):
    country_names = map(str.upper, country_names)
    df = df.loc[df['country'].isin(country_names)]
    return df


def get_data(data_file, my_stns):

    ### Sanity Checks
    if (data_file.endswith('.dat') == False):
        raise ValueError('filename does not look correct')
    version = data_file.split('/')[-1].split('.')[2]
    if (version != 'v3'):
        raise ValueError('This filename appears to be for GHCN-M '+version+ \
                                    '. This has only been tested for v3')

    ### identify lines to read
    line_stns = pd.read_fwf(data_file, colspecs=[(0,11)], names=['station'])
    line_stns_filtered = line_stns.loc[line_stns['station'].isin(my_stns['station'])]

    ### read all data
    lines = np.genfromtxt(data_file, delimiter='\n', dtype='str')
    lines = lines[line_stns_filtered.index]
    nlines    = len(lines)
    linewidth = lines.dtype.itemsize

    ### initialise arrays
    country_codes = np.zeros( nlines*12 ).astype(int)
    stn_id  = [] # np.chararray(nlines*12, itemsize=11)
    year    = np.zeros( nlines*12 ).astype(int)
    month   = np.zeros( nlines*12 ).astype(int)
    element = [] # np.chararray(nlines*12, itemsize=4)
    value   = np.zeros( nlines*12 )
    dmflag  = [] # np.chararray( nlines*12, itemsize=1)
    qcflag  = [] # np.chararray( nlines*12, itemsize=1)
    dsflag  = [] # np.chararray( nlines*12, itemsize=1)

    ### Loop through all lines in input file
    i = 0 ### start iteration from zero

    for line_tmp in lines:

        ### return a string of the correct width, left-justified
        line = line_tmp.ljust(linewidth)

        ### extract values from original line
        ### each new index (i) represents a different month for 
        ### this line (i.e., year and station)
        for m in range(0,12):

            stn_id.append( line[0:11] )
            country_codes[i] = line[0:3]
            year[i]    = line[11:15]
            month[i]   = m+1
            element.append( line[15:19] )

            ### get column positions for monthly data
            cols = np.array([19,24,25,26]) + (8*m)
        
            val_tmp  = line[ cols[0]:cols[1] ]

            if (val_tmp == missing_id ): 
                value[i] = val_tmp
            else:
                value[i] = np.float(val_tmp) / 100.
            
            dmflag.append( line[ cols[1] ] )
            qcflag.append( line[ cols[2] ] )
            dsflag.append( line[ cols[3] ] )

            i = i + 1 ### interate by line and by month

    stn_id = np.array(stn_id).astype(int)

    ### Convert to Pandas DataFrame
    df = pd.DataFrame()
    df['country']  = stn_id # these will be replaced (see below)
    df['name']     = stn_id #
    df['station']  = stn_id
    df['lat']      = stn_id #
    df['lon']      = stn_id #
    df['elev']     = stn_id #
    df['year']     = year
    df['month']    = month
    df['variable'] = element
    df['value']    = value
    df['dmflag']   = dmflag
    df['qcflag']   = qcflag
    df['dsflag']   = dsflag
    df = df.replace( float(missing_id), np.nan )

    ### add metadata (by replacing temporarily stored station ids)
    for index, row in my_stns.iterrows():
        df = df.replace({'country': row['station']}, row['country'])
        df = df.replace({'name':    row['station']}, row['name']   )
        df = df.replace({'lon':     row['station']}, row['lon']    )
        df = df.replace({'lat':     row['station']}, row['lat']    )
        df = df.replace({'elev':    row['station']}, row['elev']   )

    return df
