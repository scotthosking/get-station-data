
def nearest_stn(df, my_x, my_y, n_neighbours=1):

    from scipy import spatial

    x = df['lon'].values
    y = df['lat'].values

    if x.min() <= my_x <= x.max():
        pass
    else:
        raise ValueError('my_x not within range of longitudes')

    if y.min() <= my_y <= y.max():
        pass
    else:
        raise ValueError('my_y not within range of latitudes')

    tree = spatial.KDTree(list(zip(x, y)))
    d, i = tree.query( [(my_x, my_y)], k=n_neighbours )

    if i.ndim == 1: index = i
    if i.ndim == 2: index = i[0]
    df1 = df.loc[index]

    return df1

