import pathlib
import shutil

import pytest


@pytest.fixture
def local_dir():
    path = pathlib.Path.cwd() / 'local'
    path.mkdir()
    yield path
    shutil.rmtree(path)
