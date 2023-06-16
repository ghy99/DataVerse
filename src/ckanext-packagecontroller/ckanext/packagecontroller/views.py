from flask import Blueprint


packagecontroller = Blueprint(
    "packagecontroller", __name__)


def page():
    return "Hello, packagecontroller!"


packagecontroller.add_url_rule(
    "/packagecontroller/page", view_func=page)


def get_blueprints():
    return [packagecontroller]
