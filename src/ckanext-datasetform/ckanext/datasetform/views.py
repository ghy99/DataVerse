# encoding: utf-8
from __future__ import annotations

import logging
import inspect
from collections import OrderedDict
from functools import partial
from typing_extensions import TypeAlias
from urllib.parse import urlencode
from typing import Any, Iterable, Optional, Union, cast

from flask import Blueprint
from flask.views import MethodView
from jinja2.exceptions import TemplateNotFound
from werkzeug.datastructures import MultiDict
from ckan.common import asbool, current_user

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.model as model
import ckan.plugins as plugins
import ckan.authz as authz
from ckan.common import _, config, g, request
from ckan.views.home import CACHE_PARAMETERS
from ckan.lib.plugins import lookup_package_plugin
from ckan.lib.search import SearchError, SearchQueryError, SearchIndexError
from ckan.types import Context, Response

class OverwritePackageView(MethodView):
    
    def post(self, package_type: str) -> Union[Response, str]:
        # The staged add dataset used the new functionality when the dataset is
        # partially created so we need to know if we actually are updating or
        # this is a real new.
        context = self._prepare()
        is_an_update = False
        ckan_phase = request.form.get(u'_ckan_phase')
        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
            )
        except dict_fns.DataError:
            return base.abort(400, _(u'Integrity Error'))
        try:
            if ckan_phase:
                # prevent clearing of groups etc
                context[u'allow_partial_update'] = True
                # sort the tags
                if u'tag_string' in data_dict:
                    data_dict[u'tags'] = _tag_string_to_list(
                        data_dict[u'tag_string']
                    )
                if data_dict.get(u'pkg_name'):
                    is_an_update = True
                    # This is actually an update not a save
                    data_dict[u'id'] = data_dict[u'pkg_name']
                    del data_dict[u'pkg_name']
                    # don't change the dataset state
                    data_dict[u'state'] = u'draft'
                    # this is actually an edit not a save
                    pkg_dict = get_action(u'package_update')(
                        context, data_dict
                    )

                    # redirect to add dataset resources
                    url = h.url_for(
                        u'{}_resource.new'.format(package_type),
                        id=pkg_dict[u'name']
                    )
                    return h.redirect_to(url)
                # Make sure we don't index this dataset
                if request.form[u'save'] not in [
                    u'go-resource', u'go-metadata'
                ]:
                    data_dict[u'state'] = u'draft'
                # allow the state to be changed
                context[u'allow_state_change'] = True

            data_dict[u'type'] = package_type
            pkg_dict = get_action(u'package_create')(context, data_dict)

            # create_on_ui_requires_resources = config.get(
            #     'ckan.dataset.create_on_ui_requires_resources'
            # )
            new_or_existing = pkg_dict["new_or_existing"]
            if ckan_phase:
                if new_or_existing == "Add New Dataset":
                    # redirect to add dataset resources if
                    # create_on_ui_requires_resources is set to true
                    logging.warning(f"THIS IS ADDING A NEW DATASET!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    url = h.url_for(
                        u'{}_resource.new'.format(package_type),
                        id=pkg_dict[u'name']
                    )
                    return h.redirect_to(url)
                logging.warning(f"THIS IS REFERENCING FROM CLEARMLLLLLLLLLLLLLLLLLLLLLLLLLL")
                get_action(u'package_update')(
                    cast(Context, dict(context, allow_state_change=True)),
                    dict(pkg_dict, state=u'active')
                )
                logging.warning(f"TRYING TO REDIRECT NOW!!!!!!!!!!!!!!!!!!!")
                return h.redirect_to(
                    u'{}.read'.format(package_type),
                    id=pkg_dict["id"]
                )

            return _form_save_redirect(
                pkg_dict[u'name'], u'new', package_type=package_type
            )
            
        except NotAuthorized:
            return base.abort(403, _(u'Unauthorized to read package'))
        except NotFound:
            return base.abort(404, _(u'Dataset not found'))
        except SearchIndexError as e:
            try:
                exc_str = str(repr(e.args))
            except Exception:  # We don't like bare excepts
                exc_str = str(str(e))
            return base.abort(
                500,
                _(u'Unable to add package to search index.') + exc_str
            )
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            if is_an_update:
                # we need to get the state of the dataset to show the stage we
                # are on.
                pkg_dict = get_action(u'package_show')(context, data_dict)
                data_dict[u'state'] = pkg_dict[u'state']
                return EditView().get(
                    package_type,
                    data_dict[u'id'],
                    data_dict,
                    errors,
                    error_summary
                )
            data_dict[u'state'] = u'none'
            return self.get(package_type, data_dict, errors, error_summary)