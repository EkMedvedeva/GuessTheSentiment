import os
from dataclasses import dataclass
import logging
from io import StringIO
import json


log_stream = StringIO()
logging.basicConfig(stream=log_stream, format='%(message)s')
logger = logging.getLogger(name='deployment_scripts')
logger.setLevel(logging.DEBUG)


def log_get():
    return log_stream.getvalue()


def log_clear():
    log_stream.truncate(0)
    log_stream.seek(0)


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
REVIEWS_PATH = path_join(CURRENT_PATH, 'reviews')


def deploy_products(database_manager):
    logger.info('Deploying products to the database...')
    # Get all existing product names in the database
    db_product_lookup = database_manager.product_lookup_get()
    
    for product_file in list_files(REVIEWS_PATH):
        if product_file.name != 'data.json':
            continue
        product_name = os.path.dirname(product_file.relative_path)
        if product_name not in db_product_lookup:
            # The product is not in the database
            logger.info(f'Inserting the product "{product_name}" to the database...')
            product_id = database_manager.product_create(product_name)
            db_review_positions = []
        else:
            # Get all existing review positions in the database for this product id
            product_id = db_product_lookup[product_name]
            db_review_positions = database_manager.review_positions_get(product_id)
        # Check how many reviews actually exist in the file
        with open(product_path_get(product_name), 'r') as file:
            text = file.read()
        product_data = json.loads(text)
        review_count = len(product_data['reviews'])
        # Check which review positions in the file are missing in the database
        missing_review_positions = [
            review_position
            for review_position in range(review_count)
            if review_position not in db_review_positions
        ]
        # Insert the missing review positions in the database
        if len(missing_review_positions) == 0:
            continue
        logger.info(f'Inserting {len(missing_review_positions)} reviews to the product "{product_name}" (id={product_id})...')
        database_manager.reviews_create(product_id, missing_review_positions)


