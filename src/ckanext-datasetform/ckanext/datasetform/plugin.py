from __future__ import annotations

from logging import warning
from typing import cast

from ckan.types import Schema
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.datasetform.views import CreatePackageView, CreateResourceView


class DatasetformPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "datasetform")

    # IDatasetForm
    def prepare_dataset_blueprint(self, package_type: str, bp: Blueprint):
        """Update or replace dataset blueprint for given package type.

        Internally CKAN registers blueprint for every custom dataset
        type. Before default routes added to this blueprint and it
        registered inside application this method is called. It can be
        used either for registration of the view function under new
        path or under existing path(like `/new`), in which case this
        new function will be used instead of default one.

        Note, this blueprint has prefix `/{package_type}`.

        :rtype: flask.Blueprint

        """
        warning(f"---------- ADDING BLUEPRINT FOR PACKAGE FORM  : {bp.name} ----------")
        # if self._dataset_form_pages[package_type]:
        bp.add_url_rule(
            "/new",
            "overridePackageCreation",
            view_func=CreatePackageView.as_view(str("new")),
        )
        return bp

    def prepare_resource_blueprint(self, package_type: str,
                                   blueprint: Blueprint) -> Blueprint:
        u'''Update or replace resource blueprint for given package type.

        Internally CKAN registers separate resource blueprint for
        every custom dataset type. Before default routes added to this
        blueprint and it registered inside application this method is
        called. It can be used either for registration of the view
        function under new path or under existing path(like `/new`),
        in which case this new function will be used instead of
        default one.

        Note, this blueprint has prefix `/{package_type}/<id>/resource`.

        :rtype: flask.Blueprint

        '''
        warning(f"---------- ADDING BLUEPRINT FOR RESOURCE FORM : {blueprint.name} ----------")
        blueprint.add_url_rule(
            "/new", 
            "OverrideResourceCreation", 
            view_func=CreateResourceView.as_view("new"),
        )
        # for key, val in blueprint.__dict__.items():
        #     warning(f"__ -_ _- --- --- -__ __-- {key} : {val}")
        # warning(f"-- --__ _ __ _- _ __ _ _--- rule: {blueprint.deferred_functions[0]}")
        return blueprint

    def _modify_package_schema(self, schema: Schema) -> Schema:
        warning(f"---------- MODIFYING PACKAGE SCHEMA HERE ----------")
        schema.update(
            {
                "project_title": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_title": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_uses": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_users": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_abstract": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_limitations": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_published_date": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_license": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "privacy_marking_classification": [
                    toolkit.get_converter("convert_to_extras")
                ],
                "privacy_marking_sensitivity": [
                    toolkit.get_converter("convert_to_extras")
                ],
                "additional_remarks": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_source": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_related_resources": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "dataset_type": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "data_collection": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "update_frequency": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "geospatial_coverage": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "temporal_coverage": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "online_coverage": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "data_preparation": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "data_dict_and_schema": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "new_or_existing": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                "clearml_id": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ],
                # "upload": [
                #     toolkit.get_validator("ignore_missing"),
                #     toolkit.get_converter("convert_to_extras"),
                # ],
            }
        )

        # Add our custom_resource_text metadata field to the schema
        # cast(Schema, schema["resources"]).update(
        #     {
        #         "display_preview": [
        #             toolkit.get_validator("ignore_missing"),
        #         ]
        #     }
        # )
        # cast(Schema, schema['resources']).update({
        #         'metafield_resource_2' : [ toolkit.get_validator('ignore_missing') ]
        #         })
        # cast(Schema, schema['resources']).update({
        #         'metafield_resource_3' : [ toolkit.get_validator('ignore_missing') ]
        #         })
        return schema

    def create_package_schema(self):
        schema: Schema = super(DatasetformPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema: Schema = super(DatasetformPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self) -> Schema:
        schema: Schema = super(DatasetformPlugin, self).show_package_schema()

        # Add our custom_text field to the dataset schema.
        schema.update(
            {
                "project_title": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_title": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_uses": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_users": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_abstract": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_limitations": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_published_date": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_license": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "privacy_marking_classification": [
                    toolkit.get_converter("convert_from_extras")
                ],
                "privacy_marking_sensitivity": [
                    toolkit.get_converter("convert_from_extras")
                ],
                "additional_remarks": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_source": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_related_resources": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "dataset_type": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "data_collection": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "update_frequency": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "geospatial_coverage": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "temporal_coverage": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "online_coverage": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "data_preparation": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "data_dict_and_schema": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "new_or_existing": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                "clearml_id": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ],
                # "upload": [
                #     toolkit.get_converter("convert_from_extras"),
                #     toolkit.get_validator("ignore_missing"),
                # ],
            }
        )

        # cast(Schema, schema["resources"]).update(
        #     {"display_preview": [toolkit.get_validator("ignore_missing")]}
        # )

        # cast(Schema, schema['resources']).update({
        #         'metafield_resource_2' : [ toolkit.get_validator('ignore_missing') ]
        #     })

        # cast(Schema, schema['resources']).update({
        #         'metafield_resource_3' : [ toolkit.get_validator('ignore_missing') ]
        #     })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return False

    def package_types(self) -> list[str]:
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return ["dataset"]
