"""
Computing El Nino composites
============================

This example demonstrates constructing a NINO3.4 index from using it to produce
composite maps of sea-surface-temperature (SST) for El Nino and La Nina.

References
----------

    Trenberth, K. E. (1997) The Definition of El Nino.
    Bulletin of the American Meteorological Society, Vol 78, pp 2771-2777.

"""
import numpy as np
import iris
import iris.plot as iplt
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt


# define SST anomaly thresholds for classifying El Nino and La Nina events:
EL_NINO_THRESHOLD = 0.4
LA_NINA_THRESHOLD = -0.4


def classify(index_value, low_threshold, high_threshold):
    """Classify a value given thresholds.

    Args:

    index_value: float
        The value to classify.

    low_threshold: float
        Threshold below which *index_value* is classified as low ('L').

    high_threshold: float
        Threshold above which *index_value* is classified as high ('H').

    Returns:

    classification: str
        Single character string, either: 'H'=high, 'L'=low, 'N'=null.

    """
    if index_value <= low_threshold:
        return 'L'
    elif index_value >= high_threshold:
        return 'H'
    else:
        return 'N'


def filter_events(seq, min_length):
    """
    Nullify high or low events in a sequence that are below a minimum
    length.

    A high event is a continuous sub-sequence of 'H', and similarly for
    low ('L') events.

    Args:

    seq: array
        Array of classification characters ('H'=high, 'L'=low,
        'N'=null).

    min_length: int
        Minimum length of an event. Events shorter than this are
        nullified (set to 'N').

    """
    for char in ('H', 'L'):
        bits = np.concatenate((np.array([0]),
                               np.where(np.array(seq) == char, 1, 0),
                               np.array([0])))
        diff = np.diff(bits)
        starts, = np.where(diff > 0)
        ends, = np.where(diff < 0)
        lengths = ends - starts
        for start, length in zip(starts, lengths):
            if length < min_length:
                for i in xrange(length):
                    seq[start + i] = 'N'
    return


def main():

    # load the winter-mean sea-surface-temperature (SST) anomaly data:
    fname = iris.sample_data_path('sst.mon.anom.nc')
    sst = iris.load_cube(fname)

    # extract the NINO3.4 region from the SST cube:
    nino34_region = iris.Constraint(latitude=lambda l: -5 <= l <= 5,
                                    longitude=lambda l: 190 <= l <= 240)
    nino34 = sst.extract(nino34_region).collapsed(['latitude', 'longitude'],
                                                  iris.analysis.MEAN)

    # construct a 5-month running-mean of the NINO3.4 index, this will lose
    # 2 data points at either end of the time series, so we also extract only
    # the points that will remain from the sst cube as well:
    nino34_rm = nino34.rolling_window('time', iris.analysis.MEAN, 5)
    sst = sst[2:-2]

    # for each month in the NINO3.4 index classify into either high temperature
    # ('H'), low temperature ('L') or null ('N') events, then identify El Nino
    # and La Nina events as those that are classed as 'H' or 'L' respectively
    # for 6 months or more in a row:
    high_low_null = np.vectorize(classify)(nino34_rm.data,
                                           LA_NINA_THRESHOLD,
                                           EL_NINO_THRESHOLD)
    filter_events(high_low_null, 6)

    # create an auxiliary coordinate that describes the phase of ENSO and add
    # it to the time dimension of the SST cube:
    enso_aux = iris.coords.AuxCoord(high_low_null, long_name='ENSO_phase')
    time_dim = sst.coord_dims(sst.coord('time'))[0]
    sst.add_aux_coord(enso_aux, data_dims=time_dim)

    # construct composites for El Nino and La Nina (note this could also be
    # achieved using the aggregated_by method, but this would also compute
    # a null composite)
    el_nino = sst.extract(iris.Constraint(ENSO_phase='H'))
    el_nino.remove_coord('ENSO_phase')
    el_nino = el_nino.collapsed('time', iris.analysis.MEAN)
    el_nino.rename('El Nino')
    la_nina = sst.extract(iris.Constraint(ENSO_phase='L'))
    la_nina.remove_coord('ENSO_phase')
    la_nina = la_nina.collapsed('time', iris.analysis.MEAN)
    la_nina.rename('La Nina')

    # plot composites of each phase
    fig = plt.figure(figsize=(9, 8))
    contour_levels = np.arange(-1.0, 1.1, .2)
    for icomp, composite in enumerate([el_nino, la_nina]):
        ax = plt.subplot(2, 1, icomp + 1,
                         projection=ccrs.PlateCarree(central_longitude=180))
        c = iplt.contourf(composite, contour_levels, extend='both',
                          cmap=plt.cm.RdBu_r, coords=['longitude', 'latitude'])
        ax.set_extent([100, 270, -30, 60], crs=ccrs.PlateCarree())
        ax.add_feature(cartopy.feature.LAND, facecolor='w', edgecolor='k')
        cbar = plt.colorbar(c, orientation='vertical', ticks=contour_levels,
                            drawedges=True)
        cbar.ax.tick_params(length=0)
        ax.set_title('Composite {!s} (1960-2010)'.format(composite.name()))
    plt.tight_layout()
    plt.show()

    # plot the NINO3.4 index indicating El Nino and La Nina events with shading
    plt.figure(figsize=(8, 4))
    ax = plt.subplot(111)
    line, = iplt.plot(nino34_rm, color='k', linewidth=1.5, coords=['time'])
    time_values = line.get_xdata()
    ax.fill_between(time_values,
                    np.ones(time_values.shape) * EL_NINO_THRESHOLD,
                    nino34_rm.data,
                    where=sst.coord('ENSO_phase').points == 'H',
                    facecolor='r', edgecolor='none')
    ax.fill_between(time_values,
                    np.ones(time_values.shape) * LA_NINA_THRESHOLD,
                    nino34_rm.data,
                    where=sst.coord('ENSO_phase').points == 'L',
                    facecolor='b', edgecolor='none')
    ax.axhline(y=EL_NINO_THRESHOLD, color='k', linestyle='--')
    ax.axhline(y=LA_NINA_THRESHOLD, color='k', linestyle='--')
    ax.set_title('NINO3.4 Index')
    ax.set_ylabel('SST Anomaly / degrees C')
    ax.set_xlabel('Time')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
