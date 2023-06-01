from __future__ import annotations

from typing import Any, cast
from ckan.types import Schema
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "extrafields")

    def _modify_package_schema(self, schema: Schema) -> Schema:
        schema.update({
            'metafield_1': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })

        schema.update({
            'metafield_2': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })

        schema.update({
            'metafield_3': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })
         # Add our custom_resource_text metadata field to the schema
        cast(Schema, schema['resources']).update({
                'metafield_resource_1' : [ toolkit.get_validator('ignore_missing') ]
                })
        cast(Schema, schema['resources']).update({
                'metafield_resource_2' : [ toolkit.get_validator('ignore_missing') ]
                })
        cast(Schema, schema['resources']).update({
                'metafield_resource_3' : [ toolkit.get_validator('ignore_missing') ]
                })
        return schema

    def create_package_schema(self):
        schema: Schema = super(
            ExtrafieldsPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema: Schema = super(
            ExtrafieldsPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema
    
    def show_package_schema(self) -> Schema:
        schema: Schema = super(
            ExtrafieldsPlugin, self).show_package_schema()
        
        # Add our custom_text field to the dataset schema.
        schema.update({
            'metafield_1': [toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')]
            })
        
        schema.update({
            'metafield_2': [toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')]
            })
        
        schema.update({
            'metafield_3': [toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')]
            })

        cast(Schema, schema['resources']).update({
                'metafield_resource_1' : [ toolkit.get_validator('ignore_missing') ]
            })

        cast(Schema, schema['resources']).update({
                'metafield_resource_2' : [ toolkit.get_validator('ignore_missing') ]
            })

        cast(Schema, schema['resources']).update({
                'metafield_resource_3' : [ toolkit.get_validator('ignore_missing') ]
            })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self) -> list[str]:
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []