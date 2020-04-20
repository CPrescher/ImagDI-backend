import numpy as np


def gaussian_2d(x_dim, y_dim, amplitude, center_x, center_y, fwhm_x, fwhm_y, theta):
    x = np.arange(0, x_dim, 1)
    y = np.arange(0, y_dim, 1)
    x, y = np.meshgrid(x, y)

    sigma_x = fwhm_x/2.35482
    sigma_y = fwhm_y/2.35482

    a = (np.cos(theta) ** 2) / (2 * sigma_x ** 2) + (np.sin(theta) ** 2) / (2 * sigma_y ** 2)
    b = -(np.sin(2 * theta)) / (4 * sigma_x ** 2) + (np.sin(2 * theta)) / (4 * sigma_y ** 2)
    c = (np.sin(theta) ** 2) / (2 * sigma_x ** 2) + (np.cos(theta) ** 2) / (2 * sigma_y ** 2)
    g = amplitude * np.exp(
        - (a * ((x - center_x) ** 2) + 2 * b * (x - center_x) * (y - center_y) + c * ((y - center_y) ** 2)))
    return g
