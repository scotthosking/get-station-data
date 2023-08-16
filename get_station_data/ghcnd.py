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

import numpy as np
import pandas as pd
from datetime import datetime

import multiprocessing
from functools import partial
import tqdm

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


def process_stn(stn_id, stn_md, include_flags=True, element_types=None):
    stn_md1 = stn_md[stn_md["station"] == stn_id]
    lat = stn_md1["lat"].values[0]
    lon = stn_md1["lon"].values[0]
    elev = stn_md1["elev"].values[0]
    name = stn_md1["name"].values[0]

    # file = 'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/' + stn_id + '.dly'
    filename = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/" + stn_id + ".dly"
    df = _create_DataFrame_1stn(filename, include_flags, element_types)

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


def get_data(my_stns, include_flags=True, element_types=None):
    stn_md = get_stn_metadata()

    # Number of processes to use, you can adjust this based on your system's capabilities
    num_processes = multiprocessing.cpu_count()

    with multiprocessing.Pool(processes=num_processes) as pool:
        partial_process_stn = partial(
            process_stn, stn_md=stn_md, include_flags=include_flags, element_types=element_types
        )
        dfs = list(
            tqdm.tqdm(pool.imap(partial_process_stn, pd.unique(my_stns["station"])))
        )

    df = pd.concat(dfs)
    # df = df.replace(-999.0, np.nan)

    return df.query('element.isin(@element_types)')


def _create_DataFrame_1stn(filename, include_flags, element_types, verbose=False):
    raw_array = pd.Series(np.genfromtxt(filename, delimiter="\n", dtype="str"))

    out_dict = {}
    out_dict["station"] = raw_array.str[0:11]
    out_dict["year"] = raw_array.str[11:15].astype(int)
    out_dict["month"] = raw_array.str[15:17].astype(int)
    out_dict["element"] = raw_array.str[17:21]

    # TODO - Check this
    dfs = []

    if include_flags:
        names = ["value", "mflag", "qflag", "sflag"]
    else:
        names = ["value", "mflag", "qflag", "sflag"]
    for i, n in enumerate(names):
        sub_dict = {}
        for d in range(31):
            idx = np.array([21, 26, 27, 28]) + (8 * d)
            if n == "value":
                out_dict[d] = (
                    raw_array.str[idx[0] : idx[1]]
                    .replace("-9999", np.nan)
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

    # df.columns[30:50
    # type(df["mflag0"].iloc[0])

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
        .sort_values(by=["station", "year", "month", "day", "element"])
        .reset_index(drop=True)
    )

    if include_flags:
        out_df = out_df.fillna({"qflag": " ", "mflag": " ", "sflag": " "})
    
    if element_types is None:
        return out_df
    else:
        return out_df.query('element.isin(@element_types)')


def get_stn_metadata(fname=None):
    url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
    if fname == None:
        fname = url
    md = pd.read_fwf(
        fname,
        colspecs=[(0, 12), (12, 21), (21, 31), (31, 38), (38, 69)],
        names=["station", "lat", "lon", "elev", "name"],
    )
    return md
