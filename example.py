'''

Extract variable/element of interest from the
Global Historical Climatology Network Daily (GHCND) Version 3

To run this script you will need to save the ghcnd.py file along side the 
	GHCN-D '.dly' and 'ghcnd-stations.txt' files.

To save as NetCDF using ghcnd.py you will need to have iris and some other 
	libraries installed.

'''

import numpy as np
import iris
import ghcnd

### Name of original daily data file from GHCN-D
### e.g., ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/UKM00003772.dly
filename= 'UKM00003772.dly'

### Extract all data into a labelled numpy array
data = ghcnd.extract_data(filename)

### Filter data for, e.g., desired variable etc
element = 'TMAX'
index = np.where( (data['element'] == element) )[0]
data = data[index]

### save to netcdf file
stn_id = np.unique(data['station'])[0]
lat, lon, stn_elev, name = ghcnd.get_metadata('ghcnd-stations.txt', stn_id)
cube = ghcnd.create_cube(data, stn_id, lat, lon, stn_elev, name)

cube.data = cube.data / 10.
cube.units = 'degrees_c'

iris.save(cube, 'NetCDFs/'+stn_id+'_'+'_'.join(name.split())+'.nc')
print('\nNote: These netcdf files may be considerably larger than the input data, '+
 	 'therefore it may be appropriate to recreate them as-and-when you need them if disk space is an issue.')