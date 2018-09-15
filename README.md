
# GHCND.py

GHCND.py is a set of Python tools to make it easier to work with station data from [Global Historical Climatology Network Daily (GHCND)](https://www.ncdc.noaa.gov/ghcn-daily-description).

Extract variable/element of interest from the
Global Historical Climatology Network Daily (GHCND) Version 3

To run this script you will need to save the ghcnd.py file along side the 
        GHCN-D '.dly' and 'ghcnd-stations.txt' files.


## Example


```python
import numpy as np
import pandas as pd
import ghcnd
```


```python
### Name of original daily data file from GHCN-D
### e.g., ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/UKM00003772.dly
filename = 'CHM00057516.dly'

### Extract all data into a labelled numpy array
df = ghcnd.create_DataFrame('indata/'+filename)

### Filter data for, e.g., desired variable etc
var = 'TMIN'
df = df[ df['element'] == var ]

### Tidy up columns
df = df.rename(index=str, columns={"value": var})
df = df.drop(['element'], axis=1)

### Add metadata
df = ghcnd.add_metadata(df, 'ghcnd-stations.txt')
```

    PRCP values have been divided by ten as specified by readme.txt
    TMAX values have been divided by ten as specified by readme.txt
    TMIN values have been divided by ten as specified by readme.txt



```python
df.head(n=10)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>station</th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>TMIN</th>
      <th>mflag</th>
      <th>qflag</th>
      <th>sflag</th>
      <th>lat</th>
      <th>lon</th>
      <th>elev</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>620</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>1</td>
      <td>6.1</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
    <tr>
      <th>621</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>2</td>
      <td>4.3</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
    <tr>
      <th>622</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>3</td>
      <td>3.0</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
    <tr>
      <th>623</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>4</td>
      <td>8.3</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
    <tr>
      <th>624</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>5</td>
      <td>8.9</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
    <tr>
      <th>625</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>6</td>
      <td>8.4</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
    <tr>
      <th>626</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>7</td>
      <td>7.7</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
    <tr>
      <th>627</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>8</td>
      <td>10.5</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
    <tr>
      <th>628</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>9</td>
      <td>4.0</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
    <tr>
      <th>629</th>
      <td>CHM00057516</td>
      <td>1951</td>
      <td>1</td>
      <td>10</td>
      <td>3.2</td>
      <td></td>
      <td></td>
      <td>s</td>
      <td>29.583</td>
      <td>106.467</td>
      <td>416.0</td>
      <td>CHONGQING</td>
    </tr>
  </tbody>
</table>
</div>




```python
### Save to file
name = '-'.join(np.unique(df['name'].values))
stn  = '-'.join(np.unique(df['station'].values))
df.to_csv(name+'_'+stn+'_'+var+'_GHCN-D.csv', index=False)
```
