from __future__ import annotations

from typing import Any
from logging import warning
from clearml import Dataset

from ckan.types import Context
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def findFile(file_id):
    directory = "/var/lib/ckan/resources"
    outer_path = file_id[0:3]
    inner_path = file_id[3:6]
    filename = file_id[6:]
    filepath = rf"{directory}/{outer_path}/{inner_path}/{filename}"
    return filepath


class ResourcecontrollerPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController)


    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "resourcecontroller")
    
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
        dataset_path = findFile(resource['id'])
        warning(f"FILES: {dataset_path}")
        dataset = None
        try:
            warning(f"CREATING DATASET NOW!!!!!!!!!!!!!!")
            dataset = Dataset.create(
                dataset_project='Project HDB',
                dataset_name=resource['name'],
                description=resource['description'],
            )
            # dataset = Dataset.get(
            #     dataset_project='Project HDB',
            #     dataset_name=resource['name'],
            #     description=resource['description'],
            #     auto_create=True
            # )
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
    
    