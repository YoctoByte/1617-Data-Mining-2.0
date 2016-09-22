from scipy.io import loadmat
import numpy as np
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt
from itertools import combinations


FN_WINE_DATA = 'Data/wine.mat'
FN_ZIP_DATA = 'Data/zipdata.mat'


def ass2_1():
    # Load the wine data:
    raw_data = loadmat(FN_WINE_DATA)
    wine_data = raw_data['X']
    attributes = [attr[0] for attr in raw_data['attributeNames'][0]]

    # 2.1.1
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
        axises[i].hist(col, n_bins)
        axises[i].set_title(attributes[i])
    plt.show()

    # 2.1.2
    # Calculate the pearson Coefficients:
    pearson_coefficients = list()
    quality_scores = wine_data[:, 11]
    for i, col in enumerate(wine_data[:, :-1].T):
        col = col.T
        pearson_coefficients.append((pearsonr(col, quality_scores)[0], i))

    # Sort the coefficients and print them:
    pearson_coefficients.sort(key=lambda x: abs(x[0]), reverse=True)
    print('Pearson Coefficients between attributes and quality scores: ')
    for pearson_coefficient, attribute_nr in pearson_coefficients:
        print('  ' + attributes[attribute_nr] + ': ' + str(pearson_coefficient))

    # Plot the scatter plots:
    fig, axis = plt.subplots(nrows=3, ncols=4)
    axises = axis.flat
    for i, (pearson_coefficient, attribute_nr) in enumerate(pearson_coefficients):
        attr_values = wine_data[:, attribute_nr]
        axises[i].scatter(quality_scores, attr_values, alpha=0.02)
        axises[i].set_title(attributes[attribute_nr] + ' vs. Quality score\nPCC: ' + str(pearson_coefficient))
    plt.show()


def ass2_2():
    # Load the data:
    raw_data = loadmat(FN_ZIP_DATA)
    train_data = raw_data['traindata']
    test_data = raw_data['testdata']

    matrix_x = train_data[:, 1:]
    vector_y = train_data[:, 0]

    # Create a dataset containing only ones and zeros:
    not_one_zero_ids = list()
    for i, digit in enumerate(vector_y):
        if digit not in [0, 1]:
            not_one_zero_ids.append(i)
    only_one_zero = np.delete(matrix_x, not_one_zero_ids, 0)

    # PCA:
    mu = np.mean(only_one_zero, axis=0)
    zero_mean_data = only_one_zero - (mu * np.ones((only_one_zero.shape[0], 1)))
    u, s, vt = np.linalg.svd(zero_mean_data)
    v = vt.T
    print(u.shape)
    print(s.shape)
    print(v.shape)


def ass2_3():
    population = [2, 3, 6, 8, 11, 18]

    # 2.3.1 I:
    mean = sum(population)/len(population)
    std_dev = np.std(population)
    print('mean population = ' + str(mean))
    print('standard deviation = ' + str(std_dev))

    # 2.3.1 II:
    two_sample_combs = list(combinations(population, 2))
    four_sample_combs = list(combinations(population, 4))
    print('two sample combinations =')
    for comb in two_sample_combs:
        print('  ' + str(comb))
    print('four sample combinations = ')
    for comb in four_sample_combs:
        print('  ' + str(comb))


if __name__ == '__main__':
    # ass2_1()
    # ass2_2()
    ass2_3()
