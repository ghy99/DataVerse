"""Tests for views.py."""

import pytest

import ckanext.packagecontroller.validators as validators


import ckan.plugins.toolkit as tk


@pytest.mark.ckan_config("ckan.plugins", "packagecontroller")
@pytest.mark.usefixtures("with_plugins")
def test_packagecontroller_blueprint(app, reset_db):
    resp = app.get(tk.h.url_for("packagecontroller.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, packagecontroller!"
