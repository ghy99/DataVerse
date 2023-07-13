# encoding: utf-8
from __future__ import annotations

import cgi
import json
import logging
from typing import Any, cast, Optional, Union

from werkzeug.wrappers.response import Response as WerkzeugResponse
import flask
from flask.views import MethodView

import ckan.lib.base as base
import ckan.lib.datapreview as lib_datapreview
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.lib.uploader as uploader
import ckan.logic as logic
import ckan.model as model
import ckan.plugins as plugins
from ckan.lib import signals
from ckan.common import _, config, g, request, current_user
from ckan.views.home import CACHE_PARAMETERS
from ckan.views.dataset import (
    _get_pkg_template,
    _get_package_type,
    _setup_template_variables,
)

from ckan.types import Context, Response

import os
import shutil
from werkzeug.datastructures import FileStorage
from clearml import Dataset

Blueprint = flask.Blueprint
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key

log = logging.getLogger(__name__)

resource = Blueprint(
    "dataset_resource",
    __name__,
    url_prefix="/dataset/<id>/resource",
    url_defaults={"package_type": "dataset"},
)
prefixed_resource = Blueprint(
    "resource",
    __name__,
    url_prefix="/dataset/<id>/resource",
    url_defaults={"package_type": "dataset"},
)


def read(package_type: str, id: str, resource_id: str) -> Union[Response, str]:
    context = cast(
        Context,
        {
            "model": model,
            "session": model.Session,
            "user": current_user.name,
            "auth_user_obj": current_user,
            "for_view": True,
        },
    )

    try:
        package = get_action("package_show")(context, {"id": id})
    except NotFound:
        return base.abort(404, _("Dataset not found"))
    except NotAuthorized:
        if config.get("ckan.auth.reveal_private_datasets"):
            if current_user.is_authenticated:
                return base.abort(
                    403, _("Unauthorized to read resource %s") % resource_id
                )
            else:
                return h.redirect_to(
                    "user.login",
                    came_from=h.url_for(
                        "resource.read", id=id, resource_id=resource_id
                    ),
                )
        return base.abort(404, _("Dataset not found"))

    resource = None
    for res in package.get("resources", []):
        if res["id"] == resource_id:
            resource = res
            break
    if not resource:
        return base.abort(404, _("Resource not found"))

    # get package license info
    license_id = package.get("license_id")
    try:
        package["isopen"] = model.Package.get_license_register()[license_id].isopen()
    except KeyError:
        package["isopen"] = False

    resource_views = get_action("resource_view_list")(context, {"id": resource_id})
    resource["has_views"] = len(resource_views) > 0

    current_resource_view = None
    view_id = request.args.get("view_id")
    if resource["has_views"]:
        if view_id:
            current_resource_view = [rv for rv in resource_views if rv["id"] == view_id]
            if len(current_resource_view) == 1:
                current_resource_view = current_resource_view[0]
            else:
                return base.abort(404, _("Resource view not found"))
        else:
            current_resource_view = resource_views[0]

    # required for nav menu
    pkg = context["package"]
    dataset_type = pkg.type or package_type

    # TODO: remove
    g.package = package
    g.resource = resource
    g.pkg = pkg
    g.pkg_dict = package

    extra_vars: dict[str, Any] = {
        "resource_views": resource_views,
        "current_resource_view": current_resource_view,
        "dataset_type": dataset_type,
        "pkg_dict": package,
        "package": package,
        "resource": resource,
        "pkg": pkg,
    }

    template = _get_pkg_template("resource_template", dataset_type)
    return base.render(template, extra_vars)


def download(
    package_type: str, id: str, resource_id: str, filename: Optional[str] = None
) -> Union[Response, WerkzeugResponse]:
    """
    Provides a direct download by either redirecting the user to the url
    stored or downloading an uploaded file directly.
    """
    context = cast(
        Context,
        {
            "model": model,
            "session": model.Session,
            "user": current_user.name,
            "auth_user_obj": current_user,
        },
    )

    try:
        rsc = get_action("resource_show")(context, {"id": resource_id})
        get_action("package_show")(context, {"id": id})
    except NotFound:
        return base.abort(404, _("Resource not found"))
    except NotAuthorized:
        return base.abort(403, _("Not authorized to download resource"))

    if rsc.get("url_type") == "upload":
        upload = uploader.get_resource_uploader(rsc)
        filepath = upload.get_path(rsc["id"])
        resp = flask.send_file(filepath, download_name=filename)

        if rsc.get("mimetype"):
            resp.headers["Content-Type"] = rsc["mimetype"]
        signals.resource_download.send(resource_id)
        return resp

    elif "url" not in rsc:
        return base.abort(404, _("No download is available"))
    return h.redirect_to(rsc["url"])


def change_dataset_title(pkg_dict):
    """
    This function is used to change the dataset title. 
    Similar to the code written in `after_dataset_create()` in packagecontroller extension's `plugin.py`.

    Args:
        pkg_dict (dict): The whole package dictionary

    Returns:
        pkg_dict (dict): The whole package dictionary with the new titles.
    """
    dataset = None
    try:
        dataset = Dataset.get(dataset_id=pkg_dict["clearml_id"])
        # put the download url in pkg_dict'
    except Exception as e:
        logging.warning(
            f"ClearML ID:{pkg_dict['clearml_id']} does not exist in the ClearML database."
        )

    if dataset == None:
        logging.warning(
            f"****************CLEARML ID IS NOT VALID. DID NOT MANAGE TO RETRIEVE DATASET"
        )
        return pkg_dict

    pkg_dict["clearml_download_url"] = dataset.get_default_storage()

    # Changing metadata fields for the things below
    pkg_dict["project_title"] = dataset.project
    pkg_dict["dataset_title"] = dataset.name
    new_title = dataset.name + "-v" + dataset._dataset_version
    new_title = new_title.replace(" ", "-")
    new_title = new_title.replace(".", "-")
    new_title = new_title.lower()
    # warning(f"---------- NEW TITLE: {new_title}")
    # pkg_dict['name'] = new_name
    pkg_dict["title"] = new_title

    new_pkg_dict = get_action("package_update")({}, pkg_dict)
    logging.warning(f"-----*****----- THIS IS THE UPDATED PKG DICT -----*****-----")
    for key, val in new_pkg_dict.items():
        logging.warning(f"***** {key} : {val} -----")

    return new_pkg_dict


def upload_to_clearml(
    path_to_folder,
    path_to_file,
    package_id,
    project_title,
    dataset_title,
    parent_datasets,
):
    """
    This function handles the uploading to ClearML.
    We retrieve the uploaded files through path_to_folder / path_to_file and upload them to ClearML as a dataset.
    We also check for possible parent_datasets that users might want their dataset to inherit from.

    Args:
        path_to_folder (str): folder path for uploaded folders
        path_to_file (str): file path for uploaded file
        package_id (str): package ID (Not used)
        project_title (str): Project title to be named in ClearML
        dataset_title (str): Dataset title to be named in ClearML
        parent_datasets (str): Parent Datasets that new dataset should inherit from.

    Returns:
        dataset.id (str): returns the ID of the newly created dataset in ClearML so that we can store this ID in DataVerse.
    """
    logging.warning(f"Package ID: {package_id}")
    logging.warning(f"Folder Path: {path_to_folder}")
    logging.warning(f"Project Title: {project_title}")
    logging.warning(f"Dataset Title: {dataset_title}")
    logging.warning(f"Parent Datasets: {parent_datasets}")
    if parent_datasets:
        dataset = Dataset.create(
            dataset_project=project_title,
            dataset_name=dataset_title,
            parent_datasets=list(parent_datasets),
        )
    else:
        dataset = Dataset.get(
            dataset_project=project_title, dataset_name=dataset_title, auto_create=True
        )

    logging.warning(f"----------ADDING FILES TO DATASET----------")
    if path_to_folder != None:
        dataset.add_files(path=r"{}".format(path_to_folder))
    if path_to_file != None:
        dataset.add_files(path=r"{}".format(path_to_file))
    logging.warning(f"----------UPLOADING TO CLEARML----------")
    dataset.upload(show_progress=True, verbose=True)
    logging.warning(f"----------FINALIZING DATASET----------")
    # if resource_show['save'] =='go-metadata':
    dataset.finalize(verbose=True, raise_on_error=True, auto_upload=True)
    return dataset.id


class CreateView(MethodView):
    def post(self, package_type: str, id: str) -> Union[str, Response]:
        logging.warning(
            "__________________________________________________________________________"
        )
        logging.warning("THIS IS THE FIRST LINE OF POST IN RESOURCE.py")
        package_details = get_action("package_show")({}, {"id": id})
        logging.warning(f"Package Details: ")
        for key, val in package_details.items():
            logging.warning(f"{key} : {val}")
        parent_ids = []
        if "extras" in package_details:
            for extra in package_details["extras"]:
                parent_ids.append(extra["key"])
        try:
            for parent_id in parent_ids:
                ds = Dataset.get(dataset_id=parent_id)
        except Exception as e:
            return base.abort(404, _("Invalid Parent ID"))
        save_action = request.form.get("save")
        data = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(request.form))))
        logging.warning(
            f"_________ PRINTING DATA DICTIONARY IN RESOURCE.PY ___________"
        )
        for key, val in data.items():
            logging.warning(f"------------------ {key} : {val}")
        files = dict_fns.unflatten(tuplize_dict(parse_params(request.files)))
        logging.warning(f"THIS IS THE CONTENT OF THE FILES: {files}")
        defaultpath = r"/var/lib/ckan/default"
        folderpath = None
        pathtofolder = None
        pathtofile = None
        if isinstance(files["upload"], list):
            logging.warning(f"---- ---- -- ---- ---- IM ONLY JUST A FOLDER")
            for eachfile in files["upload"]:
                splitFileName = eachfile.filename.split("/")
                # (comment) splitFileName == [""] when the file upload or folder upload is not filled
                if splitFileName == [""]:
                    continue
                if len(splitFileName) > 1:
                    folderpath = defaultpath
                    filepath = defaultpath
                    pathtofolder = os.path.join(defaultpath, splitFileName[0])
                    for i in range(len(splitFileName)):
                        filepath = os.path.join(filepath, splitFileName[i])
                        if i != len(splitFileName) - 1:
                            folderpath = os.path.join(folderpath, splitFileName[i])
                    os.makedirs(folderpath, exist_ok=True)
                    eachfile.save(filepath)
                else:
                    pathtofile = defaultpath + "/temp/"
                    os.makedirs(pathtofile, exist_ok=True)
                    logging.warning(f"split file name: {splitFileName}")
                    filepath = os.path.join(pathtofile, splitFileName[0])
                    logging.warning(f"FILE PATH: {filepath}")
                    if os.path.isdir(filepath):
                        logging.error(f"{filepath} is a directory")
                    else:
                        eachfile.save(filepath)
        logging.warning(f"____-----_____----- printing path to folder: {pathtofolder}")
        logging.warning(f"____-----_____----- printing path to file: {pathtofile}")
        clearml_id = upload_to_clearml(
            pathtofolder,
            pathtofile,
            id,
            package_details["project_title"],
            package_details["dataset_title"],
            parent_ids,
        )

        package_details["clearml_id"] = clearml_id

        package_details = change_dataset_title(package_details)

        get_action("package_update")({}, package_details)
        # we don't want to include save as it is part of the form
        del data["save"]
        try:
            logging.warning(
                f"-- __ -- __ REMOVING UPLOADED FILES FROM CKAN AS IT IS UPLOADED TO CLEARML ALREADY."
            )
            shutil.rmtree(defaultpath)
        except Exception as e:
            logging.warning(
                f"-- __ -- __ UNABLE TO DELETE FOLDER FOR SOME GODFORSAKEN REASON: {e}"
            )
        context = cast(
            Context,
            {
                "model": model,
                "session": model.Session,
                "user": current_user.name,
                "auth_user_obj": current_user,
            },
        )

        # see if we have any data that we are trying to save
        data_provided = False
        for key, value in data.items():
            if (
                value or isinstance(value, cgi.FieldStorage)
            ) and key != "resource_type":
                data_provided = True
                break

        if not data_provided and save_action != "go-dataset-complete":
            if save_action == "go-dataset":
                # go to final stage of adddataset
                return h.redirect_to("{}.edit".format(package_type), id=id)
            # see if we have added any resources
            try:
                data_dict = get_action("package_show")(context, {"id": id})
            except NotAuthorized:
                return base.abort(403, _("Unauthorized to update dataset"))
            except NotFound:
                return base.abort(
                    404, _("The dataset {id} could not be found.").format(id=id)
                )
            if not len(data_dict["resources"]):
                # no data so keep on page
                msg = _("You must add at least one data resource")
                # On new templates do not use flash message

                errors: dict[str, Any] = {}
                error_summary = {_("Error"): msg}
                return self.get(package_type, id, data, errors, error_summary)

            # race condition if another user edits/deletes
            data_dict = get_action("package_show")(context, {"id": id})
            get_action("package_update")(
                cast(Context, dict(context, allow_state_change=True)),
                dict(data_dict, state="active"),
            )
            return h.redirect_to("{}.read".format(package_type), id=id)

        data["package_id"] = id
        if save_action == "go-metadata":
            # race condition if another user edits/deletes
            data_dict = get_action("package_show")(context, {"id": id})
            get_action("package_update")(
                cast(Context, dict(context, allow_state_change=True)),
                dict(data_dict, state="active"),
            )
            return h.redirect_to("{}.read".format(package_type), id=id)
        elif save_action == "go-dataset":
            # go to first stage of add dataset
            return h.redirect_to("{}.edit".format(package_type), id=id)
        elif save_action == "go-dataset-complete":
            return h.redirect_to("{}.read".format(package_type), id=id)
        else:
            # add more resources
            return h.redirect_to("{}_resource.new".format(package_type), id=id)

    def get(
        self,
        package_type: str,
        id: str,
        data: Optional[dict[str, Any]] = None,
        errors: Optional[dict[str, Any]] = None,
        error_summary: Optional[dict[str, Any]] = None,
    ) -> str:
        # get resources for sidebar
        context = cast(
            Context,
            {
                "model": model,
                "session": model.Session,
                "user": current_user.name,
                "auth_user_obj": current_user,
            },
        )
        try:
            pkg_dict = get_action("package_show")(context, {"id": id})
        except NotFound:
            return base.abort(
                404, _("The dataset {id} could not be found.").format(id=id)
            )
        try:
            check_access("resource_create", context, {"package_id": pkg_dict["id"]})
        except NotAuthorized:
            return base.abort(
                403, _("Unauthorized to create a resource for this package")
            )

        package_type = pkg_dict["type"] or package_type

        errors = errors or {}
        error_summary = error_summary or {}
        extra_vars: dict[str, Any] = {
            "data": data,
            "errors": errors,
            "error_summary": error_summary,
            "action": "new",
            "resource_form_snippet": _get_pkg_template("resource_form", package_type),
            "dataset_type": package_type,
            "pkg_name": id,
            "pkg_dict": pkg_dict,
        }
        template = "package/new_resource_not_draft.html"
        if pkg_dict["state"].startswith("draft"):
            extra_vars["stage"] = ["complete", "active"]
            template = "package/new_resource.html"
        return base.render(template, extra_vars)


class EditView(MethodView):
    def _prepare(self, id: str):
        user = current_user.name
        context = cast(
            Context,
            {
                "model": model,
                "session": model.Session,
                "api_version": 3,
                "for_edit": True,
                "user": user,
                "auth_user_obj": current_user,
            },
        )
        try:
            check_access("package_update", context, {"id": id})
        except NotAuthorized:
            return base.abort(403, _("User %r not authorized to edit %s") % (user, id))
        return context

    def post(
        self, package_type: str, id: str, resource_id: str
    ) -> Union[str, Response]:
        context = self._prepare(id)
        data = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(request.form))))
        data.update(
            clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(request.files))))
        )

        # we don't want to include save as it is part of the form
        del data["save"]

        data["package_id"] = id
        try:
            if resource_id:
                data["id"] = resource_id
                get_action("resource_update")(context, data)
            else:
                get_action("resource_create")(context, data)
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.get(package_type, id, resource_id, data, errors, error_summary)
        except NotAuthorized:
            return base.abort(403, _("Unauthorized to edit this resource"))
        return h.redirect_to(
            "{}_resource.read".format(package_type), id=id, resource_id=resource_id
        )

    def get(
        self,
        package_type: str,
        id: str,
        resource_id: str,
        data: Optional[dict[str, Any]] = None,
        errors: Optional[dict[str, Any]] = None,
        error_summary: Optional[dict[str, Any]] = None,
    ) -> str:
        context = self._prepare(id)
        pkg_dict = get_action("package_show")(context, {"id": id})

        try:
            resource_dict = get_action("resource_show")(context, {"id": resource_id})
        except NotFound:
            return base.abort(404, _("Resource not found"))

        if pkg_dict["state"].startswith("draft"):
            return CreateView().get(package_type, id, data=resource_dict)

        # resource is fully created
        resource = resource_dict
        # set the form action
        form_action = h.url_for(
            "{}_resource.edit".format(package_type), resource_id=resource_id, id=id
        )
        if not data:
            data = resource_dict

        package_type = pkg_dict["type"] or package_type

        errors = errors or {}
        error_summary = error_summary or {}
        extra_vars: dict[str, Any] = {
            "data": data,
            "errors": errors,
            "error_summary": error_summary,
            "action": "edit",
            "resource_form_snippet": _get_pkg_template("resource_form", package_type),
            "dataset_type": package_type,
            "resource": resource,
            "pkg_dict": pkg_dict,
            "form_action": form_action,
        }
        return base.render("package/resource_edit.html", extra_vars)


class DeleteView(MethodView):
    def _prepare(self, id: str):
        context = cast(
            Context,
            {
                "model": model,
                "session": model.Session,
                "user": current_user.name,
                "auth_user_obj": current_user,
            },
        )
        try:
            check_access("package_delete", context, {"id": id})
        except NotAuthorized:
            return base.abort(403, _("Unauthorized to delete package %s") % "")
        return context

    def post(self, package_type: str, id: str, resource_id: str) -> Response:
        if "cancel" in request.form:
            return h.redirect_to(
                "{}_resource.edit".format(package_type), resource_id=resource_id, id=id
            )
        context = self._prepare(id)

        try:
            get_action("resource_delete")(context, {"id": resource_id})
            h.flash_notice(_("Resource has been deleted."))
            pkg_dict = get_action("package_show")({}, {"id": id})
            if pkg_dict["state"].startswith("draft"):
                return h.redirect_to("{}_resource.new".format(package_type), id=id)
            else:
                return h.redirect_to("{}.read".format(package_type), id=id)
        except NotAuthorized:
            return base.abort(403, _("Unauthorized to delete resource %s") % "")
        except NotFound:
            return base.abort(404, _("Resource not found"))

    def get(self, package_type: str, id: str, resource_id: str) -> str:
        context = self._prepare(id)
        try:
            resource_dict = get_action("resource_show")(context, {"id": resource_id})
            pkg_id = id
        except NotAuthorized:
            return base.abort(403, _("Unauthorized to delete resource %s") % "")
        except NotFound:
            return base.abort(404, _("Resource not found"))

        # TODO: remove
        g.resource_dict = resource_dict
        g.pkg_id = pkg_id

        return base.render(
            "package/confirm_delete_resource.html",
            {
                "dataset_type": _get_package_type(id),
                "resource_dict": resource_dict,
                "pkg_id": pkg_id,
            },
        )


def views(package_type: str, id: str, resource_id: str) -> str:
    package_type = _get_package_type(id)
    context = cast(
        Context,
        {
            "model": model,
            "session": model.Session,
            "user": current_user.name,
            "for_view": True,
            "auth_user_obj": current_user,
        },
    )
    data_dict = {"id": id}

    try:
        check_access("package_update", context, data_dict)
    except NotAuthorized:
        return base.abort(
            403, _("User %r not authorized to edit %s") % (current_user.name, id)
        )
    # check if package exists
    try:
        pkg_dict = get_action("package_show")(context, data_dict)
        pkg = context["package"]
    except (NotFound, NotAuthorized):
        return base.abort(404, _("Dataset not found"))

    try:
        resource = get_action("resource_show")(context, {"id": resource_id})
        views = get_action("resource_view_list")(context, {"id": resource_id})

    except NotFound:
        return base.abort(404, _("Resource not found"))
    except NotAuthorized:
        return base.abort(403, _("Unauthorized to read resource %s") % id)

    _setup_template_variables(context, {"id": id}, package_type=package_type)

    # TODO: remove
    g.pkg_dict = pkg_dict
    g.pkg = pkg
    g.resource = resource
    g.views = views

    return base.render(
        "package/resource_views.html",
        {"pkg_dict": pkg_dict, "pkg": pkg, "resource": resource, "views": views},
    )


def view(
    package_type: str, id: str, resource_id: str, view_id: Optional[str] = None
) -> str:
    """
    Embedded page for a resource view.

    Depending on the type, different views are loaded. This could be an
    img tag where the image is loaded directly or an iframe that embeds a
    webpage or another preview.
    """
    context = cast(
        Context,
        {
            "model": model,
            "session": model.Session,
            "user": current_user.name,
            "auth_user_obj": current_user,
        },
    )

    try:
        package = get_action("package_show")(context, {"id": id})
    except (NotFound, NotAuthorized):
        return base.abort(404, _("Dataset not found"))

    try:
        resource = get_action("resource_show")(context, {"id": resource_id})
    except (NotFound, NotAuthorized):
        return base.abort(404, _("Resource not found"))

    view = None
    if request.args.get("resource_view", ""):
        try:
            view = json.loads(request.args.get("resource_view", ""))
        except ValueError:
            return base.abort(409, _("Bad resource view data"))
    elif view_id:
        try:
            view = get_action("resource_view_show")(context, {"id": view_id})
        except (NotFound, NotAuthorized):
            return base.abort(404, _("Resource view not found"))

    if not view or not isinstance(view, dict):
        return base.abort(404, _("Resource view not supplied"))

    return h.rendered_resource_view(view, resource, package, embed=True)


# FIXME: could anyone think about better name?
class EditResourceViewView(MethodView):
    def _prepare(self, id: str, resource_id: str) -> tuple[Context, dict[str, Any]]:
        user = current_user.name
        context = cast(
            Context,
            {
                "model": model,
                "session": model.Session,
                "user": user,
                "for_view": True,
                "auth_user_obj": current_user,
            },
        )

        # update resource should tell us early if the user has privilages.
        try:
            check_access("resource_update", context, {"id": resource_id})
        except NotAuthorized:
            return base.abort(403, _("User %r not authorized to edit %s") % (user, id))

        # get resource and package data
        try:
            pkg_dict = get_action("package_show")(context, {"id": id})
            pkg = context["package"]
        except (NotFound, NotAuthorized):
            return base.abort(404, _("Dataset not found"))
        try:
            resource = get_action("resource_show")(context, {"id": resource_id})
        except (NotFound, NotAuthorized):
            return base.abort(404, _("Resource not found"))

        # TODO: remove
        g.pkg_dict = pkg_dict
        g.pkg = pkg
        g.resource = resource

        extra_vars: dict[str, Any] = dict(
            data={},
            errors={},
            error_summary={},
            view_type=None,
            to_preview=False,
            pkg_dict=pkg_dict,
            pkg=pkg,
            resource=resource,
        )
        return context, extra_vars

    def post(
        self,
        package_type: str,
        id: str,
        resource_id: str,
        view_id: Optional[str] = None,
    ) -> Union[str, Response]:
        context, extra_vars = self._prepare(id, resource_id)
        data = clean_dict(
            dict_fns.unflatten(
                tuplize_dict(parse_params(request.form, ignore_keys=CACHE_PARAMETERS))
            )
        )
        data.pop("save", None)

        to_preview = data.pop("preview", False)
        if to_preview:
            context["preview"] = True
        to_delete = data.pop("delete", None)
        data["resource_id"] = resource_id
        data["view_type"] = request.args.get("view_type")

        try:
            if to_delete:
                data["id"] = view_id
                get_action("resource_view_delete")(context, data)
            elif view_id:
                data["id"] = view_id
                data = get_action("resource_view_update")(context, data)
            else:
                data = get_action("resource_view_create")(context, data)
        except ValidationError as e:
            # Could break preview if validation error
            to_preview = False
            extra_vars["errors"] = e.error_dict
            extra_vars["error_summary"] = e.error_summary
        except NotAuthorized:
            # This should never happen unless the user maliciously changed
            # the resource_id in the url.
            return base.abort(403, _("Unauthorized to edit resource"))
        else:
            if not to_preview:
                return h.redirect_to(
                    "{}_resource.views".format(package_type),
                    id=id,
                    resource_id=resource_id,
                )
        extra_vars["data"] = data
        extra_vars["to_preview"] = to_preview
        return self.get(package_type, id, resource_id, view_id, extra_vars)

    def get(
        self,
        package_type: str,
        id: str,
        resource_id: str,
        view_id: Optional[str] = None,
        post_extra: Optional[dict[str, Any]] = None,
    ) -> str:
        context, extra_vars = self._prepare(id, resource_id)
        to_preview = extra_vars["to_preview"]
        if post_extra:
            extra_vars.update(post_extra)

        package_type = _get_package_type(id)
        data = extra_vars["data"] if "data" in extra_vars else None

        if data and "view_type" in data:
            view_type = data.get("view_type")
        else:
            view_type = request.args.get("view_type")

        # view_id exists only when updating
        if view_id:
            if not data or not view_type:
                try:
                    view_data = get_action("resource_view_show")(
                        context, {"id": view_id}
                    )
                    view_type = view_data["view_type"]
                    if data:
                        data.update(view_data)
                    else:
                        data = view_data
                except (NotFound, NotAuthorized):
                    return base.abort(404, _("View not found"))

            # might as well preview when loading good existing view
            if not extra_vars["errors"]:
                to_preview = True

        if data is not None:
            data["view_type"] = view_type
        view_plugin = lib_datapreview.get_view_plugin(view_type)
        if not view_plugin:
            return base.abort(404, _("View Type Not found"))

        _setup_template_variables(context, {"id": id}, package_type=package_type)

        data_dict: dict[str, Any] = {
            "package": extra_vars["pkg_dict"],
            "resource": extra_vars["resource"],
            "resource_view": data,
        }

        view_template = view_plugin.view_template(context, data_dict)
        form_template = view_plugin.form_template(context, data_dict)

        extra_vars.update(
            {
                "form_template": form_template,
                "view_template": view_template,
                "data": data,
                "to_preview": to_preview,
                "datastore_available": plugins.plugin_loaded("datastore"),
            }
        )
        extra_vars.update(
            view_plugin.setup_template_variables(context, data_dict) or {}
        )
        extra_vars.update(data_dict)

        if view_id:
            return base.render("package/edit_view.html", extra_vars)

        return base.render("package/new_view.html", extra_vars)


def register_dataset_plugin_rules(blueprint: Blueprint) -> None:
    logging.warning(f"ORIGINAL RESOURCE.PY REGISTERING BLUEPRINT")
    blueprint.add_url_rule("/new", view_func=CreateView.as_view(str("new")))
    blueprint.add_url_rule("/<resource_id>", view_func=read, strict_slashes=False)
    blueprint.add_url_rule(
        "/<resource_id>/edit", view_func=EditView.as_view(str("edit"))
    )
    blueprint.add_url_rule(
        "/<resource_id>/delete", view_func=DeleteView.as_view(str("delete"))
    )

    blueprint.add_url_rule("/<resource_id>/download", view_func=download)
    blueprint.add_url_rule("/<resource_id>/views", view_func=views)
    blueprint.add_url_rule("/<resource_id>/view", view_func=view)
    blueprint.add_url_rule("/<resource_id>/view/<view_id>", view_func=view)
    blueprint.add_url_rule("/<resource_id>/download/<filename>", view_func=download)

    _edit_view: Any = EditResourceViewView.as_view(str("edit_view"))
    blueprint.add_url_rule("/<resource_id>/new_view", view_func=_edit_view)
    blueprint.add_url_rule("/<resource_id>/edit_view/<view_id>", view_func=_edit_view)
    # for key,  val in blueprint.__dict__.items():
    #     logging.warning(f"------_______----- {key} : {val}")


register_dataset_plugin_rules(resource)
register_dataset_plugin_rules(prefixed_resource)
# remove this when we improve blueprint registration to be explicit:
resource.auto_register = False  # type: ignore
