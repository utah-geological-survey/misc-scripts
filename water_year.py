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

  def plot_circday(dfwy,val,climvar='Temperature',tickint = 2, offset=True):

    df = dfwy.copy()
    #df[val] = df[val].apply(lambda x: x - df[val].mean(),1)
    df = df.resample('1D').mean().interpolate(method='time')


    df['year'] = df.index.year
    df['month'] = df.index.month
    #df[val] = df[val].mean() - df[val]

    #modf = df.groupby(['year','month']).mean()[val]           
    modf = df
    minval = modf.min()
    maxval = modf.max()
    
    if offset:
        modf = modf + 10

    fig = plt.figure(figsize=(14,14))
    ax1 = plt.subplot(111, projection='polar')

    morng = pd.date_range('1/1/2014','12/31/2014',freq='1MS')
    ax1.set_xticks(np.linspace(0,2*np.pi,13))
    ax1.set_xticklabels([d.strftime('%b') for d in morng])
    #ax1.set_yticklabels([])
    #fig.set_facecolor("#323331")
    
    plotymin = modf[val].min()-1
    plotymax = modf[val].max()

    yticks = np.arange(plotymin,plotymax+tickint,tickint)
    
    if offset:
        ylabs = [round(i,1) for i in np.arange(plotymin-10,plotymax-10+tickint,tickint)]
    else:
        ylabs = [round(i,1) for i in np.arange(plotymin,plotymax+tickint,tickint)]

    ax1.set_ylim(plotymin, plotymax)
    ax1.set_yticks(yticks)
    ax1.set_yticklabels(ylabs)
    ax1.set_title(f"{climvar} at {val.split('_')[0]}", fontdict={'fontsize': 20})
    #ax1.set_axis_bgcolor('#000100')

    color=iter(plt.cm.viridis(np.linspace(0,1,len(dfwy.index.year.unique()))))
    for year in modf.index.year.unique():
        clr=next(color)
        begdate = pd.to_datetime(f"{year}-01-01")
        enddate = pd.to_datetime(f"{year+1}-01-01")
        yrmodf = modf.loc[begdate:enddate,val]
        dtrng = pd.date_range(begdate,enddate,freq='1D')
        datelabels = [int(d.strftime('%j')) for d in dtrng]
        monthpi = dict(zip(datelabels,np.linspace(0,2*np.pi,len(datelabels)+1)))
        r = yrmodf.values
        theta = [monthpi[i] for i in yrmodf.index.dayofyear]
        ax1.plot(theta, r, color=clr,label=year)

    plt.legend()
    return fig, ax1
                  
def plot_circtime(dfwy,val,climvar='Temperature',tickint = 2, offset=True):

    df = dfwy.copy()
    #df[val] = df[val].apply(lambda x: x - df[val].mean(),1)

    dtrng = pd.date_range('1/1/2014','12/31/2014',freq='1MS')
    datelabels = [int(d.strftime('%m')) for d in dtrng]
    monthpi = dict(zip(datelabels,np.linspace(0,2*np.pi,13)))

    df['year'] = df.index.year
    df['month'] = df.index.month
    #df[val] = df[val].mean() - df[val]

    modf = df.groupby(['year','month']).mean()[val]           

    minval = modf.min()
    maxval = modf.max()
    
    if offset:
        modf = modf + 10

    fig = plt.figure(figsize=(14,14))
    ax1 = plt.subplot(111, projection='polar')

    ax1.set_xticks(np.linspace(0,2*np.pi,13))
    ax1.set_xticklabels([d.strftime('%b') for d in dtrng])
    #ax1.set_yticklabels([])
    #fig.set_facecolor("#323331")
    
    plotymin = modf.min()-1
    plotymax = modf.max()
    yticks = np.arange(plotymin,plotymax+tickint,tickint)
    
    if offset:
        ylabs = [round(i,1) for i in np.arange(plotymin-10,plotymax-10+tickint,tickint)]
    else:
        ylabs = [round(i,1) for i in np.arange(plotymin,plotymax+tickint,tickint)]

    ax1.set_ylim(plotymin, plotymax)
    ax1.set_yticks(yticks)
    ax1.set_yticklabels(ylabs)
    ax1.set_title(f"{climvar} at {val.split('_')[0]}", fontdict={'fontsize': 20})
    #ax1.set_axis_bgcolor('#000100')

    color=iter(plt.cm.viridis(np.linspace(0,1,len(dfwy.index.year.unique()))))
    for year in modf.index.get_level_values(0).unique():
        clr=next(color)
        yrmodf = modf.loc[(year,1):(year+1,1)]
        r = yrmodf.values
        theta = [monthpi[i] for i in yrmodf.index.get_level_values(1)]
        ax1.plot(theta, r, color=clr,label=year)

    plt.legend()
    return fig, ax1
  
