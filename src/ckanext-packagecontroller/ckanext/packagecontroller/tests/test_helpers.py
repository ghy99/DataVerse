"""Tests for helpers.py."""

import ckanext.packagecontroller.helpers as helpers


def test_packagecontroller_hello():
    assert helpers.packagecontroller_hello() == "Hello, packagecontroller!"
