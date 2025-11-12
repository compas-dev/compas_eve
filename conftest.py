from pathlib import Path
import math
import numpy
import pytest

import compas
import compas_eve


def pytest_ignore_collect(collection_path: Path, config):
    # Skip anything under rhino/blender/ghpython
    parts_lower = {p.lower() for p in collection_path.parts}
    if {"rhino", "blender", "ghpython"} & parts_lower:
        return True

    # return None -> don't ignore
    return None


@pytest.fixture(autouse=True)
def add_compas(doctest_namespace):
    doctest_namespace["compas"] = compas


@pytest.fixture(autouse=True)
def add_compas_eve(doctest_namespace):
    doctest_namespace["compas_eve"] = compas_eve


@pytest.fixture(autouse=True)
def add_math(doctest_namespace):
    doctest_namespace["math"] = math


@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    doctest_namespace["np"] = numpy
