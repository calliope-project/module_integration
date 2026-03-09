import logging
from urllib import request
from zipfile import ZipFile

logger = logging.getLogger(__name__)


def download(url, target_directory):
    logger.info(f"Downloading from {url} to {target_directory}.")
    request.urlretrieve(url, target_directory)


def unzip(zip_filepath, destination):
    with ZipFile(zip_filepath, "r") as zObject:
        zObject.extractall(path=destination)
