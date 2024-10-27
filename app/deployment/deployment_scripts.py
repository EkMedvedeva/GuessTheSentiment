from dataclasses import dataclass
from typing import Callable
import sqlite3
import os
import json
import logging
from io import StringIO

from deployment import deployment_helper


log_stream = StringIO()
logging.basicConfig(stream=log_stream, format='%(message)s')
logger = logging.getLogger(name='deployment_scripts')
logger.setLevel(logging.DEBUG)


@dataclass
class DeploymentScript:
    previous_version: tuple[int, int]
    next_version: tuple[int, int]
    function: Callable[[], None]


DEPLOYMENT_SCRIPTS = []
BASE_VERSION = (0, 0)


def deployment_decorator(function, major):
    # Get the previous version
    if len(DEPLOYMENT_SCRIPTS) == 0:
        previous_version = BASE_VERSION
    else:
        previous_version = DEPLOYMENT_SCRIPTS[-1].next_version
    # Get the next version
    if major:
        next_version = (previous_version[0] + 1, 0)
    else:
        next_version = (previous_version[0], previous_version[1] + 1)
    # Register the received function as a deployment function
    # with the correct version numbers
    deployment_script = DeploymentScript(
        previous_version=previous_version,
        next_version=next_version,
        function=function
    )
    DEPLOYMENT_SCRIPTS.append(deployment_script)
    return function

def major_update(function):
    return deployment_decorator(function, True)

def minor_update(function):
    return deployment_decorator(function, False)

def scripts_get(current_version):
    if current_version is None:
        current_version = BASE_VERSION
    for deployment_script in DEPLOYMENT_SCRIPTS:
        if deployment_script.next_version > current_version:
            yield deployment_script

def log_get():
    return log_stream.getvalue()

def log_clear():
    log_stream.truncate(0)
    log_stream.seek(0)


# ------------------------------------------------------------
# Start of the deployment scripts


@minor_update
def deploy_v0_1():
    logger.info('Blank update')


def deploy_products(connection, cursor):
    logger.info('Deploying products to the database...')
    # Get all existing product names in the database
    cursor.execute(
        'SELECT id, name '
        'FROM Products'
    )
    rows = cursor.fetchall()
    db_product_lookup = {name: product_id for product_id, name in rows}
    
    for product_file in deployment_helper.list_files(deployment_helper.REVIEWS_PATH):
        if product_file.name != 'data.json':
            continue
        product_name = os.path.dirname(product_file.relative_path)
        if product_name not in db_product_lookup:
            # The product is not in the database
            logger.info(f'Inserting the product "{product_name}" to the database...')
            cursor.execute(
                'INSERT INTO Products(name) '
                'VALUES (?) '
                'RETURNING id',
                (product_name,)
            )
            product_id, = cursor.fetchone()
            db_review_positions = []
        else:
            # Get all existing review positions in the database for this product id
            product_id = db_product_lookup[product_name]
            cursor.execute(
                'SELECT position '
                'FROM Reviews '
                'WHERE product_id = ?',
                (product_id,)
            )
            rows = cursor.fetchall()
            db_review_positions = [position for position, in rows]
        # Check how many reviews actually exist in the file
        with open(deployment_helper.product_path_get(product_name), 'r') as file:
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
        cursor.executemany(
            'INSERT INTO Reviews(product_id, position) '
            'VALUES (?,?)',
            [(product_id, review_position) for review_position in missing_review_positions]
        )
    connection.commit()


@major_update
def deploy_v1_0():
    logger.info('Creating the database with two tables Reviews and Products...')
    
    deployment_helper.create_folder_for_file(deployment_helper.DATABASE_PATH)
    connection = sqlite3.connect(deployment_helper.DATABASE_PATH)
    cursor = connection.cursor()
    
    cursor.execute(
        'CREATE TABLE Products('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'name TEXT NOT NULL UNIQUE'
        ')'
    )
    
    cursor.execute(
        'CREATE TABLE Reviews('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'product_id INTEGER NOT NULL,'
        'position INTEGER NOT NULL,'
        'active INTEGER DEFAULT 1 NOT NULL CHECK (active IN (0,1)),'
        'FOREIGN KEY (product_id) REFERENCES Products(id)'
        ')'
    )
    cursor.execute(
        'CREATE INDEX idx_reviews_product_id '
        'ON Reviews(product_id)'
    )
    connection.commit()
    
    deploy_products(connection, cursor)
    connection.close()
    


