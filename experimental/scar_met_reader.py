'''

REference Antarctic Data for Environmental Research (READER) 

MET-READER providing surface and upper air mean climate data

https://legacy.bas.ac.uk/met/READER/

'''


import pandas as pd
import numpy as np
import glob


def reshape_col_month(df, col_name):
    new = pd.DataFrame(columns=['Year', 'Month', col_name])
    yr_arr, mon_arr = [], []
    for yr in df['Year'].values: 
        yr_arr  = np.append( yr_arr, np.repeat(yr,12) )
        mon_arr = np.append( mon_arr, np.arange(1,13) )
    new['Year']   = yr_arr.astype(int)
    new['Month']  = mon_arr.astype(int)
    new[col_name] = np.array(df.drop(columns='Year')).flatten()
    return new


def months_since(df, ref_yr):
    col_name = 'Months_Since_'+str(ref_yr)
    first_yr = np.min(df['Year'].values)
    last_yr  = np.max(df['Year'].values)
    n_yrs    = last_yr - first_yr + 1
    months_since = np.arange(0,n_yrs*12) + ((first_yr-ref_yr)*12.)

    ### NEED TO FIX THIS PROPERLY AT SOME POINT!!!
    if df['Month'].values[0] != 1:
        raise ValueError('first row does not correspond to January')
    if df['Month'].values[-1] != 12:
        print('last row does not correspond to December')
        months_since = months_since[:df.shape[0]]

    df[col_name] = months_since.astype(int)
    df = df.set_index(col_name)
    return df




### List all *.txt files

facilities = ['surface', 'aws']

for fac in facilities:
    files = glob.glob("RAW/"+fac+"/*.txt")
    names = ['Year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 
                'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df    = pd.DataFrame()
    ref_yr   = 1800

    for file in files:
        var = pd.read_csv(file, nrows=0).columns[0]
        var = var.replace('msl_pressure', 'MSLP').replace('station_level_pressure', 'StnLevP') 
        var = var.replace('_','').replace(' ','_').replace('temperature','T') 
        var = eval(repr(var).replace("\\", '')) # special method to replace '\'
        df_tmp  = pd.read_csv(file, delim_whitespace=True, skiprows=1, 
                                    names=names, na_values='-')
        df_tmp  = reshape_col_month(df_tmp, var)
        df_tmp  = months_since(df_tmp, ref_yr)
        print file
        df = pd.concat( [df, df_tmp], axis=1 )


    ### Remove duplicate columns
    yr_cols = df['Year'].values
    if all(np.nanstd(yr_cols, axis=1) == 0):
        yr_col = np.nanmin(yr_cols, axis=1)
        df = df.drop(columns=['Year'])
        df['Year'] = yr_col.astype(int)

    m_cols = df['Month'].values
    if all(np.nanstd(m_cols, axis=1) == 0):
        m_col = np.nanmin(m_cols, axis=1)
        df = df.drop(columns=['Month'])
        df['Month'] = m_col.astype(int)

    ### Tidy up columns
    df = df.reset_index()
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('Year')))
    cols.insert(1, cols.pop(cols.index('Month')))
    df = df.loc[:, cols]

    ### Save to csv
    df.to_csv('READER_'+fac+'_combined_monthly.csv', index=False) 