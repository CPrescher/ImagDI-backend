import io
from copy import deepcopy

import flask
from flask import request

import numpy as np
import fabio

from imagdi.util.FileIteration import get_next_file, get_previous_file
from imagdi.util.math import gaussian_2d


class ImgBrowser:
    def __init__(self):
        self._file_name = ''
        self._fabio = None
        self.img_data = None

    def load_image(self, file_name):
        self._file_name = file_name
        self._fabio = fabio.open(file_name)
        self.img_data = self._fabio.data

    def next(self):
        if self._file_name == '':
            return
        next_file_name = get_next_file(self._file_name)
        self.load_image(next_file_name)

    def previous(self):
        if self._file_name == '':
            return
        previous_file_name = get_previous_file(self._file_name)
        self.load_image(previous_file_name)

    @property
    def byte_img(self):
        return convert_array_to_bytes(self.img_data)

    @property
    def file_name(self):
        return self._file_name




browser = ImgBrowser()


def convert_array_to_bytes(numpy_array):
    bytestream = io.BytesIO()
    np.save(bytestream, numpy_array)
    return bytestream.getvalue()


def create_app(test_config=None):
    app = flask.Flask(__name__)

    @app.route('/load', methods=['POST'])
    def load_image():
        filename = request.form.get('filename')
        browser.load_image(filename)
        return browser.byte_img


    @app.route('/next', methods=['POST'])
    def next_file():
        browser.next()
        return browser.byte_img


    @app.route('/previous', methods=['POST'])
    def previous_file():
        browser.previous()
        return browser.byte_img


    @app.route('/filename')
    def file_name():
        return browser.file_name


    @app.route('/random', methods=['POST'])
    def random():
        x_dim = int(request.form.get('x_dim'))
        y_dim = int(request.form.get('y_dim'))
        return convert_array_to_bytes(np.random.random((x_dim, y_dim)))


    @app.route('/gaussian', methods=['POST'])
    def gaussian():
        default_param = dict(
            x_dim=1024,
            y_dim=1024,
            center_x=512,
            center_y=512,
            fwhm_x=100,
            fwhm_y=100,
            amplitude=1000,
            theta=0,
        )
        post_param = request.form
        param = default_param

        for key in default_param.keys():
            if key in post_param.keys():
                param[key] = float(post_param[key])

        gaussian = gaussian_2d(**param)
        return convert_array_to_bytes(gaussian)

    return app
