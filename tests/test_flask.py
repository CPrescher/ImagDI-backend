import os
import shutil
import io
import unittest
import tempfile
from pathlib import Path

from PIL import Image
import numpy as np

from backend.app import app


def create_temp_tiff(img_data):
    temp_file_dir = Path(tempfile.gettempdir(), "imagdi")
    temp_file_dir.mkdir(exist_ok=True)
    temp_file_path = Path(temp_file_dir.absolute(), os.urandom(24).hex() + '.tiff')
    temp_file = open(temp_file_path, "wb")
    im = Image.fromarray(img_data)
    im.save(temp_file)
    temp_file.close()
    return temp_file


def save_tiff(img_data, filename):
    with open(filename, "wb") as f:
        im = Image.fromarray(img_data)
        im.save(f)


def create_tiff_file_series(img_arrays):
    temp_directory_path = Path(tempfile.gettempdir(), 'imagdi')
    temp_directory_path.mkdir(exist_ok=True)
    file_names = []
    for ind, img_array in enumerate(img_arrays):
        file_name = os.path.join(temp_directory_path, 'series_{:03d}.tiff'.format(ind + 1))
        save_tiff(img_array, file_name)
        file_names.append(file_name)
    return file_names


class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        shutil.rmtree(Path(tempfile.gettempdir(), 'imagdi'), ignore_errors=True)

    def test_load_image(self):
        rand_img = np.random.random((5, 5))
        temp_file = create_temp_tiff(rand_img)

        response = self.app.post('/load', data=dict(filename=temp_file.name))
        self.assertEqual(response.status_code, 200)
        received_img = np.load(io.BytesIO(response.data))

        self.assertTrue(np.allclose(received_img, rand_img))
        self.assertEqual(rand_img.shape, received_img.shape)

    def test_load_next_image(self):
        img_arrays = [np.random.random((5, 5)) for _ in range(10)]
        file_names = create_tiff_file_series(img_arrays)

        # load first image
        response = self.app.post('/load', data=dict(filename=file_names[0]))
        self.assertEqual(response.status_code, 200)

        response = self.app.post('/next')
        self.assertEqual(response.status_code, 200)

        received_img = np.load(io.BytesIO(response.data))
        self.assertTrue(np.allclose(received_img, img_arrays[1]))
        self.assertEqual(img_arrays[1].shape, received_img.shape)

    def test_load_previous_image(self):
        img_arrays = [np.random.random((5, 5)) for _ in range(3)]
        file_names = create_tiff_file_series(img_arrays)

        # load third image
        response = self.app.post('/load', data=dict(filename=file_names[2]))
        self.assertEqual(response.status_code, 200)

        response = self.app.post('/previous')
        self.assertEqual(response.status_code, 200)

        received_img = np.load(io.BytesIO(response.data))
        self.assertTrue(np.allclose(received_img, img_arrays[1]))
        self.assertEqual(img_arrays[1].shape, received_img.shape)

    def test_get_random_array(self):
        x_dim = 1024
        y_dim = 1024
        response = self.app.post('/random', data=dict(x_dim=1024, y_dim=1024))
        self.assertEqual(response.status_code, 200)

        received_img = np.load(io.BytesIO(response.data))
        self.assertTrue(received_img.shape, (x_dim, y_dim))

    def test_get_gaussian_array(self):
        response = self.app.post('/gaussian', data=dict(
            center_x=348,
            center_y=458,
            amplitude=100,
            fwhm_x=30,
            fwhm_y=20,
            x_dim=1024,
            y_dim=1024
        ))
        self.assertEqual(response.status_code, 200)

        received_img = np.load(io.BytesIO(response.data))
        self.assertEqual(received_img.shape, (1024, 1024))
        self.assertEqual(np.max(received_img), 100)

    def test_get_filename(self):
        temp_file = create_temp_tiff(np.random.random((5, 5)))

        response = self.app.post('/load', data=dict(filename=temp_file.name))
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/filename')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), str(temp_file.name))
