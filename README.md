# HaoYi and JinRui's README.md

# Table of Content:

- [Important Docker Commands](#docker-commands)
- [src Changes](#changes)
    - [lib Folder](#lib)
    - [logic Folder](#logic)
    - [plugins Folder](#plugins)
    - [public Folder](#public)
    - [templates Folder](#templates)
    - [views Folder](#views)
    - [varlibckan Folder](#varlibckan)
- [Extensions](#extensions)
- [Considerations](#considerations)
- [ClearML Configuration](#clearml-config)
- [To Do List](#todo)

---
---

## Important Docker Commands: <a id="docker-commands"></a>

Build docker container:
```
docker compose -f docker-compose.dev.yml up --build
```

Copy files from Docker: ( I think is smth like that ah )
```
docker cp <container id>:<filepath> <destination>
```

List docker containers:
```
docker ps -a
watch docker ps -a
```

Delete docker containers:
```
docker rm $(docker ps -a -q)
```

Delete docker images:
```
docker rmi $(docker images)
```

## Things that we added / changed in the `/src` folder: <a id="changes"></a>

We copied out the main folders from the ckan-dev container such as:
- /lib
- /logic
- /plugins
- /public
- /templates
- /views
- /var/lib/ckan

### lib Folder: <a id="lib"></a>

This folder contains all the built in functions that CKAN created. 

Important ones that we looked through:
- `helpers.py`
- `datapreview.py`
- `uploader.py`

> `datapreview.py` was edited by us (Hao Yi) as there seemed to be a bug inside.
>
> `datapreview.py` is called to check for default view types. 
>
> This is used to show a preview of the file that is uploaded for previews / resources.
>
> Under `get_default_view_plugins()` function, it checks the list of view types that are declared in `ckan.ini`
> The default types are `text_view` and `datatables_view`.
> However, I changed it through the `.env` file. 
>
> When changed, it only takes in a string when retrieving the new view types from the `.env` file. 
>
> I changed the function to check the type of config value retrieved from the `.env` file.
> If it is a string, I convert it to a list so that CKAN can process it as an actual view type instead of looping through a string. 
>
> The extensions `audio_view`, `datatables_view`, `image_view`, `text_view`, `video_view` are the current available view types for the resource page. 
>
> `text_view` currently has some issue where it is not loading my css file changes.

### logic Folder <a id="logic"></a>

This folder stores the API functions, authorization functions and a few other scripts.

Important ones that we looked through:
- `/action/create.py`
- `/action/delete.py`
- `/action/get.py`
- `/action/patch.py`
- `/action/update.py`

### plugins Folder <a id="plugins"></a>

This folder stores files like the plugin interfaces and toolkit.

Important ones that we looked through:
- `interfaces.py`
- `toolkit.py`

### public Folder <a id="public"></a>

This folder stores all the front end code, such as css files, images, javascript files, and the bootstrap and jquery files.

Important files that we added / edited:
- `/css/main.css`
- `/images/dataverse-logo-footer.png`
- `/images/dataverse-logo.png`

> We modified the front end designs through /css/main.css.
> (The gorgeous design rn).
>
>We also added our own logo for the header.html and footer.html.

### templates Folder <a id="templates"></a>

This folder stores all the html files rendered in the frontend. 

Important files that we looked through:
- `/home`
- `/macros`
- `/package`
- `/snippets`
- `footer.html`
- `header.html`
- `page.html`
- `base.html`

> The files that we overwrote are all stored inside the datasetform extension.
>
> Did not change many files here as we added our own templates to overwrite the original.

### views Folder <a id="views"></a>

This folder stores the python scripts that handle the flask requests that occurs during usage. 

Important files that we looked through:
- `dataset.py`
- `resource.py`

> We edited `resource.py` as our script to overwrite `resource.py` did not work for some reason. 
>
> Unsure why CKAN did not register our own blueprint for `resource.py`.
> 
> Refer to `datasetform` extension under `views.py`, and `plugins.py`. 
>> We added the `prepare_resource_blueprint()` function and it shows that it added our blueprint, but it just did not load our URL.
>>
>> So we just overwrote the original `resource.py` file.
>
> We also added our own function `upload_to_clearml()` to handle the dataset uploading to ClearML.
> 
> The function that we overwrote in `resource.py` is the `post()` function in the class `CreateView`.
> 
>> We changed it such that it will download and store the files uploaded in the docker container, then upload it to ClearML. 
>>
>> After uploading, we call the `change_dataset_title()` function to change the name of our dataset in DataVerse. 
>>
>> Lastly, we will delete the files that are uploaded to save space in the docker container.

### var/lib/ckan Folder <a id="varlibckan"></a>

This folder stores the uploaded resources to DataVerse. 

For example, resource files are stored the /resources folder. The names of the files are changed to the resource ID, split by the names in the order of:
    
    [0:3] : first folder
    [3:6] : second folder
    [6: ] : file

> Files that will be uploaded to ClearML are stored in a `/default` folder, which will be deleted after the upload is complete. 

## Extensions <a id="extensions"></a>

List of extensions:
- audio_view
- datatables_view
- image_view
- text_view
- video_view
- datasetform
- fileuploader
- packagecontroller
- resourcecontroller
- versiontree

***Please refer to their own README in the extensions.***


## Things to note: <a id="considerations"></a>

- When there is any changes to the .env file, the docker container ckan-dev will be recreated. So any files added through "`docker exec -it <container id> /bin/sh`" will be deleted. 

## ClearML Configuration: <a id="clearml-config"></a>

- Currently, our ClearML credentials are hardcoded, such that we have to call "`docker exec -it <container id> /bin/sh`" to enter the container can create our ClearML credentials inside before we can create any datasets that will be stored in ClearML. 

### Steps to create ClearML credentials:

> Add `clearml` in dev-requirements.txt
>
> Our current one is added inside resourcecontroller extension.
>
> Navigate to the folder where `docker-compose.dev.yml` is stored.
>
> Run the following command to bring the docker container up:
>>`docker compose -f docker-compose.dev.yml up --build`
>
> Enter the ckan-dev docker container by running the command in a Ubuntu terminal:
>
>> `docker exec -it <container id> /bin/sh`
>
> Run the following command to start the initialization process:
>> `clearml-init`
>
> Switch to the /root folder:
>> `cd /root`
>
> Run the following command to copy the `clearml.conf` file into the /srv/app folder where CKAN is running:
>> `cp clearml.conf /srv/app`
>
> Exit the docker container by typing `ctrl + d`.
>
> Down the docker by typing `ctrl + c`.
>
> Up the docker container again. 

## DataVerse Databases:

To access the databases, follow the following instructions:

> Navigate to the folder where `docker-compose.dev.yml` is stored.
>
> Run the following command to bring the docker container up:
>>`docker compose -f docker-compose.dev.yml up --build`
>
> Enter the db docker container by running the command in a Ubuntu terminal:
>
>> `docker exec -it <container id> /bin/sh`
>
> Enter the following command to log in:
>> `psql -U ckan -d ckan`
>
> Enter the following command to list all tables:
>> `\dt`
>
> To query the database, use postgresql queries. 
>
> E.g.: To select everything from table `package`:
>> `select * from "package";`

# To Do: <a id="todo"></a>

- [ ] Fix `Edit Datasets`. Allow Users to edit datasets without bugs.
- [ ] Fix `Delete Datasets`. Allow Users to delete datasets without bugs, including on the ClearML side. 
- [ ] Add ClearML credentials to the `Register Account`. Users should upload their ClearML credentials so that DataVerse has access to their ClearML account. 
- [ ] Send credentials along with ClearML Dataset requests to communicate with ClearML servers. Currently rely on `clearml.conf` to establish connection to ClearML. Not feasible when introducing multiple users. 
- [ ] Improve version tree design, as well as add more information for user to view in version tree, such as metadata details and links to dataset in DataVerse. 
- [ ] Allow multiple dataset selection and manipulation. 
- [ ] Add CSRF Token to allow removal of dataset from groups