# Get daily weather station data (Global)

<!-- [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scotthosking/get-station-data/master?filepath=ghcn_monthly_data.ipynb) -->

A set of Python tools to make it easier to extract weather station data (e.g., temperature, precipitation) from the [Global Historical Climatology Network - Daily (GHCND)](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily)

> *"The Global Historical Climatology Network daily (GHCNd) is an integrated database of daily climate summaries from land surface stations across the globe. GHCNd is made up of daily climate records from numerous sources that have been integrated and subjected to a common suite of quality assurance reviews. GHCNd contains records from more than 100,000 stations in 180 countries and territories. NCEI provides numerous daily variables, including maximum and minimum temperature, total daily precipitation, snowfall, and snow depth. About half the stations only report precipitation. Both record length and period of record vary by station and cover intervals ranging from less than a year to more than 175 years."* [source](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily)

More information on the data can be found [here](https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt)

<!-- See Examples:

* [Get daily data](https://scotthosking.com/notebooks/ghcn_daily/)
* [Get monthly data](https://scotthosking.com/notebooks/ghcn_monthly/) -->

## Installation

<!-- 1. **Install the package via [PyPi](https://pypi.org/project/get-station-data/)**: which tends to be the most user-friendly option:

    ```bash
    pip install get-station-data
    ``` -->

1. **Install from the source code**:

* Clone the repository source code:

```bash
git clone https://github.com/scotthosking/get-station-data.git 
```

* Install along with its dependencies:

```bash
cd /path/to/my/get-station-data
pip install -v -e .
```

## Worked through example

```python
from get_station_data import ghcnd
from get_station_data.util import nearest_stn

%matplotlib inline 
```

### Read station metadata

```python
stn_md = ghcnd.get_stn_metadata()
```

### Choose a location (lon/lat) and number of nearest neighbours

```python
london_lon_lat = -0.1278, 51.5074
my_stns = nearest_stn(stn_md, 
                        london_lon_lat[0], london_lon_lat[1], 
                        n_neighbours=5 )
my_stns
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>station</th>
      <th>lat</th>
      <th>lon</th>
      <th>elev</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>52113</th>
      <td>UKE00105915</td>
      <td>51.5608</td>
      <td>0.1789</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
    <tr>
      <th>52165</th>
      <td>UKM00003772</td>
      <td>51.4780</td>
      <td>-0.4610</td>
      <td>25.3</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>52098</th>
      <td>UKE00105900</td>
      <td>51.8067</td>
      <td>0.3581</td>
      <td>128.0</td>
      <td>ROTHAMSTED</td>
    </tr>
    <tr>
      <th>52191</th>
      <td>UKW00035054</td>
      <td>51.2833</td>
      <td>0.4000</td>
      <td>91.1</td>
      <td>WEST MALLING</td>
    </tr>
    <tr>
      <th>52131</th>
      <td>UKE00107650</td>
      <td>51.4789</td>
      <td>0.4489</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
  </tbody>
</table>
</div>



### Download and extract data into a pandas DataFrame


```python
df = ghcnd.get_data(my_stns)

df.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>station</th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>element</th>
      <th>value</th>
      <th>mflag</th>
      <th>qflag</th>
      <th>sflag</th>
      <th>date</th>
      <th>lon</th>
      <th>lat</th>
      <th>elev</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>UKE00105915</td>
      <td>1959</td>
      <td>12</td>
      <td>1</td>
      <td>TMAX</td>
      <td>NaN</td>
      <td></td>
      <td></td>
      <td></td>
      <td>1959-12-01</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
    <tr>
      <th>1</th>
      <td>UKE00105915</td>
      <td>1959</td>
      <td>12</td>
      <td>2</td>
      <td>TMAX</td>
      <td>NaN</td>
      <td></td>
      <td></td>
      <td></td>
      <td>1959-12-02</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
    <tr>
      <th>2</th>
      <td>UKE00105915</td>
      <td>1959</td>
      <td>12</td>
      <td>3</td>
      <td>TMAX</td>
      <td>NaN</td>
      <td></td>
      <td></td>
      <td></td>
      <td>1959-12-03</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
    <tr>
      <th>3</th>
      <td>UKE00105915</td>
      <td>1959</td>
      <td>12</td>
      <td>4</td>
      <td>TMAX</td>
      <td>NaN</td>
      <td></td>
      <td></td>
      <td></td>
      <td>1959-12-04</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
    <tr>
      <th>4</th>
      <td>UKE00105915</td>
      <td>1959</td>
      <td>12</td>
      <td>5</td>
      <td>TMAX</td>
      <td>NaN</td>
      <td></td>
      <td></td>
      <td></td>
      <td>1959-12-05</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
  </tbody>
</table>
</div>



### Filter data for, e.g., a single variable

```python
var = 'PRCP'   # precipitation
df = df[ df['element'] == var ]

### Tidy up columns
df = df.rename(index=str, columns={"value": var})
df = df.drop(['element'], axis=1)

df.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>station</th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>PRCP</th>
      <th>mflag</th>
      <th>qflag</th>
      <th>sflag</th>
      <th>date</th>
      <th>lon</th>
      <th>lat</th>
      <th>elev</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>93</th>
      <td>UKE00105915</td>
      <td>1960</td>
      <td>1</td>
      <td>1</td>
      <td>2.5</td>
      <td></td>
      <td></td>
      <td>E</td>
      <td>1960-01-01</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
    <tr>
      <th>94</th>
      <td>UKE00105915</td>
      <td>1960</td>
      <td>1</td>
      <td>2</td>
      <td>1.5</td>
      <td></td>
      <td></td>
      <td>E</td>
      <td>1960-01-02</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
    <tr>
      <th>95</th>
      <td>UKE00105915</td>
      <td>1960</td>
      <td>1</td>
      <td>3</td>
      <td>1.0</td>
      <td></td>
      <td></td>
      <td>E</td>
      <td>1960-01-03</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
    <tr>
      <th>96</th>
      <td>UKE00105915</td>
      <td>1960</td>
      <td>1</td>
      <td>4</td>
      <td>0.8</td>
      <td></td>
      <td></td>
      <td>E</td>
      <td>1960-01-04</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
    <tr>
      <th>97</th>
      <td>UKE00105915</td>
      <td>1960</td>
      <td>1</td>
      <td>5</td>
      <td>0.0</td>
      <td></td>
      <td></td>
      <td>E</td>
      <td>1960-01-05</td>
      <td>0.1789</td>
      <td>51.5608</td>
      <td>137.0</td>
      <td>HAMPSTEAD</td>
    </tr>
  </tbody>
</table>
</div>




```python
df.drop(columns=['mflag','qflag','sflag']).tail(n=10)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>station</th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>PRCP</th>
      <th>date</th>
      <th>lon</th>
      <th>lat</th>
      <th>elev</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>83938</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>22</td>
      <td>0.0</td>
      <td>2016-12-22</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>83939</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>23</td>
      <td>1.4</td>
      <td>2016-12-23</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>83940</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>24</td>
      <td>0.0</td>
      <td>2016-12-24</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>83941</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>25</td>
      <td>1.0</td>
      <td>2016-12-25</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>83942</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>26</td>
      <td>0.0</td>
      <td>2016-12-26</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>83943</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>27</td>
      <td>0.0</td>
      <td>2016-12-27</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>83944</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>28</td>
      <td>0.2</td>
      <td>2016-12-28</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>83945</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>29</td>
      <td>0.4</td>
      <td>2016-12-29</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>83946</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>30</td>
      <td>0.0</td>
      <td>2016-12-30</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
    <tr>
      <th>83947</th>
      <td>UKE00107650</td>
      <td>2016</td>
      <td>12</td>
      <td>31</td>
      <td>0.4</td>
      <td>2016-12-31</td>
      <td>0.4489</td>
      <td>51.4789</td>
      <td>25.0</td>
      <td>HEATHROW</td>
    </tr>
  </tbody>
</table>
</div>



### Save to file

```python
df.to_csv('London_5stns_GHCN-D.csv', index=False)
```

### Plot histogram of all data

```python
df['PRCP'].plot.hist(bins=40)
```
    <matplotlib.axes._subplots.AxesSubplot at 0x11ae36898>

![png](http://scotthosking.com/images/notebooks/ghcn_daily_data/output_14_1.png)


### Plot time series for one station

```python
heathrow = df[ df['name'] == 'HEATHROW' ]
heathrow['PRCP'].plot()
```

    <matplotlib.axes._subplots.AxesSubplot at 0x81f0d7240>

![png](http://scotthosking.com/images/notebooks/ghcn_daily_data/output_16_1.png)

