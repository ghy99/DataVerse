"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.packagecontroller.logic import validators


def test_packagecontroller_reauired_with_valid_value():
    assert validators.packagecontroller_required("value") == "value"


def test_packagecontroller_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.packagecontroller_required(None)
