import numpy as np
import matplotlib.pyplot as plt

article_style = {
    'axes.titlesize': 'medium',
    'axes.labelsize': 'small'
}

def figlabel(*args, fig=None, **kwargs):
    """Put label in figure coords"""
    if fig is None:
        fig = plt.gcf()
    plt.text(*args, transform=fig.transFigure, **kwargs)


def loghist(x, logy=True, gaussian_comparison=True, ax=None,
            lower_percentile=1e-5, upper_percentile=100-1e-5,
            label='Sample', colors=('k', 'g')):
    """
    Plot log histogram of given samples with normal comparison using
    kernel density estimation
    """
    from scipy.stats import gaussian_kde, norm
    from numpy import percentile

    if ax is None:
        ax = plt.axes()


    p = gaussian_kde(x)

    npts = 100

    p1 = percentile(x, lower_percentile)
    p2 = percentile(x, upper_percentile)
    xx = np.linspace(p1, p2, npts)

    if logy:
        y = np.log(p(xx))
    else:
        y = p(xx)

    ax.plot(xx, y, label=label, c=colors[0])

    if gaussian_comparison:
        mles = norm.fit(x)
        gpdf = norm.pdf(xx, *mles)
        if logy:
            ax.plot(xx, np.log(gpdf),  label='Gauss', c=colors[1])
        else:
            ax.plot(xx, gpdf,  label='Gauss', c=colors[1])

    ax.set_xlim([p1, p2])


def test_loghist():
    from numpy.random import normal

    x = normal(size=1000)
    loghist(x)
    plt.legend()
    plt.show()

def plot2d(x, y, z, ax=None, cmap='RdGy', **kw):
    """ Plot dataset using NonUniformImage class
    
    Args:
        x (nx,)
        y (ny,)
        z (nx,nz)
        
    """
    from matplotlib.image import NonUniformImage
    if ax is None:
        fig = plt.gcf()
        ax  = fig.add_subplot(111)
   
    xlim = (x.min(), x.max())
    ylim = (y.min(), y.max()) 
    
    im = NonUniformImage(ax, interpolation='bilinear', extent=xlim + ylim,
                        cmap=cmap)
   
    im.set_data(x,y,z, **kw)
    ax.images.append(im)
    #plt.colorbar(im)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    return im

def test_plot2d():
    x = np.arange(10)
    y = np.arange(20)
    
    z = x[None,:]**2 + y[:,None]**2
    plot2d(x,y,z)
    plt.show()


def func_plot(df, func, w=1, aspect=1.0, figsize=None, layout=(-1,3),
              sharex=False, sharey=False,
             **kwargs):
    """Plot every column in dataframe with func(series, ax=ax, **kwargs)"""
    ncols = df.shape[1]

    q, r = divmod(ncols, layout[-1])

    nrows = q
    if r> 0:
        nrows +=1

    # Adjust figsize
    if not figsize:
        figsize = (w * layout[-1], w * aspect * nrows)
    fig, axs = plt.subplots(nrows, layout[1], figsize=figsize, sharex=sharex, sharey=sharey)
    lax = axs.ravel().tolist()
    for i in range(ncols):
        ser = df.iloc[:,i]
        ax  = lax.pop(0)
        ax.text(.1,.8, df.columns[i], bbox=dict(fc='white'), transform=ax.transAxes)
        func(ser, ax=ax, **kwargs)

    for ax in lax:
        fig.delaxes(ax)

def pgram(x,ax=None):
    from scipy.signal import welch
    f, Pxx = welch(x.values)
    if not ax:
        ax = plt.gca()

    ax.loglog(f, Pxx)
    ax.grid()
    ax.autoscale(True, tight=True)

def labelled_bar(x, ax=None, pad=200, **kw):
    """A bar chart for a pandas series x with labelling


    x.plot(kind='hist') labels the xaxis only of the plots, and it is nice to
    label the actual bars directly.

    """
    locs = np.arange((len(x)))

    if not ax:
        fig, ax = plt.subplots()

    rects =ax.bar(locs, x,  **kw)
    ax.set_xticks(locs+.5)
    ax.xaxis.set_major_formatter(plt.NullFormatter())


    def autolabel(rects, labels, ax=None, pad=pad):


        for rect, lab in zip(rects, labels):
            lab = str(lab)
            height = rect.get_height() * (1 if rect.get_y() >= 0 else -1)

            kw = {'ha':'center'}
            if height < 0 :
                kw['va'] = 'top'
                height -= ax.transScale.inverted().transform((0, pad))[1]
            else:
                kw['va'] = 'bottom'
                height += ax.transScale.inverted().transform((0, pad))[1]

            ax.text(rect.get_x()+rect.get_width()/2., height, lab,
                        **kw)
    autolabel(rects, x.index, ax=ax, pad=pad)
    return rects, ax
