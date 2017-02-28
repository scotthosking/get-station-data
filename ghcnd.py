'''

Extract, process and save data from the
Global Historical Climatology Network Daily (GHCND) Version 3.22

GHCND README: ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt


ghcnd.py
---------

Author: Dr Scott Hosking (British Antarctic Survey)
Date:   28th February 2017

'''

import numpy as np

missing_id = '-9999'



def extract_data(filename):

	### read all data
	lines = np.genfromtxt(filename, delimiter='\n', dtype='str')
	nlines    = len(lines)
	linewidth = lines.dtype.itemsize

	### initialise arrays
	stn_id  = np.chararray(nlines*31, itemsize=11)
	year    = np.zeros( nlines*31 ).astype(int)
	month   = np.zeros( nlines*31 ).astype(int)
	day     = np.zeros( nlines*31 ).astype(int)
	element = np.chararray(nlines*31, itemsize=4)
	value   = np.zeros( nlines*31 )
	mflag   = np.chararray( nlines*31, itemsize=1)
	qflag   = np.chararray( nlines*31, itemsize=1)
	sflag   = np.chararray( nlines*31, itemsize=1)

	### Loop through all lines in input file
	i = 0 ### start iteration from zero

	for line_tmp in lines:

		### return a string of the correct width, left-justified
		line = line_tmp.ljust(linewidth)

		### extract values from original line
		### each new index (i) represents a different month for this line (i.e., year and station)
		for d in range(0,31):

			stn_id[i]  = line[0:11]
			year[i]    = line[11:15]
			month[i]   = line[15:17]
			day[i]     = d+1
			element[i] = line[17:21]

			### get column positions for daily data
			cols = np.array([21, 26, 27, 28]) + (8*d)
		
			val_tmp  = line[ cols[0]:cols[1] ]

			if (val_tmp == missing_id ): 
				value[i] = val_tmp
			else:
				value[i] = np.float(val_tmp)
			
			mflag[i] = line[ cols[1] ]
			qflag[i] = line[ cols[2] ]
			sflag[i] = line[ cols[3] ]

			i = i + 1 ### interate by line and by day

	### convert to numpy array
	dt = np.dtype([ ('station', '|S11'), ('year', 'i'), ('month', 'i'), ('day', 'i'), ('element', '|S4'),
					 ('value', 'd'), ('mflag', '|S1'), ('qflag', '|S1'), ('sflag', '|S1') ])

	array = np.zeros( nlines*31, dt )

	array['station'] = stn_id
	array['year']    = year
	array['month']   = month
	array['day']     = day
	array['element'] = element
	array['value']   = value
	array['mflag']   = mflag
	array['qflag']   = qflag
	array['sflag']   = sflag

	return array


def get_metadata(filename, desired_stn_id):

	lines = np.genfromtxt(filename, delimiter='\n', dtype='str')
	linewidth = lines.dtype.itemsize

	for line in lines:
		### return a string of the correct width, left-justified
		line = line.ljust(linewidth)

		stn_id   = line[0:11]
		lat      = np.float( line[12:20] )
		lon      = np.float( line[21:30] )
		stn_elev = np.float( line[31:37] )
		name     =           line[38:68]

		if stn_id == str(desired_stn_id):
		 	return lat, lon, stn_elev, name




def create_cube(data, stn_id, lat, lon, stn_elev, name):

	### using http://scitools.org.uk/iris/
	import iris
	from iris.coords import DimCoord, AuxCoord
	from cf_units import Unit
	from datetime import datetime

	index = np.where( (data['station'] == stn_id) & (data['year'] >= 1900) )[0]
	data = data[index]
	ntimes = len(data)
	years  = data['year']
	months = data['month']
	days   = data['day']

	dt0 = datetime(year=1900, month=1, day=1)
	dt0_str = dt0.strftime('%Y-%m-%d')

	if (len(np.unique(data['element'])) == 1):
		name_str = data['element'][0]

	time = np.zeros(ntimes)
	keep_ind = np.array([]).astype(int)
	for i in range(0, ntimes):
		if data['value'][i] != np.float(missing_id):
			dt = datetime(year=years[i], month=months[i], day=days[i])
			time[i] = (dt - dt0).days
			keep_ind = np.append(keep_ind, i)

	### remove days that do not exist (e.g., 31st February)
	time = time[keep_ind]
	data = data[keep_ind]

	cube = iris.cube.Cube(np.zeros((len(time))), long_name=name_str, units="1")

	### define time dimension
	time_coord = DimCoord(time, "time", units=Unit("days since "+dt0_str, calendar='gregorian'))
	cube.add_dim_coord(time_coord, 0)

	### add lat, lon, elevation as scalar coords
	cube.add_aux_coord(AuxCoord(lat,      long_name='latitude',   units='degrees')) 
	cube.add_aux_coord(AuxCoord(lon,      long_name='longitude',  units='degrees'))
	cube.add_aux_coord(AuxCoord(stn_elev, long_name='elevation',  units='m'))

	#### add station ID within attributes
	cube.attributes = { 'StationID': stn_id,
						'StationName': '_'.join(name.split())
						}

	### insert data into cube
	cube.data = data['value']

	return cube