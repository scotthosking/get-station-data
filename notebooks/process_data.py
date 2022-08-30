import numpy as np
import pandas as pd
from get_station_data import ghcnm

### Name of original data file from GHCN-M
### ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v3/

### Define version number and data + metadata filenames
data_version = 'v3.3.0.20180404'
data_fname   = 'raw_data/ghcnm.tavg.'+data_version+'.qca.dat'
stn_md_fname = 'raw_data/ghcnm.tavg.'+data_version+'.qca.inv'

### Get metadata data for all weather stations around the globe
stn_md = ghcnm.get_stn_metadata(stn_md_fname)

### Extract metadata for specified countries
country_names = ['UNITED KINGDOM']
my_stns = ghcnm.extract_countries(stn_md, country_names)

### Get all available data for all specified stations 
df = ghcnm.get_data(data_fname, my_stns)

print(np.unique(df['name']))

### Remove unneeded whitespace from station names
df['name'] = [ ' '.join(name.split()) for name in df['name']]

### Add year fraction to df
years         = df['year']
months        = df['month']
year_fraction = df['year'] + (df['month'] / 12.)

### Save to a CSV file
df.to_csv('UK_weather_station_data_ghcnm.csv', index=False)