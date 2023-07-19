# encoding: utf-8
from __future__ import annotations

from typing import Any, Optional
from ckan.types import AuthResult, Context
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def group_update(
        context: Context,
        data_dict: Optional[dict[str, Any]] = None) -> AuthResult:
    return {'success': True}

class IauthfunctionPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "iauthfunction")

    # IAuthFunction

    def get_auth_functions(self):
        return {'group_update': group_update}
