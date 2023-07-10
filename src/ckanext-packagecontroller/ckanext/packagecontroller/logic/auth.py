import ckan.plugins.toolkit as tk


@tk.auth_allow_anonymous_access
def packagecontroller_get_sum(context, data_dict):
    return {"success": True}


def get_auth_functions():
    return {
        "packagecontroller_get_sum": packagecontroller_get_sum,
    }
