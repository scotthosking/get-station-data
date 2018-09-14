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
import pandas as pd

missing_id = '-9999'


def create_DataFrame(filename):

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

	warnings = []

	for line_tmp in lines:

		### return a string of the correct width, left-justified
		line = line_tmp.ljust(linewidth)

		### extract values from original line
		### each new index (i) represents a different month for this 
		### line (i.e., year and station)
		for d in range(0,31):

			stn_id[i]  = line[0:11]
			year[i]    = line[11:15]
			month[i]   = line[15:17]
			day[i]     = d+1
			element[i] = line[17:21]

			### get column positions for daily data
			cols = np.array([21, 26, 27, 28]) + (8*d)
		
			val_tmp  = line[ cols[0]:cols[1] ]

			if val_tmp == missing_id: 
				value[i] = val_tmp
			elif element[i] in ['PRCP', 'TMAX', 'TMIN', 'AWND', 'EVAP', 
								'MDEV', 'MDPR', 'MDTN', 'MDTX', 
								'MNPN', 'MXPN']:
				### these are in tenths of a UNIT
				### (e.g., tenths of degrees C)
				warnings.append(element[i]+\
						' values have been divided by ten' + \
						' as specified by readme.txt')
				value[i] = np.float(val_tmp) / 10.
			else:
				value[i] = np.float(val_tmp)
			
			mflag[i] = line[ cols[1] ]
			qflag[i] = line[ cols[2] ]
			sflag[i] = line[ cols[3] ]

			i = i + 1 ### interate by line and by day

	### Print any warnings
	warnings = np.unique(np.array(warnings))
	for w in warnings: print w

	### Convert to Pandas DataFrame
	df = pd.DataFrame(columns=['station', 'year', 'month', 'day',
								'element', 'value',
								'mflag', 'qflag', 'sflag'])

	df['station'] = stn_id
	df['year']    = year
	df['month']   = month
	df['day']     = day
	df['element'] = element
	df['value']   = value
	df['mflag']   = mflag
	df['qflag']   = qflag
	df['sflag']   = sflag

	df = df.replace(-9999.0, np.nan)

	return df


def add_metadata(df, meta_fname):
	md = pd.read_fwf(meta_fname, colspecs=[(0,12), (12,21), (21,31), 
											(31,38), (38,69)], 
	                    names=['station','lat','lon','elev','name'])
	md = md.set_index('station')
	stn_ids = df['station'].values
	md1 = md.loc[stn_ids, ['lat','lon','elev','name']]
	df['lat']  = md1['lat'].values
	df['lon']  = md1['lon'].values
	df['elev'] = md1['elev'].values
	df['name'] = md1['name'].values
	df = df.replace(-999.0, np.nan)
	return df