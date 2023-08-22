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
def notebook_n5_data_tail():
    return pd.DataFrame({
        'station': ['UKE00107650', 'UKE00107650', 'UKE00107650', 'UKE00107650', 'UKE00107650'],
        'element': ['TMIN', 'PRCP', 'SNWD', 'TMAX', 'TMIN'],
        'value': [15.0, 0.6, 0.0, float('NaN'), 11.8],
        'mflag': ['', '', '', '', ''],
        'qflag': ['', '', '', '', ''],
        'sflag': ['E', 'E', 'E', '', 'E'],
        'date': ['2023-06-29', '2023-06-30', '2023-06-30', '2023-06-30', '2023-06-30'],
        'lon': [0.4489, 0.4489, 0.4489, 0.4489, 0.4489],
        'lat': [51.4789, 51.4789, 51.4789, 51.4789, 51.4789],
        'elev': [25.0, 25.0, 25.0, 25.0, 25.0],
        'name': ['HEATHROW', 'HEATHROW', 'HEATHROW', 'HEATHROW', 'HEATHROW']
    })


def test_notebook_nearest_metadata(notebook_n5_latlon, notebook_n5_metadata):
    target, london_lon_lat = notebook_n5_metadata, notebook_n5_latlon
    stn_md = ghcnd.get_stn_metadata()
    my_stns = nearest_stn(stn_md,
                          london_lon_lat[0], london_lon_lat[1],
                          n_neighbours=5).drop(columns=["start_year", "end_year"]).reset_index(drop=True)
    assert target.equals(my_stns)


def test_notebook_nearest_data_tail(notebook_n5_metadata, notebook_n5_data_tail):
    df =  ghcnd.get_data(notebook_n5_metadata).reset_index(drop=True).tail()
    assert df.equals(notebook_n5_data_tail)

