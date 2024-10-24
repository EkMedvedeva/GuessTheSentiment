import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RelativeFile:
    name: str
    relative_path: str


def path_join(*paths):
    path = os.path.join(*paths)
    normalized_path = os.path.normpath(path)
    return normalized_path


def list_files(folder_path):
    # Relative paths are relative to 'folder_path'
    for root_path, folder_names, file_names in os.walk(folder_path):
        root_relative_path = os.path.relpath(root_path, folder_path)
        for file_name in file_names:
            file_relative_path = path_join(root_relative_path, file_name)
            file = RelativeFile(name=file_name, relative_path=file_relative_path)
            yield file


def create_folder_for_file(file_path):
    folder_path = os.path.dirname(file_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def product_path_get(name):
    return path_join(REVIEWS_PATH, name, 'data.json')


SOURCE_PATH = ''
CURRENT_PATH = '../current'
BACKUP_PATH = '../backups'

VERSION_HISTORY_PATH = path_join(CURRENT_PATH, 'deployment/version_history.json')
DATABASE_PATH = path_join(CURRENT_PATH, 'database/database.db')
REVIEWS_PATH = path_join(CURRENT_PATH, 'reviews')


