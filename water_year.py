def calc_wat_year(df):
  df.loc[:,'month'] = df.index.month
  df.loc[:,'year'] = df.index.year
  df.loc[:,'doy'] = df.index.dayofyear
  
  df['water year'] = df.index.shift(-9,freq='M').year+1
  df['ones'] = 1
  df['water year doy'] = df['ones'].groupby(df['water year']).cumsum()
  df['doylen'] = df['ones'].groupby(df['water year']).count()
  df['water year doy1'] = df.apply(lambda df: df['doy']-273 if df['water year'] > df['year'] else df['doy']+92,1)
  return df

def plot_all_years(dfwy, val, smooth='20D', showmean=False, 
                   eachyr=True, qntile=False, mindate=None, maxdate=None):
    
    
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()
    df = dfwy.copy()
    if maxdate:
        df = df[df.index <= maxdate]
    
    if mindate:
        df = df[df.index >= mindate]
    
    grpd = df.groupby(dfwy.index.dayofyear)[val]
    xm = grpd.median().index
    ym = grpd.median()
    y1 = grpd.quantile(q=0.05)
    y2 = grpd.quantile(q=0.95)

    fig, ax = plt.subplots(1,1)
    
    color=iter(plt.cm.viridis(np.linspace(0,1,len(dfwy.index.year.unique()))))
    # doy needed for smoother hydrograph; using .index.doy works below, but it creates steps
    df['doy'] = df.index.dayofyear
    
    if eachyr:
        yrlist = dfwy.index.year.unique()
        if type(eachyear) == list:
            yrlist = eachyear
        
        for year in yrlist:
            clr=next(color)
            xyr = df[df.index.year == year].rolling(smooth).mean()['doy']
            yyr = df[df.index.year == year].rolling(smooth).mean()[val]
            ax.plot(xyr,yyr,alpha=0.5,label=year, c=clr)
    
    if showmean:
        ax.plot(xm,ym,label='Mean')

    if qntile:
        ax.fill_between(xm,y1,y2, label='90% of data values', alpha=0.2, linewidth=0)

    ax.legend()
    ax.grid(True)

    ax.set_xlabel('month')
    dtrng = pd.date_range('1/1/2014','12/31/2014',freq='1MS')
    datelabels = [d.strftime('%b') for d in dtrng]
    ax.set_xticks([i.dayofyear for i in dtrng])#dtrng)#,rotation=90)
    ax.set_xticklabels(datelabels)
    ax.set_xlim(0,365)
    return fig, ax
