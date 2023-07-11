[Refer to HaoYi's GitHub for DataVerse for reference i guess](https://github.com/ghy99/DataVerse)


# ckanext-resourcecontroller

This extension is supposed to be used to make any changes after resource create.
But this does not seem to be used. For now. 
Next time can use I guess.


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


## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
