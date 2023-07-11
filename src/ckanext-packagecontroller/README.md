[Refer to HaoYi's GitHub for DataVerse for reference i guess](https://github.com/ghy99/DataVerse)

# ckanext-packagecontroller

This module extends the IPackageController interface provided by CKAN and implements custom logic for the `after_dataset_create` method.


**plugins.py**
```python
    after_dataset_create(self, context: Context, pkg_dict: dict[str, Any])
    ''' 
    This function is called when `referencing ClearML Datasets` occurs. 
    
    The download url for the specified dataset is retrieved and stored in the metadata.
    
    The metadata is then modified by retrieving the `project title` and `dataset title` from ClearML. 
    
    The `title` of the metadata will then be renamed into `new_title` and updated in the package. 
    '''
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