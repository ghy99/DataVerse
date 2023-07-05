# encoding: utf-8
from __future__ import annotations

from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.types import Context
from ckan.common import CKANConfig
from ckan.config.declaration import Declaration, Key


ignore_empty = plugins.toolkit.get_validator('ignore_empty')
unicode_safe = plugins.toolkit.get_validator('unicode_safe')




class VideoViewPlugin(plugins.SingletonPlugin):
    '''This plugin makes views of video resources, using a <video> tag'''

    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IConfigDeclaration)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "theme/templates")
        self.formats = config_.get('ckan.preview.video_formats').split()
        # toolkit.add_public_directory(config_, "public")
        # toolkit.add_resource("assets", "video_view")

    def info(self) -> dict[str, Any]:
        return {'name': 'video_view',
                'title': plugins.toolkit._('Video'),
                'icon': 'file-video',
                'schema': {'video_url': [ignore_empty, unicode_safe],
                           'poster_url': [ignore_empty, unicode_safe]},
                'iframed': False,
                'always_available': True,
                'default_title': plugins.toolkit._('Video'),
                }

    def can_view(self, data_dict: dict[str, Any]):
        return (data_dict['resource'].get('format', '').lower()
                in self.formats)

    def view_template(self, context: Context, data_dict: dict[str, Any]):
        return 'video_view.html'

    def form_template(self, context: Context, data_dict: dict[str, Any]):
        return 'video_form.html'

    # IConfigDeclaration

    def declare_config_options(self, declaration: Declaration, key: Key):
        declaration.annotate("video_view settings")
        declaration.declare(key.ckan.preview.video_formats, "mp4 ogg webm")
           



    
