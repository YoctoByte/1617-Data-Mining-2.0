import scipy.io
import numpy as np
from scipy.stats.mstats import zscore
import matplotlib.pyplot as plt


FN_WINE_DATA = 'Data/wine.mat'


def ass2_1_1():
    # Load the wine data:
    raw_data = scipy.io.loadmat(FN_WINE_DATA)
    wine_data = raw_data['X']
    attributes = raw_data['attributeNames'][0]

    # Filter the outliers:
    for col_nr, max_value in [(1, 20), (7, 10), (10, 100)]:
        col = wine_data[:, col_nr]
        indexes_to_remove = list()
        for index, value in enumerate(col):
            if value > max_value:
                indexes_to_remove.append(index)
        wine_data = np.delete(wine_data, indexes_to_remove, 0)

    # Plot the histograms:
    n_bins = 20
    fig, axis = plt.subplots(nrows=3, ncols=4)
    axises = axis.flat
    for i, col in enumerate(wine_data.T):
        col = col.T
        # col = zscore(col)
        axises[i].hist(col, n_bins)
        axises[i].set_title(attributes[i][0])
    plt.show()


if __name__ == '__main__':
    ass2_1_1()
