# encoding: utf-8
from __future__ import annotations

from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.types import Context, DataDict
from ckan.common import CKANConfig
from ckan.config.declaration import Declaration, Key


ignore_empty = plugins.toolkit.get_validator('ignore_empty')
unicode_safe = plugins.toolkit.get_validator('unicode_safe')


class AudioViewPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IConfigDeclaration)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "theme/templates")
        self.formats = config_.get('ckan.preview.audio_formats').split()
        # toolkit.add_public_directory(config_, "public")
        # toolkit.add_resource("assets", "audio_view")

    def info(self) -> dict[str, Any]:
        return {'name': 'audio_view',
                'title': plugins.toolkit._('Audio'),
                'icon': 'file-audio',
                'schema': {'audio_url': [ignore_empty, unicode_safe]},
                'iframed': False,
                'always_available': True,
                'default_title': plugins.toolkit._('Audio'),
                }

    def can_view(self, data_dict: DataDict) -> bool:
        return (data_dict['resource'].get('format', '').lower()
                in self.formats)

    def view_template(self, context: Context, data_dict: DataDict) -> str:
        return 'audio_view.html'

    def form_template(self, context: Context, data_dict: DataDict) -> str:
        return 'audio_form.html'

    # IConfigDeclaration

    def declare_config_options(self, declaration: Declaration, key: Key):
        declaration.annotate("audio_view settings")
        declaration.declare(key.ckan.preview.audio_formats, "wav ogg mp3")
