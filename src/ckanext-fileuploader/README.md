[Refer to HaoYi's GitHub for DataVerse for reference i guess](https://github.com/ghy99/DataVerse)


# ckanext-fileuploader

This extension uses the IUploader plugin Interface. 
Mostly copied from github ckan.
I used this to check the max file size that i can upload.
Didn't use this to do anything else i think. 

## Installation

1. Create an extension with the following command:
   
   `docker compose -f docker-compose.dev.yml exec ckan-dev /bin/sh -c "ckan generate extension --output-dir /srv/app/src_extensions"`

2. Add your extension name to your .env file. 

   `CKAN__PLUGINS="envvars fileuploader"`

3. Restart CKAN. 

   `docker compose -f docker-compose.dev.yml up --build`


## Config settings

None at present


## Tests

None at present


## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
