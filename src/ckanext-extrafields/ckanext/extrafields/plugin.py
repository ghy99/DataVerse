from __future__ import annotations

from typing import Any, cast
from logging import warning
from ckan.types import Schema
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.types import Context

import wget
import os
from clearml import Dataset

class ExtrafieldsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IResourceController)

    
    # IPackageController
    def read(self, entity: 'model.Package') -> None:
        u'''
        Called after IPackageController.before_dataset_view inside
        package_show.
        '''
        pass

    def create(self, entity: 'model.Package') -> None:
        u'''Called after the dataset had been created inside package_create.
        '''
        pass

    def edit(self, entity: 'model.Package') -> None:
        u'''Called after the dataset had been updated inside package_update.
        '''
        pass

    def delete(self, entity: 'model.Package') -> None:
        u'''Called before commit inside package_delete.
        '''
        pass

    def after_dataset_create(
            self, context: Context, pkg_dict: dict[str, Any]) -> None:
        u'''
        Extensions will receive the validated data dict after the dataset
        has been created (Note that the create method will return a dataset
        domain object, which may not include all fields). Also the newly
        created dataset id will be added to the dict.
        '''
        warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!LOGGING PACKAGE DICTIONARY IN CREATE:")
        for key, val in pkg_dict.items():
            warning(f"{key} : {val}")
        

    def after_dataset_update(
            self, context: Context, pkg_dict: dict[str, Any]) -> None:
        u'''
        Extensions will receive the validated data dict after the dataset
        has been updated.
        '''
        warning(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!LOGGING PACKAGE DICTIONARY IN UPDATE:")
        for key, val in pkg_dict.items():
            warning(f"{key} : {val}")
        pass

    def after_dataset_delete(
            self, context: Context, pkg_dict: dict[str, Any]) -> None:
        u'''
        Extensions will receive the data dict (typically containing
        just the dataset id) after the dataset has been deleted.
        '''
        pass

    def after_dataset_show(
            self, context: Context, pkg_dict: dict[str, Any]) -> None:
        u'''
        Extensions will receive the validated data dict after the dataset
        is ready for display.
        '''
        pass

    def before_dataset_search(
            self, search_params: dict[str, Any]) -> dict[str, Any]:
        u'''
        Extensions will receive a dictionary with the query parameters,
        and should return a modified (or not) version of it.

        search_params will include an `extras` dictionary with all values
        from fields starting with `ext_`, so extensions can receive user
        input from specific fields.
        '''
        return search_params

    def after_dataset_search(
            self, search_results: dict[str, Any],
            search_params: dict[str, Any]) -> dict[str, Any]:
        u'''
        Extensions will receive the search results, as well as the search
        parameters, and should return a modified (or not) object with the
        same structure::

            {'count': '', 'results': '', 'search_facets': ''}

        Note that count and facets may need to be adjusted if the extension
        changed the results for some reason.

        search_params will include an `extras` dictionary with all values
        from fields starting with `ext_`, so extensions can receive user
        input from specific fields.

        '''

        return search_results

    def before_dataset_index(self, pkg_dict: dict[str, Any]) -> dict[str, Any]:
        u'''
        Extensions will receive what will be given to Solr for
        indexing. This is essentially a flattened dict (except for
        multi-valued fields such as tags) of all the terms sent to
        the indexer. The extension can modify this by returning an
        altered version.
        '''
        return pkg_dict

    def before_dataset_view(self, pkg_dict: dict[str, Any]) -> dict[str, Any]:
        u'''
        Extensions will receive this before the dataset gets
        displayed. The dictionary passed will be the one that gets
        sent to the template.
        '''
        return pkg_dict

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
        warning(f"LOGGING RESOURCE CREATION BABEYYYYY:")
        for key, val in resource.items():
            warning(f"key - {key} : val - {val}")
        
        
        pass

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
        warning(f"LOGGING RESOURCE UPDATE BABEYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY:")
        url = resource['url']
        local_file = url.split('/')[-1]
        wget.download(url, local_file)
        
        try:
            dataset = Dataset.create(
                dataset_project='Project Covid',
                dataset_name=resource['name'],
                dataset_version='1.0',
                description=resource['description'],
            )
        except Exception as e:
            warning(f"ERROR CREATING DATASET: ERROR {e}")
        warning(f"DATASET CREATION DONE!!!!!")
        
        warning(f"ADDING FILES NOW!!!!!!!!!!!!!!!!!!")
        url = resource['url']
        warning(r"This url is : {}".format(url))
        dataset.add_files(
            path=r"{}".format(local_file)
        )
        warning(f"UPLOADING NOW!!!!!!!!!!!!!!!!!!!!!")
        try:
            dataset.upload(show_progress=True, verbose=True)
            warning(f"FINALIZING NOW!!!!!!!!!!!!!!!!!!!!")
            dataset.finalize(verbose=True, raise_on_error=True, auto_upload=True)
        except Exception as e:
            warning(f"unable to upload file. Error: {e}")
        os.remove(local_file)
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