[Refer to HaoYi's GitHub for DataVerse for reference i guess](https://github.com/ghy99/DataVerse)

# ckanext-resourcecontroller

This module extends the IResourceController interface provided by CKAN, and is used to hook logic into the resource view.

>> ** This module is no longer used** 

## Installation

1. Create an extension with the following command:
   
   `docker compose -f docker-compose.dev.yml exec ckan-dev /bin/sh -c "ckan generate extension --output-dir /srv/app/src_extensions"`

2. Add your extension name to your .env file. 

   `CKAN__PLUGINS="envvars datastore datapusher resourcecontroller"`

3. Restart CKAN. 

   `docker compose -f docker-compose.dev.yml up --build`


## Config settings

None at present


## Tests

None at present