import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.model as model
from ckan.types import Context
from typing import Any
from logging import warning
from clearml import Dataset

class PackagecontrollerPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)
    

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "packagecontroller")

    
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
        if pkg_dict['new_or_existing'] == "Add New Dataset":
            return
        else:
            package_show = toolkit.get_action('package_show')({}, {"id": pkg_dict['id']})

            # retrieved the dataset from ClearML. Should we allow auto create dataset if it doesnt exist?
            dataset = Dataset.get(
                dataset_id=pkg_dict['clearml_id']
            )

            # put the download url in pkg_dict'
            
            package_show["clearml_download_url"] = dataset.get_default_storage()
            
            # Changing metadata fields for the things below
            package_show['project_title'] = dataset.project
            package_show['dataset_title'] = dataset.name
            new_title = dataset.name + "-v" + dataset._dataset_version
            new_title = new_title.replace(" ", "-")
            new_title = new_title.replace(".", "-")
            new_title = new_title.lower()
            # warning(f"---------- NEW TITLE: {new_title}")
            # package_show['name'] = new_name
            package_show['title'] = new_title

            new_pkg_dict = toolkit.get_action("package_update")({}, package_show)
            # warning(f"---------- THIS IS THE UPDATED PKG DICT ----------")
            # for key, val in new_pkg_dict.items():
            #     warning(f"----- {key} : {val} -----")
            return

    def after_dataset_update(
            self, context: Context, pkg_dict: dict[str, Any]) -> None:
        u'''
        Extensions will receive the validated data dict after the dataset
        has been updated.
        '''
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
    
