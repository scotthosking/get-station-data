'''

Extract variable/element of interest from the
Global Historical Climatology Network Daily (GHCND) Version 3

To run this script you will need to save the ghcnd.py file along side the 
	GHCN-D '.dly' and 'ghcnd-stations.txt' files.

'''

import numpy as np
import pandas as pd
import ghcnd

### Name of original daily data file from GHCN-D
### e.g., ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/UKM00003772.dly
filename = 'CHM00057516.dly'

### Extract all data into a labelled numpy array
df = ghcnd.create_DataFrame('indata/'+filename)
df = df.drop(['mflag', 'qflag', 'sflag'], axis=1)

### Filter data for, e.g., desired variable etc
df = df[ df['element'] == 'TMAX' ]

### Add metadata
df = ghcnd.add_metadata(df, 'ghcnd-stations.txt')

### Save to file
name = '-'.join(np.unique(df['name'].values))
stn  = '-'.join(np.unique(df['station'].values))
df.to_csv(name+'_'+stn+'_GHCND.csv', index=False)