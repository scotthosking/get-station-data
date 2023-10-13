"""

Extract, process and save data from the
Global Historical Climatology Network Daily (GHCND) Version 3.22

GHCND README: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt


ghcnd.py
---------

Author: Dr Scott Hosking (British Antarctic Survey)
Date:   28th February 2017

Updated: 29th August 2022 - add new data source root location (https://www.ncei.noaa.gov/)
"""
from __future__ import annotations

from joblib import Memory

memory = Memory(".datacache", verbose=0)

import multiprocessing
import os
from datetime import datetime
from functools import partial
from typing import List, Optional

import datetime
import warnings

import numpy as np
import pandas as pd
import tqdm

# These data fields need to be divided by 10
DIV10_ELEMENT_TYPES = [
    "PRCP",
    "TMAX",
    "TMIN",
    "AWND",
    "EVAP",
    "MDEV",
    "MDPR",
    "MDTN",
    "MDTX",
    "MNPN",
    "MXPN",
]

STATION_DATA_COLS = [
    "station",
    "element",
    "value",
    "date",
    "lon",
    "lat",
    "elev",
    "name",
]

FLAG_COLS = ["qflag", "mflag", "sflag"]


def process_stn(
    stn_id, stn_md, include_flags=True, element_types=None, date_range=None
):
    stn_md1 = stn_md[stn_md["station"] == stn_id]
    lat = stn_md1["lat"].values[0]
    lon = stn_md1["lon"].values[0]
    elev = stn_md1["elev"].values[0]
    name = stn_md1["name"].values[0]

    # if the requested range and the stations range as provided in the metadata don't overlap
    # return and empty df and don't download/read file

    if date_range:
        start_year = int(date_range[0][:4])
        end_year = int(date_range[0][:4])
        if (end_year < stn_md1["start_year"].values[0]) or (start_year > stn_md1["end_year"].values[0]):
            df = pd.DataFrame(
                columns=STATION_DATA_COLS + [] if not include_flags else FLAG_COLS
            )
            return df
    
    filename = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/" + stn_id + ".dly"
    df = _create_DataFrame_1stn(filename, include_flags, element_types, date_range)

    if len(pd.unique(df["station"])) == 1:
        df["lon"] = lon
        df["lat"] = lat
        df["elev"] = elev
        df["name"] = name
    # handle empty dfs created by filtering element types
    elif len(pd.unique(df["station"])) == 0:
        df["lon"] = []
        df["lat"] = []
        df["elev"] = []
        df["name"] = []
    else:
        raise ValueError("more than one station ID in file")

    return df


@memory.cache
def get_data(
    my_stns: pd.DataFrame,
    include_flags: bool = True,
    element_types: Optional[List[str]] = None,
    date_range: Optional[Tuple[str, str]] = None,  
) -> pd.DataFrame:
    """
    Fetches GHCND data.

    Args:
        my_stns (pd.DataFrame): Contains metadata for stations to fetch, with columns station, lat, lon, elev, name
        include_flags (bool, optional): If true includes flags which give information about data collection.
                                        False gives significant (5x) speedup.
                                        See https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt for details.
                                        Defaults to True.
        element_types (Optional[List[str]], optional): Only fetches element types in list, if None, fetches all.
                                                      Defaults to None.
        date_range (Optional[Tuple[str, str]], optional): Specifies the date range for data retrieval.
            If provided, only data within the specified range (inclusive) will be fetched.
            Format: (start_date, end_date), where both dates are in 'YYYY-MM-DD' format.
            Defaults to None.

    Returns:
        pd.DataFrame: Station data.
    """
    print("Downloading station data...")
    if date_range:
        try:
            datetime.date.fromisoformat(date_range[0])
            datetime.date.fromisoformat(date_range[1])
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")

        assert pd.Timestamp(date_range[0]) <= pd.Timestamp(date_range[1]), "Start date must be earlier than end date."
    stn_md = get_stn_metadata()

    num_processes = multiprocessing.cpu_count()

    with multiprocessing.Pool(processes=num_processes) as pool:
        partial_process_stn = partial(
            process_stn,
            stn_md=stn_md,
            include_flags=include_flags,
            element_types=element_types,
            date_range=date_range,
        )
        dfs = list(
            tqdm.tqdm(
                pool.imap(partial_process_stn, pd.unique(my_stns["station"])),
                total=len(my_stns),
            )
        )

    empty_dfs = sum([1 for df in dfs if len(df) == 0])

    if empty_dfs > 0:
        warnings.warn(f"{empty_dfs} stations had no data, caused by not recording the requested element type or date range.")

    df = pd.concat(dfs)
    return df


def _create_DataFrame_1stn(
    filename, include_flags, element_types, date_range=None, verbose=False
):
    raw_array = pd.Series(np.genfromtxt(filename, delimiter="\n", dtype="str"))

    out_dict = {}
    out_dict["station"] = raw_array.str[0:11]
    out_dict["year"] = raw_array.str[11:15].astype(int)
    out_dict["month"] = raw_array.str[15:17].astype(int)
    out_dict["element"] = raw_array.str[17:21]

    dfs = []

    if include_flags:
        names = ["value", "mflag", "qflag", "sflag"]
    else:
        names = ["value"]
    for i, n in enumerate(names):
        sub_dict = {}
        for d in range(31):
            idx = np.array([21, 26, 27, 28]) + (8 * d)
            if n == "value":
                out_dict[d] = (
                    raw_array.str[idx[0] : idx[1]]
                    .replace("-9999", np.nan)
                    .replace("", np.nan)
                    .astype(float)
                )
            else:
                out_dict[d] = raw_array.str[idx[i]]

        df = pd.melt(
            pd.DataFrame({**out_dict, **sub_dict}),
            ["station", "year", "month", "element"],
            value_vars=list(range(31)),
            var_name="day",
            value_name=n,
        )

        dfs.append(df)

    out_df = dfs[0]
    if include_flags:
        for i in range(1, 4):
            n = names[i]
            out_df[n] = dfs[i][n]

    out_df["day"] = out_df.day.astype(int) + 1
    out_df["date"] = pd.to_datetime(out_df[["year", "month", "day"]], errors="coerce")
    out_df.loc[
        out_df.element.isin(DIV10_ELEMENT_TYPES),
        "value",
    ] /= 10
    out_df = (
        out_df.dropna(subset="date")
        .drop(columns=["year", "month", "day"])
        .sort_values(by=["station", "date", "element"])
        .reset_index(drop=True)
    )

    if include_flags:
        out_df = out_df.fillna({"qflag": " ", "mflag": " ", "sflag": " "})

    if date_range is not None:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(
            date_range[1]
        )
        out_df = out_df[(out_df["date"] >= start_date) & (out_df["date"] <= end_date)]

    if element_types is None:
        return out_df
    else:
        return out_df.query("element.isin(@element_types)")


@memory.cache
def get_stn_metadata(fname=None, inv_fname=None):
    # Print dowloading metadata
    url_md = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
    url_inv = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt"

    if fname == None:
        inv_fname = url_inv
    print("Downloading inventory metadata...")
    inv = (
        pd.read_fwf(
            inv_fname,
            colspecs=[(0, 12), (35, 41), (41, 46)],
            names=["station", "start_year", "end_year"],
        )
        .groupby(by="station")
        .first()
    )

    inv["start_year"] = inv.start_year.astype(int)
    inv["end_year"] = inv.end_year.astype(int)

    if fname == None:
        fname = url_md

    print("Downloading station metadata...")
    md = pd.read_fwf(
        fname,
        colspecs=[(0, 12), (12, 21), (21, 31), (31, 38), (38, 69)],
        names=["station", "lat", "lon", "elev", "name"],
    )

    return md.join(inv, on="station", how="left")
