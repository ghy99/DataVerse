[Refer to HaoYi's GitHub for DataVerse for reference i guess](https://github.com/ghy99/DataVerse)

# ckanext-packagecontroller

This module extends the IPackageController interface provided by CKAN and implements custom logic for the `after_dataset_create` method.



**plugins.py**
```python

    read(self, entity: 'model.Package') -> None:
        ''' This method is called after IPackageController before_dataset_view insidepackage_show. This method currently does nothing and can be customised as per your requirements. '''


    create(self, entity: 'model.Package') -> None:
        ''' This method is called after the datasett had been created insde package_create. This method currently does nothing and can be customised as per your requirements.'''

    edit(self, entity: 'model.Package') -> None:
        ''' This method is called after the dataset had been updated inside package_update. This method currently does nothing and can be customised as per your requirements.'''


    delete(self, entity: 'model.Package') -> None:
        ''' This method is called before commit inside package_delete. This method currently does nothing and can be customised as per your requirements.'''


    after_dataset_create(
            self, context: Context, pkg_dict: dict[str, Any]) -> None:
        
        ''' This method is called after the dataset has been created. If a dataset is referenced and not created in the dataset form, the method retrieves the clearml_id from pkg_dict, and updates the package_show dictionary based on the referenced dataset information.'''

    after_dataset_update(
            self, context: Context, pkg_dict: dict[str, Any]) -> None:
             
        ''' This method is called after the dataset is updated. This method currently does nothing and can be customised as per your requirements.'''

    after_dataset_delete(
            self, context: Context, pkg_dict: dict[str, Any]) -> None:
             
        ''' This method is called after the dataset is deleted. This method currently does nothing and can be customised as per your requirements.'''

    after_dataset_show(
            self, context: Context, pkg_dict: dict[str, Any]) -> None:
          
        ''' This method is called after the dataset is displayed. This method currently does nothing and can be customised as per your requirements.'''

    before_dataset_search(
            self, search_params: dict[str, Any]) -> dict[str, Any]:
            
        ''' This method is called before search for datasets. This method currently does nothing and returns the search_params in the form of a dictionary.'''
        return search_params

    after_dataset_search(
            self, search_results: dict[str, Any],
            search_params: dict[str, Any]) -> dict[str, Any]:
    
        ''' This method is called after searching for datasets. This method curerently does nothing and returns the results of the search in the form of a dictionary.'''

        return search_results

    before_dataset_index(self, pkg_dict: dict[str, Any]) -> dict[str, Any]:
        u
        '''
        This method will receive what will be given to Solr for indexing. This is essentially a flattened dict (except for
        multi-valued fields such as tags) of all the terms sent to
        the indexer. This method currently does nothing and returns the pkg_dict.
        '''
        return pkg_dict

    before_dataset_view(self, pkg_dict: dict[str, Any]) -> dict[str, Any]:
        u
        ''' This method is called before the dataset gets displayed. This method currently does nothing and returns the pkg_dict.'''
        return pkg_dict

```


## Installation

1. Create an extension with the following command:
   
   `docker compose -f docker-compose.dev.yml exec ckan-dev /bin/sh -c "ckan generate extension --output-dir /srv/app/src_extensions"`

2. Add your extension name to your .env file. 

   `CKAN__PLUGINS="envvars datastore datapusher packagecontroller"`

3. Restart CKAN. 

   `docker compose -f docker-compose.dev.yml up --build`


## Config settings

None at present


## Tests

None at present