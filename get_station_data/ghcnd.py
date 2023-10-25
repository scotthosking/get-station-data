"""

Extract, process and save data from the
Global Historical Climatology Network Daily (GHCND) Version 3.22

GHCND README: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt


ghcnd.py
---------

Author: Dr Scott Hosking (British Antarctic Survey)
Date:   28th February 2017

Updated: 29th August 2022 - add new data source root location (https://www.ncei.noaa.gov/)

Updated: September/October 2023 - speed up downloads and improve robustness (Magnus Ross & Tom Andersson)
"""
from __future__ import annotations

from joblib import Memory

import multiprocessing
import os
import shutil
import urllib.request
from time import sleep
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
    "TAXN",
    "TAVG",
    "TOBS",
    "AWND",
    "EVAP",
    "MDEV",
    "MDPR",
    "MDTN",
    "MDTX",
    "MNPN",
    "MXPN",
    "ADPT",
    "SN*#",
    "SX*#",
    "THIC",
    "WESD",
    "WESF",
    "WSF1",
    "WSF2",
    "WSF5",
    "WSFG",
    "WSFI",
    "WSFM",
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
    stn_id, stn_md, tmp_download_folder, include_flags=True, element_types=None, date_range=None
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

    # Download station data
    local_filename = os.path.join(tmp_download_folder, stn_id + ".dly")
    filename = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/" + stn_id + ".dly"

    backoff(urllib.request.urlretrieve, filename, local_filename)

    df = _create_DataFrame_1stn(local_filename, include_flags, element_types, date_range)

    # Delete temporary local file
    os.remove(local_filename)

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


def get_data(
    stn_md: pd.DataFrame,
    include_flags: bool = True,
    element_types: Optional[List[str]] = None,
    date_range: Optional[Tuple[str, str]] = None,
    num_processes: Optional[int] = None,
    verbose=True,
    cache=False,
    cache_dir=".datacache",
) -> pd.DataFrame:
    """
    Fetches GHCND data.

    Args:
        stn_md (pd.DataFrame):
            Contains metadata for stations to fetch, with columns station, lat, lon, elev, name
        include_flags (bool, optional):
            If true includes flags which give information about data collection.
            False gives significant (5x) speedup. See https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt for details.
            Defaults to True.
        element_types (Optional[List[str]], optional):
            Only fetches element types in list, if None, fetches all.  Defaults to None.
        date_range (Optional[Tuple[str, str]], optional):
            Specifies the date range for data retrieval.  If provided, only data within the specified range (inclusive) will be fetched.
            Format: (start_date, end_date), where both dates are in 'YYYY-MM-DD' format. Defaults to None.
        num_processes (Optional[int], optional):
            Number of CPUs to use for downloading station data in parallel. If not specified, will
            use 75% of all available CPUs.
        verbose (bool):
            Whether to print output. Defaults to True.
        cache (bool):
            Whether to cache output using `joblib.Memory`. If True, function output will be saved
            to disk and returned when the function is called with the same arguments.
            Defaults to False.

    Returns:
        pd.DataFrame: Station data.
    """
    if not cache:
        cache_dir = None
    memory = Memory(cache_dir, verbose=0)

    @memory.cache
    def _get_data(
        stn_md: pd.DataFrame,
        include_flags: bool = True,
        element_types: Optional[List[str]] = None,
        date_range: Optional[Tuple[str, str]] = None,
        num_processes: Optional[int] = None,
        verbose=True,
    ) -> pd.DataFrame:
        if verbose:
            print("Downloading station data...")
        if date_range:
            try:
                datetime.date.fromisoformat(date_range[0])
                datetime.date.fromisoformat(date_range[1])
            except ValueError:
                raise ValueError("Incorrect data format, should be YYYY-MM-DD")

            assert pd.Timestamp(date_range[0]) <= pd.Timestamp(date_range[1]), "Start date must be earlier than end date."

        if num_processes is None:
            # If user hasn't specified num CPUs, use 75% of available CPUs
            num_processes = max(1, int(0.75 * multiprocessing.cpu_count()))
            if verbose:
                print(f"Using {num_processes} CPUs out of {multiprocessing.cpu_count()}... ")

        tmp_download_folder = "tmp_ghcnd"
        os.makedirs(tmp_download_folder, exist_ok=True)

        with multiprocessing.Pool(processes=num_processes) as pool:
            partial_process_stn = partial(
                process_stn,
                stn_md=stn_md,
                tmp_download_folder=tmp_download_folder,
                include_flags=include_flags,
                element_types=element_types,
                date_range=date_range,
            )
            dfs = list(
                tqdm.tqdm(
                    pool.imap(partial_process_stn, pd.unique(stn_md["station"])),
                    total=len(stn_md),
                    smoothing=0,
                    # Add `disable=not verbose,`?
                )
            )

        shutil.rmtree(tmp_download_folder)

        empty_dfs = sum([1 for df in dfs if len(df) == 0])

        if empty_dfs > 0 and verbose:
            warnings.warn(f"{empty_dfs} stations had no data, caused by not recording the requested element type or date range.")

        df = pd.concat(dfs)

        return df

    return _get_data(stn_md, include_flags, element_types, date_range, num_processes, verbose)


def _create_DataFrame_1stn(
    filename, include_flags, element_types, date_range=None,
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
                    .replace("-", np.nan)
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


def get_stn_metadata(fname=None, inv_fname=None, verbose=True, cache=False, cache_dir=".datacache"):
    if not cache:
        cache_dir = None
    memory = Memory(cache_dir, verbose=0)

    @memory.cache
    def _get_stn_metadata(fname=None, inv_fname=None, verbose=True):
        url_md = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
        url_inv = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt"

        if fname == None:
            inv_fname = url_inv
        if verbose:
            print("Downloading inventory metadata...")
        local_filename = "tmp_inv.txt"
        backoff(urllib.request.urlretrieve, inv_fname, local_filename)
        inv = (
            pd.read_fwf(
                local_filename,
                colspecs=[(0, 12), (35, 41), (41, 46)],
                names=["station", "start_year", "end_year"],
            )
            .groupby(by="station")
            .first()
        )
        os.remove(local_filename)

        inv["start_year"] = inv.start_year.astype(int)
        inv["end_year"] = inv.end_year.astype(int)

        if fname == None:
            fname = url_md

        if verbose:
            print("Downloading station metadata...")
        local_filename = "tmp_md.txt"
        backoff(urllib.request.urlretrieve, fname, local_filename)
        md = pd.read_fwf(
            local_filename,
            colspecs=[(0, 12), (12, 21), (21, 31), (31, 38), (38, 69)],
            names=["station", "lat", "lon", "elev", "name"],
        )
        os.remove(local_filename)

        return md.join(inv, on="station", how="left")

    return _get_stn_metadata(fname=fname, inv_fname=inv_fname, verbose=verbose)


def backoff(callable_fn, *args, num_retries=4):
    """
    Repeat calling `callable_fn` with `args` until an exception does not occur
    or `num_retries` attempts have occurred (in which case, nothing is returned).

    Useful for robust downloading when either the client or server has
    a patchy connection.

    Args:
        callable_fn: callable
            The function to call in the backoff loop.
        args:
            The arguments to pass to the callable.
        num_retries: int
            Number of times to retry calling the function before giving up.
    """
    sleep_time = 1
    for attempt_i in range(0, num_retries):
        try:
            val = callable_fn(*args)
            str_error = None
        except Exception as e:
            str_error = str(e)
            if attempt_i == num_retries - 1:
                warnings.warn(f"{callable_fn.__name__} failed with args {args} after {num_retries} retries. "
                              f"Received error {str(e)}. ")
                return

        if str_error:
            sleep(sleep_time)  # wait before trying to fetch the data again
            sleep_time *= 2  # Implement your backoff algorithm here i.e. exponential backoff
        else:
            return val
