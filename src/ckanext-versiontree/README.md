[Refer to HaoYi's GitHub for DataVerse for reference i guess](https://github.com/ghy99/DataVerse)

# ckanext-versiontree

This extension allows the rendering of a version tree acquired from ClearML and displaying it on CKAN.

**plugins.py:**

This plugin contains the functions for the dataset object from ClearML, fetching the dependency graph of the dataset, sorting dataset IDs, and rendering the version tree with dataset details on the frontend. Additionally, it provides a CKAN plugin class `IBlueprint` to handle configuration and routing.
```python

    getDependencyGraph(dataset):
        """
        This function gets the dependency graph of the dataset parameter that is passed in and returns the dependency graph.
        An error is thrown if the dependency graph cannot be obtained.
        """

    getAllDatasetID(dataset_id):
        """
        This function gets the dataset from the dataset_id passed in and returns the dataset. 
        An errror is thrown if the dataset cannot be obtained.
        """

    sortDataset(dataset_IDs, dataset_details):
        """ 
        This function takes in a list of unsorted dataset IDs and returns a sorted list of the same IDs.
        """

    retrieveDatasetDetails(dataset_details):
        """ 
        This function takes a dataset object with dataset IDs and their attributes as input and returns a condensed dictionary. 
        Each dataset ID is associated with a nested dictionary that includes the project name, dataset name, and version, along with their respective values.
        """

    renderVersionTree():
        """
        This function retrieves the specified dataset's object form ClearML and returns the dependency graph, dataset_IDs and the dataset_details through the render_template function to display them on the frontend
        """

   
    get_blueprint(self):
        """ 
        This method under the IBlueprint interface creates a Flask bluepring object that associates the "/versiontree" URl path with the renderVersionTree function above.
        """

```

## Installation

1. Create an extension with the following command:
   
   `docker compose -f docker-compose.dev.yml exec ckan-dev /bin/sh -c "ckan generate extension --output-dir /srv/app/src_extensions"`

2. Add your extension name to your .env file. 

   `CKAN__PLUGINS="envvars datastore datapusher versiontree"`

3. Restart CKAN. 

   `docker compose -f docker-compose.dev.yml up --build`


## Config settings

None at present


## Tests

None at present