import pytest
import pandas as pd
from get_station_data import ghcnd
from get_station_data.util import nearest_stn


@pytest.fixture
def notebook_n5_latlon():
    return -0.1278, 51.5074


@pytest.fixture
def notebook_n5_metadata():
    return pd.DataFrame({
        'station': ['UKE00105915', 'UKM00003772', 'UKE00105900', 'UKW00035054', 'UKE00107650'],
        'lat': [51.5608, 51.4780, 51.8067, 51.2833, 51.4789],
        'lon': [0.1789, -0.4610, 0.3581, 0.4000, 0.4489],
        'elev': [137.0, 25.3, 128.0, 91.1, 25.0],
        'name': ['HAMPSTEAD', 'HEATHROW', 'ROTHAMSTED', 'WEST MALLING', 'HEATHROW']
    })


@pytest.fixture
def stn_id():
    return "UKE00105915"


@pytest.fixture
def stn_data(stn_id, notebook_n5_metadata):
    sub_md = notebook_n5_metadata[notebook_n5_metadata.station == stn_id]
    return ghcnd.get_data(sub_md)


def test_notebook_nearest_metadata(notebook_n5_latlon, notebook_n5_metadata):
    target, london_lon_lat = notebook_n5_metadata, notebook_n5_latlon
    stn_md = ghcnd.get_stn_metadata()
    my_stns = nearest_stn(stn_md,
                          london_lon_lat[0], london_lon_lat[1],
                          n_neighbours=5).drop(columns=["start_year", "end_year"]).reset_index(drop=True)
    assert target.equals(my_stns)

"""
Maually inspect the value at https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/UKE00105915.dly, row 2 value 1
"""

def test_stn_value_old(stn_data):
    target_val = stn_data[(stn_data.date == pd.to_datetime(
        "1960-01-01")) & (stn_data.element == "TMAX")]["value"].iloc[0]
    assert target_val == 7.8

def test_stn_value_new(stn_data):
    target_val = stn_data[(stn_data.date == pd.to_datetime(
        "2016-07-04")) & (stn_data.element == "TMIN")]["value"].iloc[0]
    assert target_val == 10.4

def test_stn_value_nan(stn_data):
    target_val = stn_data[(stn_data.date == pd.to_datetime(
        "2016-07-26")) & (stn_data.element == "TMAX")]["value"]
    assert target_val.isna().iloc[0]


def test_get_data_range(notebook_n5_metadata):
    date_range = ('2010-01-01', '2023-01-01')
    df = ghcnd.get_data(notebook_n5_metadata, date_range=date_range)
    is_between = df.date.between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))
    assert is_between.all()
     

def test_get_data_flags(notebook_n5_metadata):
    df = ghcnd.get_data(notebook_n5_metadata, include_flags=False)
    assert "qflag" not in df.columns

def test_get_data_element_type(notebook_n5_metadata):
    df = ghcnd.get_data(notebook_n5_metadata, element_types=["TMAX", "TMIN"])
    assert df.element.isin(["TMAX", "TMIN"]).all()