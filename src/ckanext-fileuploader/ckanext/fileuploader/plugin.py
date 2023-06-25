from __future__ import annotations

import ckan.logic as logic
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.uploader import ResourceUpload as DefaultResourceUpload
from ckan.lib.uploader import Upload as DefaultUpload
from ckan.common import config
import ckan.lib.munge as munge
from ckan.types import (PUploader, PResourceUploader)

import os
import datetime
import cgi
from typing import Any, IO, Union, Optional
from logging import warning
from werkzeug.datastructures import FileStorage as FlaskFileStorage

ALLOWED_UPLOAD_TYPES = (cgi.FieldStorage, FlaskFileStorage)
MB = 1 << 20


def _copy_file(input_file: IO[bytes], output_file: IO[bytes], max_size: int) -> None:
    input_file.seek(0)
    current_size = 0
    while True:
        current_size = current_size + 1
        # MB chunks
        data = input_file.read(MB)

        if not data:
            break
        output_file.write(data)
        if current_size > max_size:
            raise logic.ValidationError({"upload": ["File upload too large"]})


def _get_underlying_file(wrapper: Union[FlaskFileStorage, cgi.FieldStorage]):
    if isinstance(wrapper, FlaskFileStorage):
        return wrapper.stream
    return wrapper.file


def get_storage_path() -> str:
    """
    Function to get the storage path from config file.

    Returns:
        str: storage path
    """
    storage_path = config.get("ckan.storage_path")
    return storage_path


class Upload(DefaultUpload):
    def __init__(self, object_type: str, old_filename: Optional[str] = None) -> None:
        """Setup upload by creating a subdirectory of the storage directory
        of name object_type. old_filename is the name of the file in the url
        field last time"""

        warning(f" ------------------ IM FKING HERE BITCH")
        self.storage_path = None
        self.filename = None
        self.filepath = None
        path = get_storage_path()
        if not path:
            return

        warning(f"------ i am printing object type: {object_type}")
        self.storage_path = os.path.join(path, "storage", "uploads", object_type)
        # check if the storage directory is already created by
        # the user or third-party
        if os.path.isdir(self.storage_path):
            pass
        else:
            try:
                os.makedirs(self.storage_path)
            except OSError as e:
                # errno 17 is file already exists
                if e.errno != 17:
                    raise
        self.object_type = object_type
        self.old_filename = old_filename
        if old_filename:
            self.old_filepath = os.path.join(self.storage_path, old_filename)

    def update_data_dict(
        self,
        data_dict: dict[str, Any],
        url_field: str,
        file_field: str,
        clear_field: str,
    ) -> None:
        """Manipulate data from the data_dict.  url_field is the name of the
        field where the upload is going to be. file_field is name of the key
        where the FieldStorage is kept (i.e the field where the file data
        actually is). clear_field is the name of a boolean field which
        requests the upload to be deleted.  This needs to be called before
        it reaches any validators"""

        warning(
            f"---------------------------------------------------------------- fucking print something my god"
        )
        warning(f"---- ---- ---- WHAT THE FUCK IS URL_FIELD : {url_field}")
        warning(f"---- ---- ---- FUCKING PRINT THE DATADICT : {data_dict}")
        self.url = data_dict.get(url_field, "")
        self.clear = data_dict.pop(clear_field, None)
        self.file_field = file_field
        self.upload_field_storage = data_dict.pop(file_field, None)
        warning(f"---- ---- ---- self.url: {self.url}")
        warning(f"---- ---- ---- self.clear: {self.clear}")
        warning(f"---- ---- ---- self.file_field: {self.file_field}")
        warning(
            f"---- ---- ---- self.upload_field_storage: {self.upload_field_storage}"
        )
        if not self.storage_path:
            return

        if isinstance(self.upload_field_storage, ALLOWED_UPLOAD_TYPES):
            if self.upload_field_storage.filename:
                self.filename = self.upload_field_storage.filename
                self.filename = str(datetime.datetime.utcnow()) + self.filename
                self.filename = munge.munge_filename_legacy(self.filename)
                self.filepath = os.path.join(self.storage_path, self.filename)
                data_dict[url_field] = self.filename
                self.upload_file = _get_underlying_file(self.upload_field_storage)
                self.tmp_filepath = self.filepath + "~"
        # keep the file if there has been no change
        elif self.old_filename and not self.old_filename.startswith("http"):
            if not self.clear:
                data_dict[url_field] = self.old_filename
            if self.clear and self.url == self.old_filename:
                data_dict[url_field] = ""

    def upload(self, max_size: int = 200) -> None:
        """Actually upload the file.
        This should happen just before a commit but after the data has
        been validated and flushed to the db. This is so we do not store
        anything unless the request is actually good.
        max_size is size in MB maximum of the file"""
        warning(
            f"---------- bruh what the FUCK APPEAR LA Package Uploader -- filename: {self.filename}"
        )
        self.verify_type()

        if self.filename:
            assert self.upload_file and self.filepath

            with open(self.tmp_filepath, "wb+") as output_file:
                try:
                    _copy_file(self.upload_file, output_file, max_size)
                except logic.ValidationError:
                    os.remove(self.tmp_filepath)
                    raise
                finally:
                    self.upload_file.close()
            os.rename(self.tmp_filepath, self.filepath)
            self.clear = True

        if (
            self.clear
            and self.old_filename
            and not self.old_filename.startswith("http")
            and self.old_filepath
        ):
            try:
                os.remove(self.old_filepath)
            except OSError:
                pass


class ResourceUpload(DefaultResourceUpload):
    path_prefix = "resources"

    def get_directory(self, directory_id: str):
        path = get_storage_path()
        directory = os.path.join(
            path, self.path_prefix, directory_id[0:3], directory_id[3:6]
        )
        return directory

    def get_path(self, directory_id: str):
        path = get_storage_path()
        filepath = os.path.join(
            path,
            self.path_prefix,
            directory_id[0:3],
            directory_id[3:6],
            directory_id[6:],
        )
        warning(f"---------- Resource Uploader -- filepathhhh: {filepath}")
        return filepath

    def upload(self, directory_id, max_size: int = 200):
        """
        Uploading the file

        Args:
            directory_id (_type_): honestly dk what this is
            max_size (int, optional): file size defaults to 200.
        """

        filepath = self.get_path(directory_id)
        directory = self.get_directory(directory_id)
        if self.filename:
            warning(
                f"---------- Resource Uploader -- wtf is a self.filename: {self.filename}"
            )
            try:
                os.makedirs(directory)
            except OSError as e:
                # errno 17 is file already exists
                if e.errno != 17:
                    raise
            tmp_filepath = filepath + "~"
            with open(tmp_filepath, "wb+") as output_file:
                assert self.upload_file
                try:
                    _copy_file(self.upload_file, output_file, max_size)
                except logic.ValidationError:
                    os.remove(tmp_filepath)
                    raise
                finally:
                    self.upload_file.close()
            os.rename(tmp_filepath, filepath)
            return

        # The resource form only sets self.clear (via the input clear_upload)
        # to True when an uploaded file is not replaced by another uploaded
        # file, only if it is replaced by a link to file.
        # If the uploaded file is replaced by a link, we should remove the
        # previously uploaded file to clean up the file system.
        if self.clear:
            try:
                os.remove(filepath)
            except OSError:
                pass



class FileuploaderPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IUploader, inherit=True)

    # IUploader
    def get_uploader(self, upload_to: str,
                     old_filename: Optional[str]) -> Optional[PUploader]:
        warning(f"WHAT TF IS UPLOAD TO: {upload_to}")
        warning(f"PRINT THE FUCKING UPLOAD KNN: {old_filename}")
        # upload_to = 'preview'
        return Upload(upload_to, old_filename)

    def get_resource_uploader(self, data_dict: dict[str, Any]):
        warning(f"---- ---- ---- PRINTING THE FKING DATADICT FROM IUploader: ")
        for key, val in data_dict.items():
            warning(f"---- ---- {key} : {val}")
        return ResourceUpload(data_dict)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "fileuploader")


