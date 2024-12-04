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

    product_name = 'no_mans_sky'
    review_positions = (3, 4, 6, 8, 9, 12, 15, 16, 18, 19, 20, 22, 25, 29, 30, 31, 32, 33, 37, 38, 39, 40, 45, 52, 53, 54, 56, 59, 60, 63, 64, 66, 68, 70, 72, 77, 80, 81, 84, 86, 88, 89, 92, 93, 94, 101, 102, 110, 113, 116, 123, 124, 129, 130, 131, 133, 138, 141, 142, 146, 151, 152, 153, 154, 155, 156, 158, 159, 162, 167, 170, 171, 172, 174, 175, 176, 177, 179, 181, 184, 185, 190, 194, 195, 196, 199, 200, 201, 202, 204, 206, 210, 211, 212, 213, 214, 215, 216, 219, 220, 222, 223, 224, 225, 226, 227, 229, 233, 235, 240, 243, 249, 251, 260, 265, 268, 270, 276, 281, 283, 290, 291, 292, 293, 294, 295, 296, 299, 302, 304, 309, 313, 314, 315, 316, 317, 321, 322, 324, 329, 333, 335, 337, 338, 339, 340, 343, 344, 348, 352, 355, 356, 359, 362, 363, 365, 369, 370, 371, 372, 373, 377, 378, 379, 380, 382, 384, 385, 387, 388, 389, 391, 394, 395, 398, 399, 401, 403, 404, 406, 408, 409, 413, 416, 422, 423, 426, 427, 433, 434, 437, 438, 439, 442, 443, 444, 447, 449, 452, 454, 455, 458, 459, 460, 461, 464, 468, 474, 475, 477, 484, 488, 489, 490, 492, 494, 498, 500, 501, 503, 505, 506, 508, 509, 511, 515, 517, 520, 521, 523, 526, 527, 528, 530, 534, 535, 536, 538, 539, 542, 545, 547, 548, 549, 551, 553, 554, 558, 560, 561, 562, 563, 565, 568, 569, 570, 571, 572, 576, 578, 580, 581, 584, 589)
    logger.info(f'Disabling {len(review_positions)} reviews from the product "{product_name}" at the positions {review_positions}...')
    database_manager.reviews_disable(product_name, review_positions)

    product_name = 'mattress'
    review_positions = (25,)
    logger.info(f'Disabling {len(review_positions)} reviews from the product "{product_name}" at the positions {review_positions}...')
    database_manager.reviews_disable(product_name, review_positions)

    product_name = 'petit_jardin'
    review_positions = (58, 101, 105, 109)
    logger.info(f'Disabling {len(review_positions)} reviews from the product "{product_name}" at the positions {review_positions}...')
    database_manager.reviews_disable(product_name, review_positions)
    
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

