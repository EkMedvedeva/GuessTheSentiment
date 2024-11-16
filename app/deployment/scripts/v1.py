from deployment import deployment_helper
from deployment.deployment_registry import DeploymentRegistry
from database.database_manager import DatabaseManager


logger = deployment_helper.logger
registry = DeploymentRegistry(1)


@registry.base_update
def deploy_v1_0():
    logger.info('Creating the database with two tables Reviews and Products...')
    
    database_manager = DatabaseManager(base_path=deployment_helper.CURRENT_PATH)
    deployment_helper.create_folder_for_file(database_manager.database_path)
    database_manager.open()
    
    database_manager.create(
        'CREATE TABLE Products('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'name TEXT NOT NULL UNIQUE'
        ')'
    )
    
    database_manager.create(
        'CREATE TABLE Reviews('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'product_id INTEGER NOT NULL,'
        'position INTEGER NOT NULL,'
        'active INTEGER DEFAULT 1 NOT NULL CHECK (active IN (0,1)),'
        'FOREIGN KEY (product_id) REFERENCES Products(id)'
        ')'
    )
    database_manager.create(
        'CREATE INDEX idx_reviews_product_id '
        'ON Reviews(product_id)'
    )
    
    deployment_helper.deploy_products(database_manager)
    database_manager.close()


@registry.minor_update
def deploy_v1_1():
    database_manager = DatabaseManager(base_path=deployment_helper.CURRENT_PATH)
    database_manager.open()
    
    product_name = 'mattress'
    review_positions = (4, 5, 6)
    logger.info(f'Disabling {len(review_positions)} reviews from the product "{product_name}" at the positions {review_positions}...')
    database_manager.reviews_disable(product_name, review_positions)
    
    database_manager.close()

