import pylab as pl
from scipy.io import loadmat


X = loadmat('data/wildfaces_grayscale.mat')['X']
N, M = X.shape
print(pl.np.reshape(X[0], (40, 40)).shape)
