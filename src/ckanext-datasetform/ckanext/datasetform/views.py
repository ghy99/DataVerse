# encoding: utf-8
from __future__ import annotations

import logging
import inspect
from typing import Any, Optional, Union, cast

import cgi
from flask.views import MethodView
from ckan.common import current_user

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.model as model
from ckan.common import _, config, g, request
from ckan.views.home import CACHE_PARAMETERS
from ckan.lib.plugins import lookup_package_plugin
from ckan.lib.search import SearchIndexError
from ckan.types import Context, Response

import os
from werkzeug.datastructures import FileStorage

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


def _setup_template_variables(
    context: Context, data_dict: dict[str, Any], package_type: Optional[str] = None
) -> None:
    return lookup_package_plugin(package_type).setup_template_variables(
        context, data_dict
    )


def _get_pkg_template(template_type: str, package_type: Optional[str] = None) -> str:
    pkg_plugin = lookup_package_plugin(package_type)
    method = getattr(pkg_plugin, template_type)
    signature = inspect.signature(method)
    if len(signature.parameters):
        return method(package_type)
    else:
        return method()


def _tag_string_to_list(tag_string: str) -> list[dict[str, str]]:
    """This is used to change tags from a sting to a list of dicts."""
    out: list[dict[str, str]] = []
    for tag in tag_string.split(","):
        tag = tag.strip()
        if tag:
            out.append({"name": tag, "state": "active"})
    return out


def _form_save_redirect(
    pkg_name: str, action: str, package_type: Optional[str] = None
) -> Response:
    """This redirects the user to the CKAN package/read page,
    unless there is request parameter giving an alternate location,
    perhaps an external website.
    @param pkg_name - Name of the package just edited
    @param action - What the action of the edit was
    """
    assert action in ("new", "edit")
    url = request.args.get("return_to") or config.get(
        "package_%s_return_url" % action)
    if url:
        url = url.replace("<NAME>", pkg_name)
    else:
        if not package_type:
            package_type = "dataset"
        url = h.url_for("{0}.read".format(package_type), id=pkg_name)
    return h.redirect_to(url)


def _get_package_type(id: str) -> str:
    """
    Given the id of a package this method will return the type of the
    package, or 'dataset' if no type is currently set
    """
    pkg = model.Package.get(id)
    if pkg:
        return pkg.type or "dataset"
    return "dataset"

# dataset.py
# For Package Form
class CreatePackageView(MethodView):
    def _is_save(self) -> bool:
        return "save" in request.form

    def _prepare(self) -> Context:  # noqa
        context = cast(
            Context,
            {
                "model": model,
                "session": model.Session,
                "user": current_user.name,
                "auth_user_obj": current_user,
                "save": self._is_save(),
            },
        )
        try:
            check_access("package_create", context)
        except NotAuthorized:
            return base.abort(403, _("Unauthorized to create a package"))
        return context

    def post(self, package_type: str) -> Union[Response, str]:
        # The staged add dataset used the new functionality when the dataset is
        # partially created so we need to know if we actually are updating or
        # this is a real new.
        context = self._prepare()
        is_an_update = False
        ckan_phase = request.form.get("_ckan_phase")
        try:
            data_dict = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.form))))
            logging.warning(
                f"-- ---- ---- IM GONNA TRY SMTH HERE PLS WORK ---- ---- --")
            files = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.files))))

            # logging.warning(f"-- ---- ---- FILES: {files} --------------------------------------")
            data_dict.update(files)

        except dict_fns.DataError:
            return base.abort(400, _("Integrity Error"))
        
        logging.warning(f" - - - -  -- -- -- PRINTING DATA DICT IN VIEWS.PY")
        for key, val in data_dict.items():
            logging.warning(f"-- -- -- - -- -- {key} : {val}")

        try:
            if ckan_phase:
                # prevent clearing of groups etc
                context["allow_partial_update"] = True
                # sort the tags
                if "tag_string" in data_dict:
                    data_dict["tags"] = _tag_string_to_list(
                        data_dict["tag_string"])
                if data_dict.get("pkg_name"):
                    is_an_update = True
                    # This is actually an update not a save
                    data_dict["id"] = data_dict["pkg_name"]
                    del data_dict["pkg_name"]
                    # don't change the dataset state
                    data_dict["state"] = "draft"
                    # this is actually an edit not a save
                    pkg_dict = get_action("package_update")(context, data_dict)

                    # redirect to add dataset resources
                    url = h.url_for(
                        "{}_resource.new".format(package_type), id=pkg_dict["name"]
                    )
                    return h.redirect_to(url)
                # Make sure we don't index this dataset
                if request.form["save"] not in ["go-resource", "go-metadata"]:
                    data_dict["state"] = "draft"
                # allow the state to be changed
                context["allow_state_change"] = True

            data_dict["type"] = package_type

            logging.warning(f"---------- VIEWS.PY ----------")
            for key, val in data_dict.items():
                logging.warning(f" --- --- --- --- {key} : {val}")

            pkg_dict = get_action("package_create")(context, data_dict)

            logging.warning(
                f"--- -- ---- - IM GONNA TRY CREATING RESOURCE HERE")
            resource = get_action(f"resource_create")({}, {
                "package_id": pkg_dict["id"],
                "upload": data_dict['upload'],
                'preview': True, 
                "format" : "",

            })

            logging.warning(
                f"- ---- -- --- - I AM AT VIEWS.PY LINE 192 -------------------------------------------")
            logging.warning(
                f"- ---- -- --- - PRINTING RESOURCE FROM LINE 186 -------------------------------------")

            for key, val in resource.items():
                logging.warning(f"- --- ---- --- {key} : {val}")

            pkg_dict['resources'].append(resource)
            # pkg_dict['resources'] = [{
            #     "format": resource['format'],
            #     "url": resource['url'],
            #     "url_type": resource['url_type'],
            #     "package_id": pkg_dict['name'] or pkg_dict['id'],
            #     "name": resource['name'],
            #     "last_modified": resource['last_modified'],
            #     "mimetype": resource['mimetype'],
            #     "size": resource['size'],
            #     "id" : resource['id']
            #     # "preview" : True,
            # }]
            pkg_dict = get_action("package_update")({}, pkg_dict)

            logging.warning(
                f"- ---- -- --- - PRINTING RESOURCE FROM LINE 213 -------------------------------------")

            for key, val in pkg_dict.items():
                logging.warning(f"- --- ---- --- {key} : {val}")

            # create_on_ui_requires_resources = config.get(
            #     'ckan.dataset.create_on_ui_requires_resources'
            # )
            logging.warning(
                f"-----------------PRINTING PKG DICT: NEW OR EXISTING: {pkg_dict['new_or_existing']}"
            )
            new_or_existing = pkg_dict["new_or_existing"]
            if ckan_phase:
                if new_or_existing == "Add New Dataset":
                    # redirect to add dataset resources if
                    # create_on_ui_requires_resources is set to true
                    logging.warning(
                        f"THIS IS ADDING A NEW DATASET!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                    )
                    url = h.url_for(
                        "{}_resource.new".format(package_type), id=pkg_dict["name"]
                    )
                    return h.redirect_to(url)
                logging.warning(
                    f"THIS IS REFERENCING FROM CLEARMLLLLLLLLLLLLLLLLLLLLLLLLLL"
                )
                get_action("package_update")(
                    cast(Context, dict(context, allow_state_change=True)),
                    dict(pkg_dict, state="active"),
                )
                logging.warning(f"TRYING TO REDIRECT NOW!!!!!!!!!!!!!!!!!!!")
                return h.redirect_to("{}.read".format(package_type), id=pkg_dict["id"])

            return _form_save_redirect(
                pkg_dict["name"], "new", package_type=package_type
            )

        except NotAuthorized:
            return base.abort(403, _("Unauthorized to read package"))
        except NotFound:
            return base.abort(404, _("Dataset not found"))
        except SearchIndexError as e:
            try:
                exc_str = str(repr(e.args))
            except Exception:  # We don't like bare excepts
                exc_str = str(str(e))
            return base.abort(
                500, _("Unable to add package to search index.") + exc_str
            )
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            if is_an_update:
                # we need to get the state of the dataset to show the stage we
                # are on.
                pkg_dict = get_action("package_show")(context, data_dict)
                data_dict["state"] = pkg_dict["state"]
                return EditPackageView().get(
                    package_type, data_dict["id"], data_dict, errors, error_summary
                )
            data_dict["state"] = "none"
            return self.get(package_type, data_dict, errors, error_summary)

    def get(
        self,
        package_type: str,
        data: Optional[dict[str, Any]] = None,
        errors: Optional[dict[str, Any]] = None,
        error_summary: Optional[dict[str, Any]] = None,
    ) -> str:
        context = self._prepare()
        if data and "type" in data:
            package_type = data["type"]

        data = data or clean_dict(
            dict_fns.unflatten(
                tuplize_dict(parse_params(
                    request.args, ignore_keys=CACHE_PARAMETERS))
            )
        )
        resources_json = h.json.dumps(data.get("resources", []))
        # convert tags if not supplied in data
        if data and not data.get("tag_string"):
            data["tag_string"] = ", ".join(
                h.dict_list_reduce(data.get("tags", {}), "name")
            )

        errors = errors or {}
        error_summary = error_summary or {}
        # in the phased add dataset we need to know that
        # we have already completed stage 1
        stage = ["active"]
        if data.get("state", "").startswith("draft"):
            stage = ["active", "complete"]

        # if we are creating from a group then this allows the group to be
        # set automatically
        data["group_id"] = request.args.get("group") or request.args.get(
            "groups__0__id"
        )

        form_snippet = _get_pkg_template(
            "package_form", package_type=package_type)
        form_vars: dict[str, Any] = {
            "data": data,
            "errors": errors,
            "error_summary": error_summary,
            "action": "new",
            "stage": stage,
            "dataset_type": package_type,
            "form_style": "new",
        }
        errors_json = h.json.dumps(errors)

        # TODO: remove
        g.resources_json = resources_json
        g.errors_json = errors_json

        _setup_template_variables(context, {}, package_type=package_type)

        new_template = _get_pkg_template("new_template", package_type)
        return base.render(
            new_template,
            extra_vars={
                "form_vars": form_vars,
                "form_snippet": form_snippet,
                "dataset_type": package_type,
                "resources_json": resources_json,
                "form_snippet": form_snippet,
                "errors_json": errors_json,
            },
        )


class EditPackageView(MethodView):
    def _is_save(self) -> bool:
        return "save" in request.form

    def _prepare(self) -> Context:  # noqa
        context = cast(
            Context,
            {
                "model": model,
                "session": model.Session,
                "user": current_user.name,
                "auth_user_obj": current_user,
                "save": self._is_save(),
            },
        )
        try:
            check_access("package_create", context)
        except NotAuthorized:
            return base.abort(403, _("Unauthorized to create a package"))
        return context

    def post(self, package_type: str, id: str) -> Union[Response, str]:
        context = self._prepare()
        package_type = _get_package_type(id) or package_type
        log.debug("Package save request name: %s POST: %r", id, request.form)
        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
            )
        except dict_fns.DataError:
            return base.abort(400, _("Integrity Error"))
        try:
            if "_ckan_phase" in data_dict:
                # we allow partial updates to not destroy existing resources
                context["allow_partial_update"] = True
                if "tag_string" in data_dict:
                    data_dict["tags"] = _tag_string_to_list(
                        data_dict["tag_string"])
                del data_dict["_ckan_phase"]
                del data_dict["save"]
            data_dict["id"] = id
            pkg_dict = get_action("package_update")(context, data_dict)

            return _form_save_redirect(
                pkg_dict["name"], "edit", package_type=package_type
            )
        except NotAuthorized:
            return base.abort(403, _("Unauthorized to read package %s") % id)
        except NotFound:
            return base.abort(404, _("Dataset not found"))
        except SearchIndexError as e:
            try:
                exc_str = str(repr(e.args))
            except Exception:  # We don't like bare excepts
                exc_str = str(str(e))
            return base.abort(500, _("Unable to update search index.") + exc_str)
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.get(package_type, id, data_dict, errors, error_summary)

    def get(
        self,
        package_type: str,
        id: str,
        data: Optional[dict[str, Any]] = None,
        errors: Optional[dict[str, Any]] = None,
        error_summary: Optional[dict[str, Any]] = None,
    ) -> Union[Response, str]:
        context = self._prepare()
        package_type = _get_package_type(id) or package_type
        try:
            view_context = context.copy()
            view_context["for_view"] = True
            pkg_dict = get_action("package_show")(view_context, {"id": id})
            context["for_edit"] = True
            old_data = get_action("package_show")(context, {"id": id})
            # old data is from the database and data is passed from the
            # user if there is a validation error. Use users data if there.
            if data:
                old_data.update(data)
            data = old_data
        except (NotFound, NotAuthorized):
            return base.abort(404, _("Dataset not found"))
        assert data is not None
        # are we doing a multiphase add?
        if data.get("state", "").startswith("draft"):
            g.form_action = h.url_for("{}.new".format(package_type))
            g.form_style = "new"

            return CreateView().get(
                package_type, data=data, errors=errors, error_summary=error_summary
            )

        pkg = context.get("package")
        resources_json = h.json.dumps(data.get("resources", []))
        user = current_user.name
        try:
            check_access("package_update", context)
        except NotAuthorized:
            return base.abort(403, _("User %r not authorized to edit %s") % (user, id))
        # convert tags if not supplied in data
        if data and not data.get("tag_string"):
            data["tag_string"] = ", ".join(
                h.dict_list_reduce(pkg_dict.get("tags", {}), "name")
            )
        errors = errors or {}
        form_snippet = _get_pkg_template(
            "package_form", package_type=package_type)
        form_vars: dict[str, Any] = {
            "data": data,
            "errors": errors,
            "error_summary": error_summary,
            "action": "edit",
            "dataset_type": package_type,
            "form_style": "edit",
        }
        errors_json = h.json.dumps(errors)

        # TODO: remove
        g.pkg = pkg
        g.resources_json = resources_json
        g.errors_json = errors_json

        _setup_template_variables(
            context, {"id": id}, package_type=package_type)

        # we have already completed stage 1
        form_vars["stage"] = ["active"]
        if data.get("state", "").startswith("draft"):
            form_vars["stage"] = ["active", "complete"]

        edit_template = _get_pkg_template("edit_template", package_type)
        return base.render(
            edit_template,
            extra_vars={
                "form_vars": form_vars,
                "form_snippet": form_snippet,
                "dataset_type": package_type,
                "pkg_dict": pkg_dict,
                "pkg": pkg,
                "resources_json": resources_json,
                "form_snippet": form_snippet,
                "errors_json": errors_json,
            },
        )

# resource.py
# For Resource Form
class CreateResourceView(MethodView):
    def post(self, package_type: str, id: str) -> Union[str, Response]:
        logging.warning("__________________________________________________________________________")
        logging.warning("THIS IS THE FIRST LINE OF POST IN RESOURCE")
        save_action = request.form.get(u'save')
        data = clean_dict(
            dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
        )
        files = dict_fns.unflatten(tuplize_dict(parse_params(request.files)))
        defaultpath = r"/var/lib/ckan/default"
        if isinstance(files['upload'], list):
            logging.warning(f"---- ---- -- ---- ---- IM ONLY JUST A FOLDER")
            for eachfile in files['upload']:
                splitFileName = eachfile.filename.split("/")
                logging.warning(f"split file name: {splitFileName}")
                folderpath = os.path.join(defaultpath, splitFileName[0])
                os.makedirs(folderpath, exist_ok=True)
                # logging.warning(f"---- ---- -- ---- ---- IM ONLY JUST A SINGLE FILE {dest}")
                logging.warning(f"------- ---- {eachfile.filename}, type : {type(eachfile.filename)}")
                filepath = os.path.join(folderpath, splitFileName[1])
                logging.warning(f"FILE PATH: {filepath}")
                eachfile.save(filepath)
                # files['upload'].remove(eachfile)
        elif isinstance(files['upload'], FileStorage):
            splitFileName = files['upload'].filename.split("/")
            logging.warning(f"split file name: {splitFileName}")
            folderpath = os.path.join(defaultpath, splitFileName[0])
            os.makedirs(folderpath, exist_ok=True)
            # logging.warning(f"---- ---- -- ---- ---- IM ONLY JUST A SINGLE FILE {dest}")
            logging.warning(f"------- ---- {files['upload'].filename}, type : {type(files['upload'].filename)}")
            filepath = os.path.join(folderpath, splitFileName[1])
            logging.warning(f"FILE PATH: {filepath}")
            files['upload'].save(filepath)
        del files['upload']
            # for eachFile in files['upload'] :
            #     temp.append({
            #         'key' : 'upload', 'value' : eachFile
            #     })
            # files['upload'] = temp
        # if files['upload']:
        logging.warning(f"FILLLLLLEEEEEEEEEEEEESSSSSSSSSSSSSSSSSSSSSSSS: ")
        logging.warning(f" ---------- ---------- ----- {files}")
        data.update(clean_dict(files))
        logging.warning(f"- - - - - - - - - - RESOURCE.PY")
        logging.warning(f"- - - - - - - - - - what does resource form send?")
        for key, val in data.items():
            logging.warning(f"- - - - - {key} : {val}")
        # we don't want to include save as it is part of the form
        del data[u'save']
        resource_id = data.pop(u'id')

        context = cast(Context, {
            u'model': model,
            u'session': model.Session,
            u'user': current_user.name,
            u'auth_user_obj': current_user
        })

        # see if we have any data that we are trying to save
        data_provided = False
        for key, value in data.items():
            if (
                    (value or isinstance(value, cgi.FieldStorage))
                    and key != u'resource_type'):
                data_provided = True
                break

        if not data_provided and save_action != u"go-dataset-complete":
            if save_action == u'go-dataset':
                # go to final stage of adddataset
                return h.redirect_to(u'{}.edit'.format(package_type), id=id)
            # see if we have added any resources
            try:
                data_dict = get_action(u'package_show')(context, {u'id': id})
            except NotAuthorized:
                return base.abort(403, _(u'Unauthorized to update dataset'))
            except NotFound:
                return base.abort(
                    404,
                    _(u'The dataset {id} could not be found.').format(id=id)
                )
            if not len(data_dict[u'resources']):
                # no data so keep on page
                msg = _(u'You must add at least one data resource')
                # On new templates do not use flash message

                errors: dict[str, Any] = {}
                error_summary = {_(u'Error'): msg}
                return self.get(package_type, id, data, errors, error_summary)

            # race condition if another user edits/deletes
            data_dict = get_action(u'package_show')(context, {u'id': id})
            get_action(u'package_update')(
                cast(Context, dict(context, allow_state_change=True)),
                dict(data_dict, state=u'active')
            )
            return h.redirect_to(u'{}.read'.format(package_type), id=id)

        data[u'package_id'] = id
        try:
            if resource_id:
                data[u'id'] = resource_id
                get_action(u'resource_update')(context, data)
            else:
                get_action(u'resource_create')(context, data)
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            if data.get(u'url_type') == u'upload' and data.get(u'url'):
                data[u'url'] = u''
                data[u'url_type'] = u''
                data[u'previous_upload'] = True
            return self.get(package_type, id, data, errors, error_summary)
        except NotAuthorized:
            return base.abort(403, _(u'Unauthorized to create a resource'))
        except NotFound:
            return base.abort(
                404, _(u'The dataset {id} could not be found.').format(id=id)
            )
        if save_action == u'go-metadata':
            # race condition if another user edits/deletes
            data_dict = get_action(u'package_show')(context, {u'id': id})
            get_action(u'package_update')(
                cast(Context, dict(context, allow_state_change=True)),
                dict(data_dict, state=u'active')
            )
            return h.redirect_to(u'{}.read'.format(package_type), id=id)
        elif save_action == u'go-dataset':
            # go to first stage of add dataset
            return h.redirect_to(u'{}.edit'.format(package_type), id=id)
        elif save_action == u'go-dataset-complete':

            return h.redirect_to(u'{}.read'.format(package_type), id=id)
        else:
            # add more resources
            return h.redirect_to(
                u'{}_resource.new'.format(package_type),
                id=id
            )

    def get(self,
            package_type: str,
            id: str,
            data: Optional[dict[str, Any]] = None,
            errors: Optional[dict[str, Any]] = None,
            error_summary: Optional[dict[str, Any]] = None) -> str:
        # get resources for sidebar
        context = cast(Context, {
            u'model': model,
            u'session': model.Session,
            u'user': current_user.name,
            u'auth_user_obj': current_user
        })
        try:
            pkg_dict = get_action(u'package_show')(context, {u'id': id})
        except NotFound:
            return base.abort(
                404, _(u'The dataset {id} could not be found.').format(id=id)
            )
        try:
            check_access(
                u'resource_create', context, {u"package_id": pkg_dict["id"]}
            )
        except NotAuthorized:
            return base.abort(
                403, _(u'Unauthorized to create a resource for this package')
            )

        package_type = pkg_dict[u'type'] or package_type

        errors = errors or {}
        error_summary = error_summary or {}
        extra_vars: dict[str, Any] = {
            u'data': data,
            u'errors': errors,
            u'error_summary': error_summary,
            u'action': u'new',
            u'resource_form_snippet': _get_pkg_template(
                u'resource_form', package_type
            ),
            u'dataset_type': package_type,
            u'pkg_name': id,
            u'pkg_dict': pkg_dict
        }
        template = u'package/new_resource_not_draft.html'
        if pkg_dict[u'state'].startswith(u'draft'):
            extra_vars[u'stage'] = ['complete', u'active']
            template = u'package/new_resource.html'
        return base.render(template, extra_vars)

