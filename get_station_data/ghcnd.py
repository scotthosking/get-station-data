'''

Extract, process and save data from the
Global Historical Climatology Network Daily (GHCND) Version 3.22

GHCND README: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt


ghcnd.py
---------

Author: Dr Scott Hosking (British Antarctic Survey)
Date:   28th February 2017

Updated: 29th August 2022 - add new data source root location (https://www.ncei.noaa.gov/)

'''

import numpy as np
import pandas as pd
from datetime import datetime
import tqdm 

missing_id = '-9999'


def get_data(my_stns, include_flags=True):

    stn_md = get_stn_metadata()
    dfs = []

    for stn_id in tqdm.tqdm(pd.unique(my_stns['station'])):

        stn_md1 = stn_md[ stn_md['station'] == stn_id ]
        lat     = stn_md1['lat'].values[0]
        lon     = stn_md1['lon'].values[0]
        elev    = stn_md1['elev'].values[0]
        name    = stn_md1['name'].values[0]

        # file = 'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/'+stn_id+'.dly'
        file = 'https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/'+stn_id+'.dly'
        df   = _create_DataFrame_1stn(file, include_flags=include_flags)

        if len(pd.unique(df['station'])) == 1:
            df['lon']  = lon
            df['lat']  = lat
            df['elev'] = elev
            df['name'] = name
        else:
            raise ValueError('more than one station ID in file')

        dfs.append(df)

    df = pd.concat(dfs)

    df = df.replace(-999.0, np.nan)

    return df




def _create_DataFrame_1stn(filename, verbose=False, include_flags=True):
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
                    raw_array.str[idx[0] : idx[1]].replace("-9999", np.nan).astype(float)
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
    assert (
        dfs[0][["station", "year", "month", "day", "element"]]
        == dfs[1][["station", "year", "month", "day", "element"]]
    ).all(axis=None)
    assert (
        dfs[2][["station", "year", "month", "day", "element"]]
        == dfs[3][["station", "year", "month", "day", "element"]]
    ).all(axis=None)

    out_df = dfs[0]
    if include_flags:
        for i in range(1, 4):
            n = names[i]
            out_df[n] = dfs[i][n]

    out_df["day"] = out_df.day.astype(int) + 1
    out_df["date"] = pd.to_datetime(out_df[["year", "month", "day"]], errors="coerce")
    out_df.loc[out_df.element.isin(['PRCP', 'TMAX', 'TMIN', 'AWND', 'EVAP', 
                                    'MDEV', 'MDPR', 'MDTN', 'MDTX', 
                                    'MNPN', 'MXPN']),  "value"] /= 10 
    out_df = (
        out_df.dropna(subset="date")
        .sort_values(by=["station", "year", "month", "day", "element"])
        .reset_index(drop=True))

    if include_flags:
        out_df = out_df.fillna({"qflag": " ", "mflag": " ", "sflag": " "})
    
    return out_df 


def get_stn_metadata(fname=None):
    url = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt'
    if fname == None:
        fname = url
    md = pd.read_fwf(fname, colspecs=[(0,12), (12,21), (21,31), 
                                            (31,38), (38,69)], 
                        names=['station','lat','lon','elev','name'])
    return md



