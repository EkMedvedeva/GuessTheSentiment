import sqlite3
import os
import threading


def param_list(list_):
    return f'({",".join("?" for _ in list_)})'


def locked(function):
    def locked_function(self, *args, **kwargs):
        with self.lock:
            return function(self, *args, **kwargs)
    return locked_function


class DatabaseManager:
    
    def __init__(self, base_path=None):
        self.database_path = DatabaseManager.database_path_get(base_path)
    
    def open(self):
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.lock = threading.Lock()

    def create(self, query):
        self.cursor.execute(query)
        self.connection.commit()
    
    @locked
    def product_category_create(self, product_category_name):
        query = (
            'INSERT INTO ProductCategories(name) '
            'VALUES (?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (product_category_name,))
        product_category_id, = self.cursor.fetchone()
        self.connection.commit()
        return product_category_id
    
    @locked
    def product_category_lookup_get(self):
        query = (
            'SELECT id, name '
            'FROM ProductCategories'
        )
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        lookup = {name: product_category_id for product_category_id, name in rows}
        return lookup
    
    @locked
    def product_create(self, product_name, product_category_id):
        query = (
            'INSERT INTO Products(category_id, name) '
            'VALUES (?,?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (product_category_id, product_name,))
        product_id, = self.cursor.fetchone()
        self.connection.commit()
        return product_id
    
    @locked
    def products_get(self):
        query = (
            'SELECT id, name '
            'FROM Products'
        )
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        products = {product_id: name for product_id, name in rows}
        return products
    
    @locked
    def product_lookup_get(self):
        query = (
            'SELECT id, name '
            'FROM Products'
        )
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        lookup = {name: product_id for product_id, name in rows}
        return lookup
    
    @locked
    def reviews_create(self, product_id, positions):
        query = (
            'INSERT INTO Reviews(product_id, position) '
            'VALUES (?,?)'
        )
        self.cursor.executemany(query, [(product_id, position) for position in positions])
        self.connection.commit()
    
    @locked
    def reviews_get(self):
        query = (
            'SELECT id, product_id, position '
            'FROM Reviews'
        )
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        reviews = {review_id: (product_id, position) for review_id, product_id, position in rows}
        return reviews
    
    @locked
    def review_positions_get(self, product_id):
        query = (
            'SELECT position '
            'FROM Reviews '
            'WHERE product_id = ?'
        )
        self.cursor.execute(query, (product_id,))
        rows = self.cursor.fetchall()
        positions = [position for position, in rows]
        return positions
    
    @locked
    def unguessed_reviews_get(self, user_id, category_id):
        # Return all reviews from a product of this category that have never been guessed by this user
        query = (
            'SELECT r.id, r.product_id '
            'FROM Reviews r '
            'JOIN Products p ON r.product_id = p.id '
            'WHERE p.category_id = ? '
            'AND r.active = 1 '
            'AND r.id NOT IN ('
                'SELECT g.review_id '
                'FROM Guesses g '
                'JOIN Sessions s ON g.session_id = s.id '
                'WHERE s.user_id = ?'
            ')'
        )
        self.cursor.execute(query, (category_id, user_id))
        rows = self.cursor.fetchall()
        unguessed_reviews = {}
        for review_id, product_id in rows:
            if product_id not in unguessed_reviews:
                unguessed_reviews[product_id] = []
            unguessed_reviews[product_id].append(review_id)
        return unguessed_reviews
    
    @locked
    def reviews_disable(self, product_name, positions):
        query = (
            'SELECT id '
            'FROM Products '
            'WHERE name = ?'
        )
        self.cursor.execute(query, (product_name,))
        product_id, = self.cursor.fetchone()
        query = (
            'UPDATE Reviews '
            'SET active = 0 '
            f'WHERE product_id = ? AND position IN {param_list(positions)}'
        )
        self.cursor.execute(query, (product_id, *positions))
        self.connection.commit()
    
    @locked
    def scale_create(self, scale_name):
        query = (
            'INSERT INTO Scales(name) '
            'VALUES (?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (scale_name,))
        scale_id, = self.cursor.fetchone()
        self.connection.commit()
        return scale_id
    
    @locked
    def metric_create(self, metric_name, question, scale_id):
        query = (
            'INSERT INTO Metrics(name, question, scale_id) '
            'VALUES (?,?,?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (metric_name, question, scale_id))
        metric_id, = self.cursor.fetchone()
        self.connection.commit()
        return metric_id
    
    @locked
    def metrics_get(self):
        query = (
            'SELECT id, question '
            'FROM Metrics'
        )
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        metrics = {metric_id: question for metric_id, question in rows}
        return metrics
    
    @locked
    def experiment_create(self, experiment_name, metric_id):
        query = (
            'INSERT INTO Experiments(name, metric_id) '
            'VALUES (?,?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (experiment_name, metric_id,))
        experiment_id, = self.cursor.fetchone()
        self.connection.commit()
        return experiment_id
    
    @locked
    def experiments_get(self):
        query = (
            'SELECT e.id, m.id '
            'FROM Experiments e '
            'JOIN Metrics m ON e.metric_id = m.id '
            'WHERE e.active = 1'
        )
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        experiments = {experiment_id: metric_id for experiment_id, metric_id in rows}
        return experiments
    
    @locked
    def user_create(self, user_name, creation_time):
        query = (
            'INSERT INTO Users(name, creation_time) '
            'VALUES (?,?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (user_name, creation_time))
        user_id, = self.cursor.fetchone()
        self.connection.commit()
        return user_id
    
    @locked
    def user_id_get(self, user_name):
        query = (
            'SELECT id '
            'FROM Users '
            'WHERE name = ?'
        )
        self.cursor.execute(query, (user_name,))
        user_id, = self.cursor.fetchone()
        self.connection.commit()
        return user_id
    
    @locked
    def connection_create(self, user_id, creation_time):
        query = (
            'INSERT INTO Connections(user_id, time) '
            'VALUES (?,?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (user_id, creation_time))
        connection_id, = self.cursor.fetchone()
        self.connection.commit()
        return connection_id
    
    @locked
    def session_create(self, user_id, metric_id, product_id, creation_time):
        query = (
            'INSERT INTO Sessions(user_id, metric_id, product_id, creation_time) '
            'VALUES (?,?,?,?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (user_id, metric_id, product_id, creation_time))
        session_id, = self.cursor.fetchone()
        self.connection.commit()
        return session_id
    
    @locked
    def guess_create(self, session_id, review_id, rating, duration_ms):
        query = (
            'INSERT INTO Guesses(session_id, review_id, rating, duration_ms) '
            'VALUES (?,?,?,?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (session_id, review_id, rating, duration_ms))
        guess_id, = self.cursor.fetchone()
        self.connection.commit()
        return guess_id
    
    def close(self):
        self.cursor.close()
        self.connection.close()
    
    def database_path_get(base_path=None):
        if base_path is None:
            base_path = ''
        database_path = os.path.join(base_path, 'database/database.db')
        return database_path

