'''

Extract variable/element of interest from the
Global Historical Climatology Network Daily (GHCND) Version 3

To run this script you will need to save the ghcnd.py file along side the 
	GHCN-D '.dly' and 'ghcnd-stations.txt' files.

'''

import numpy as np
import pandas as pd
import ghcnd

### Choose a station (by name, lon/lat etc)
stn_md = ghcnd.get_stn_metadata('ghcnd-stations.txt')
my_stn = stn_md[ stn_md['name'] == 'CHONGQING' ].iloc[0]

### Name of original daily data file from GHCN-D
### e.g., ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/CHM00057516.dly
filename = my_stn['station']+'.dly' 

### Extract all data into a labelled numpy array
df = ghcnd.create_DataFrame('indata/'+filename)

### Filter data for, e.g., desired variable etc
var = 'TMIN'
df = df[ df['element'] == var ]

### Tidy up columns
df = df.rename(index=str, columns={"value": var})
df = df.drop(['mflag', 'qflag', 'sflag', 'element'], axis=1)

### Add metadata to data file
df = ghcnd.add_metadata(df, stn_md)

### Save to file
name = '-'.join(np.unique(df['name'].values))
stn  = '-'.join(np.unique(df['station'].values))
df.to_csv(name+'_'+stn+'_'+var+'_GHCN-D.csv', index=False)