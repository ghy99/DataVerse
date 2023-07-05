# encoding: utf-8
from __future__ import annotations

from ckan.types import Context
from typing import Any
from ckan.common import CKANConfig
import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


log = logging.getLogger(__name__)
ignore_empty = plugins.toolkit.get_validator('ignore_empty')
unicode_safe = plugins.toolkit.get_validator('unicode_safe')


@plugins.toolkit.blanket.config_declarations
class ImageViewPlugin(plugins.SingletonPlugin):
    '''This plugin makes views of image resources, using an <img> tag'''

    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "theme/templates")
        self.formats = config_.get('ckan.preview.image_formats').split()
        # toolkit.add_public_directory(config_, "public")
        # toolkit.add_resource("assets", "image_view")

    def info(self) -> dict[str, Any]:
        return {'name': 'image_view',
                'title': plugins.toolkit._('Image'),
                'icon': 'image',
                'schema': {'image_url': [ignore_empty, unicode_safe]},
                'iframed': False,
                'always_available': True,
                'default_title': plugins.toolkit._('Image'),
                }

    def can_view(self, data_dict: dict[str, Any]):
        return (data_dict['resource'].get('format', '').lower()
                in self.formats)

    def view_template(self, context: Context, data_dict: dict[str, Any]):
        return 'image_view.html'

    def form_template(self, context: Context, data_dict: dict[str, Any]):
        return 'image_form.html'
