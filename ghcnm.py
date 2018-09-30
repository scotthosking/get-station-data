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


def create_DataFrame(data_file, country_codes_file=None):

    ### Sanity Checks
    if (data_file.endswith('.dat') == False):
        raise ValueError('filename does not look correct')
    version = data_file.split('/')[-1].split('.')[2]
    if (version != 'v3'):
        raise ValueError('This filename appears to be for GHCN-M '+version+ \
                                    '. This has only been tested for v3')

    ### read all data
    lines = np.genfromtxt(data_file, delimiter='\n', dtype='str')
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

    country_names = country_name_from_code(country_codes, \
                            country_codes_file=country_codes_file)

    ### Default: convert to Pandas DataFrame
    df = pd.DataFrame(columns=['country', 'station', 'year', 
                                'month', 'variable', 'value',
                                'dmflag', 'qcflag', 'dsflag'])
    df['country']  = country_names
    df['station']  = stn_id
    df['year']     = year
    df['month']    = month
    df['variable'] = element
    df['value']    = value
    df['dmflag']   = dmflag
    df['qcflag']   = qcflag
    df['dsflag']   = dsflag
    df = df.replace(-9999.00, np.nan)

    return df


def extract_countries(df, country_names):
    country_names = map(str.upper, country_names)
    df = df.loc[df['country'].isin(country_names)]
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


def add_metadata(df, meta_fname):
    md = pd.read_fwf(meta_fname, colspecs=[(0,12), (13,21), (23,31), 
                                                (31,38), (38,69)], 
                        names=['station','lat','lon','elev','name'])
    md = md.set_index('station')
    stn_ids = df['station'].values.astype(int)
    md1 = md.loc[stn_ids, ['lat','lon','elev']]
    df['lat']  = md1['lat'].values
    df['lon']  = md1['lon'].values
    df['elev'] = md1['elev'].values
    df = df.replace(-999.0, np.nan)
    return df


def create_cube(data, stn_id, lat, lon, stn_elev, name):

    ### using http://scitools.org.uk/iris/
    import iris
    from iris.coords import DimCoord, AuxCoord
    from cf_units import Unit
    from datetime import datetime

    index = np.where( (data['station'] == stn_id) & (data['year'] >= 1900) )[0]

    if len(index) == 0: 
        print("No records >1900, returning None", "Station ID:", stn_id)
        return None

    data = data[index]
    ntimes = len(data)
    years  = data['year']
    months = data['month']

    dt0 = datetime(year=1900, month=1, day=1)
    dt0_str = dt0.strftime('%Y-%m-%d')

    if (len(np.unique(data['element'])) == 1):
        name_str = data['element'][0]

    cube = iris.cube.Cube(np.zeros((ntimes)), long_name=name_str, units="K")
     
    time = np.zeros(ntimes)
    for i in range(0, ntimes):
        dt = datetime(year=years[i], month=months[i], day=1)
        time[i] = (dt - dt0).days

    ### define time dimension
    time_coord = DimCoord(time, "time", units=Unit("days since "+dt0_str, 
                                                calendar='gregorian'))
    cube.add_dim_coord(time_coord, 0)

    ### add lat, lon, elevation as scalar coords
    cube.add_aux_coord(AuxCoord(lat,      long_name='latitude',  
                                                    units='degrees')) 
    cube.add_aux_coord(AuxCoord(lon,      long_name='longitude',
                                                     units='degrees'))
    cube.add_aux_coord(AuxCoord(stn_elev, long_name='elevation',
                                                     units='m'))

    #### add station ID within attributes
    cube.attributes = {
                        'StationID': stn_id,
                        'StationName': '_'.join(name.split())
                        }

    ### insert data into cube
    degreesC  = data['value']
    kelvin    = degreesC
    ind = np.where(degreesC != np.float(missing_id) )[0]
    kelvin[ind] = kelvin[ind] + 273.15
    cube.data = kelvin

    return cube