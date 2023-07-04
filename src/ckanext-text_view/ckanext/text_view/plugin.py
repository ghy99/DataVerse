
from ckan.types import Context
import logging
from typing import Any

from ckan.common import CKANConfig, json
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.resourceproxy.plugin as proxy
import ckan.lib.datapreview as datapreview

log = logging.getLogger(__name__)

def get_formats(config: CKANConfig) -> dict[str, list[str]]:
    out = {}

    out["text_formats"] = config.get(
        "ckan.preview.text_formats"
    ).split()
    out["xml_formats"] = config.get("ckan.preview.xml_formats").split()
    out["json_formats"] = config.get(
        "ckan.preview.json_formats"
    ).split()
    out["jsonp_formats"] = config.get(
        "ckan.preview.jsonp_formats"
    ).split()

    return out

@plugins.toolkit.blanket.config_declarations
class TextViewPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)

    proxy_is_enabled = False
    text_formats = []
    xml_formats = []
    json_formats = []
    jsonp_formats = []
    no_jsonp_formats = []
    

    # IConfigurer

    def update_config(self, config_):
        formats = get_formats(config_)
        for key, value in formats.items():
            setattr(self, key, value)

        self.no_jsonp_formats = (self.text_formats +
                                 self.xml_formats +
                                 self.json_formats)
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "text_view")

    # IResourceView

    def info(self):
        return {'name': 'text_view',
                'title': plugins.toolkit._('Text'),
                'icon': 'file-lines',
                'default_title': plugins.toolkit._('Text'),
                }

    def can_view(self, data_dict: dict[str, Any]):
        resource = data_dict['resource']
        format_lower = resource.get('format', '').lower()
        proxy_enabled = plugins.plugin_loaded('resource_proxy')
        same_domain = datapreview.on_same_domain(data_dict)
        if format_lower in self.jsonp_formats:
            return True
        if format_lower in self.no_jsonp_formats:
            return proxy_enabled or same_domain
        return False

    def setup_template_variables(self, context: Context,
                                 data_dict: dict[str, Any]):
        metadata = {'text_formats': self.text_formats,
                    'json_formats': self.json_formats,
                    'jsonp_formats': self.jsonp_formats,
                    'xml_formats': self.xml_formats}

        url = proxy.get_proxified_resource_url(data_dict)
        format_lower = data_dict['resource']['format'].lower()
        if format_lower in self.jsonp_formats:
            url = data_dict['resource']['url']

        return {'preview_metadata': json.dumps(metadata),
                'resource_json': json.dumps(data_dict['resource']),
                'resource_url': json.dumps(url)}

    def view_template(self, context: Context, data_dict: dict[str, Any]):
        return 'text_view.html'

    def form_template(self, context: Context, data_dict: dict[str, Any]):
        return 'text_form.html'
