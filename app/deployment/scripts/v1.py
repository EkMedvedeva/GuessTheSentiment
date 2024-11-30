from deployment import deployment_helper
from deployment.deployment_registry import DeploymentRegistry
from database.database_manager import DatabaseManager


logger = deployment_helper.logger
registry = DeploymentRegistry(1)


@registry.base_update
def deploy_v1_0():
    logger.info('Creating the database with the necessary tables...')
    
    database_manager = DatabaseManager(base_path=deployment_helper.CURRENT_PATH)
    deployment_helper.create_folder_for_file(database_manager.database_path)
    database_manager.open()
    
    database_manager.create(
        'CREATE TABLE ProductCategories('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'name TEXT NOT NULL UNIQUE'
        ')'
    )
    
    database_manager.create(
        'CREATE TABLE Products('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'category_id INTEGER NOT NULL,'
        'name TEXT NOT NULL UNIQUE,'
        'FOREIGN KEY (category_id) REFERENCES ProductCategories(id)'
        ')'
    )
    database_manager.create(
        'CREATE INDEX idx_products_category_id '
        'ON Products(category_id)'
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
    
    database_manager.create(
        'CREATE TABLE Scales('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'name TEXT NOT NULL UNIQUE'
        ')'
    )
    
    database_manager.create(
        'CREATE TABLE Metrics('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'name TEXT NOT NULL UNIQUE,'
        'question TEXT NOT NULL,'
        'scale_id INTEGER NOT NULL,'
        'FOREIGN KEY (scale_id) REFERENCES Scales(id)'
        ')'
    )
    
    database_manager.create(
        'CREATE TABLE Experiments('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'name TEXT NOT NULL UNIQUE,'
        'metric_id INTEGER NOT NULL,'
        'active INTEGER DEFAULT 1 NOT NULL CHECK (active IN (0,1)),'
        'FOREIGN KEY (metric_id) REFERENCES Metrics(id)'
        ')'
    )
    
    database_manager.create(
        'CREATE TABLE Users('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'name TEXT NOT NULL UNIQUE,'
        'creation_time INTEGER NOT NULL'
        ')'
    )
    database_manager.create(
        'CREATE INDEX idx_users_name '
        'ON Users(name)'
    )
    
    database_manager.create(
        'CREATE TABLE Connections('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'user_id INTEGER NOT NULL,'
        'time INTEGER NOT NULL,'
        'FOREIGN KEY (user_id) REFERENCES Users(id)'
        ')'
    )
    database_manager.create(
        'CREATE INDEX idx_connections_user_id '
        'ON Connections(user_id, time DESC)'
    )
    
    database_manager.create(
        'CREATE TABLE Sessions('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'user_id INTEGER NOT NULL,'
        'metric_id INTEGER NOT NULL,'
        'product_id INTEGER NOT NULL,'
        'creation_time INTEGER NOT NULL,'
        'FOREIGN KEY (user_id) REFERENCES Users(id),'
        'FOREIGN KEY (metric_id) REFERENCES Metrics(id),'
        'FOREIGN KEY (product_id) REFERENCES Products(id)'
        ')'
    )
    database_manager.create(
        'CREATE INDEX idx_sessions_user_id '
        'ON Sessions(user_id)'
    )
    
    database_manager.create(
        'CREATE TABLE Guesses('
        'id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'session_id INTEGER NOT NULL,'
        'review_id INTEGER NOT NULL,'
        'rating INTEGER NOT NULL,'
        'duration_ms INTEGER NOT NULL,'
        'FOREIGN KEY (session_id) REFERENCES Sessions(id),'
        'FOREIGN KEY (review_id) REFERENCES Reviews(id)'
        ')'
    )
    
    deployment_helper.deploy_products(database_manager)
    
    logger.info('Creating a generic nps experiment with a scale from 0 to 10...')
    scale_id = database_manager.scale_create('nps0-10')
    nps_question = 'In your opinion, how likely is this reviewer to recommend this product?'
    metric_id = database_manager.metric_create('nps0-10', nps_question, scale_id)
    experiment_id = database_manager.experiment_create('nps0-10', metric_id)
    
    database_manager.close()


##@registry.minor_update
##def deploy_v1_1():
##    database_manager = DatabaseManager(base_path=deployment_helper.CURRENT_PATH)
##    database_manager.open()
##    
##    product_name = 'mattress'
##    review_positions = (4, 5, 6)
##    logger.info(f'Disabling {len(review_positions)} reviews from the product "{product_name}" at the positions {review_positions}...')
##    database_manager.reviews_disable(product_name, review_positions)
##    
##    database_manager.close()

