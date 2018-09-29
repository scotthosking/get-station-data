'''

Extract countries of interest (along with their coordinates) from the
Global Historical Climatology Network Monthly (GHCNM) Version 3

To run this script you will need to save the ghcnm.py file along side the 
	GHCN-M '.dat' and '.inv' files.

'''

import numpy as np
import pandas as pd
from get_station_data import ghcnm

### Name of original data file from GHCN-M
### ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v3/
data_fname = 'ghcnm.tavg.v3.3.0.20180404.qca.dat'
meta_fname = data_fname[0:-3]+'inv'

### Extract all data into a labelled numpy array
df = ghcnm.create_DataFrame(data_fname)
df = df.drop(['dmflag', 'qcflag', 'dsflag'], axis=1)

### Select countries to include in output
### ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v3/country-codes
country_names = ['Egypt', 'Libya', 'Sudan', 'ISRAEL', \
                    'SAUDI ARABIA', 'Chad', 'Jordan']
df = ghcnm.extract_countries(df, country_names)
df = ghcnm.add_metadata(df, meta_fname)

df.to_csv('Egypt_surrounding_ghcnm.csv', index=False)