import ckan.plugins.toolkit as tk
import ckanext.packagecontroller.logic.schema as schema


@tk.side_effect_free
def packagecontroller_get_sum(context, data_dict):
    tk.check_access(
        "packagecontroller_get_sum", context, data_dict)
    data, errors = tk.navl_validate(
        data_dict, schema.packagecontroller_get_sum(), context)

    if errors:
        raise tk.ValidationError(errors)

    return {
        "left": data["left"],
        "right": data["right"],
        "sum": data["left"] + data["right"]
    }


def get_actions():
    return {
        'packagecontroller_get_sum': packagecontroller_get_sum,
    }
