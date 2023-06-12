from __future__ import annotations

from typing import Any, cast
from logging import warning
from ckan.types import Schema
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.types import Context

from clearml import Dataset
from logging import warning
from glob import glob
import os

def get_filename(file_id):
        partial_id = file_id.split('-')
        warning(f"file ID: {file_id}")
        warning(f"PARTIAL FILE NAME: {partial_id}")
        return partial_id

def findFile(file_id):
    partial_name = get_filename(file_id)
    directory = "/var/lib/ckan"
    filepath = os.path.join(directory, f"/{partial_name[0][0:3]}")
    filepath = os.path.join(filepath, f"/{partial_name[0][3:6]}")
    matching_files = glob(filepath + "/**/*{}*".format(partial_name[-1]), recursive=True)
    return matching_files

class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IResourceController)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "extrafields")

    # IDatasetForm
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
    
    # IResourceController
    def before_resource_create(
            self, context: Context, resource: dict[str, Any]) -> None:
        u'''
        Extensions will receive this before a resource is created.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the resource to be added
            to the dataset (the one that is about to be created).
        :type resource: dictionary
        '''
        pass

    def after_resource_create(
            self, context: Context, resource: dict[str, Any]) -> None:
        u'''
        Extensions will receive this after a resource is created.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the latest resource added
            to the dataset (the one that was just created). A key in the
            resource dictionary worth mentioning is ``url_type`` which is
            set to ``upload`` when the resource file is uploaded instead
            of linked.
        :type resource: dictionary
        '''
        warning(f"IRESOURCECONTROLLER: AFTER RESOURCE CREATE FUNCTION:")
        for key, val in resource.items():
            warning(f"----------{key} : {val}")
        dataset_path = findFile(resource['id'])[0]
        warning(f"FILES: {dataset_path}")
        dataset = None
        try:
            warning(f"CREATING DATASET NOW!!!!!!!!!!!!!!")
            # dataset = Dataset.create(
                # dataset_project='Project HDB',
                # dataset_name=resource['name'],
                # description=resource['description'],
            # )
            dataset = Dataset.get(
                dataset_project='Project HDB',
                dataset_name=resource['name'],
                description=resource['description'],
                auto_create=True
            )
        except Exception as e:
            warning(f"UNABLE TO CREATE DATASET IN CLEARML: {e}")
        
        warning(f"ADDING FILES TO DATASET NOW!!!!!!!!!!!!")
        dataset.add_files(path=r'{}'.format(dataset_path))

        try:
            warning(f"UPLOADING NOW!!!!!!!!!!!!!!!!!!!!")
            dataset.upload(show_progress=True, verbose=True)
            warning(f"FINALIZING NOW!!!!!!!!!!!!!!!!!!!!")
            dataset.finalize(verbose=True, raise_on_error=True, auto_upload=True)
        except Exception as e:
            warning(f"UNABLE TO UPLOAD AND FINALIZE: {e}")
        return

    def before_resource_update(self, context: Context, current: dict[str, Any],
                               resource: dict[str, Any]) -> None:
        u'''
        Extensions will receive this before a resource is updated.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param current: The current resource which is about to be updated
        :type current: dictionary
        :param resource: An object representing the updated resource which
            will replace the ``current`` one.
        :type resource: dictionary
        '''
        pass

    def after_resource_update(
            self, context: Context, resource: dict[str, Any]) -> None:
        u'''
        Extensions will receive this after a resource is updated.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the updated resource in
            the dataset (the one that was just updated). As with
            ``after_resource_create``, a noteworthy key in the resource
            dictionary ``url_type`` which is set to ``upload`` when the
            resource file is uploaded instead of linked.
        :type resource: dictionary
        '''
        warning(f"IRESOURCECONTROLLER: AFTER RESOURCE UPDATE FUNCTION:")
        warning(f"id: {resource['id']}")
        warning(f"package_id: {resource['package_id']}")
        warning(f"url: {resource['url']}")
        warning(f"type: {resource['mimetype']}")
        warning(f"package_id: {resource['package_id']}")
        # resource_show = None
        # try:
        #     resource_show = toolkit.get_action('resource_show')({}, {
        #         'id': resource['id']
        #     })
        #     warning(f"PRINTING RESOURCEEEEEEEEEEEEEE: ")
        #     for key, val in resource_show.items():
        #         warning(f"{key} : {val}")
        # except Exception as e:
        #     warning(f"ERROR GETTING RESOURCE_SHOW: {e}")
        
        files = findFile(resource['id'])
        warning(f"FILES: {files}")
        return

    def before_resource_delete(
            self, context: Context, resource: dict[str, Any],
            resources: list[dict[str, Any]]) -> None:
        u'''
        Extensions will receive this before a resource is deleted.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the resource that is about
            to be deleted. This is a dictionary with one key: ``id`` which
            holds the id ``string`` of the resource that should be deleted.
        :type resource: dictionary
        :param resources: The list of resources from which the resource will
            be deleted (including the resource to be deleted if it existed
            in the dataset).
        :type resources: list
        '''
        pass

    def after_resource_delete(
            self, context: Context,
            resources: list[dict[str, Any]]) -> None:
        u'''
        Extensions will receive this after a resource is deleted.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resources: A list of objects representing the remaining
            resources after a resource has been removed.
        :type resource: list
        '''
        pass

    def before_resource_show(
            self, resource_dict: dict[str, Any]) -> dict[str, Any]:
        u'''
        Extensions will receive the validated data dict before the resource
        is ready for display.

        Be aware that this method is not only called for UI display, but also
        in other methods, like when a resource is deleted, because package_show
        is used to get access to the resources in a dataset.
        '''
        
        return resource_dict
    
    