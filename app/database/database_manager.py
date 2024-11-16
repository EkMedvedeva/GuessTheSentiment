import sqlite3
import os


def param_list(list_):
    return f'({",".join("?" for _ in list_)})'


class DatabaseManager:
    
    def __init__(self, base_path=None):
        self.database_path = DatabaseManager.database_path_get(base_path)
    
    def open(self):
        self.connection = sqlite3.connect(self.database_path)
        self.cursor = self.connection.cursor()

    def create(self, query):
        self.cursor.execute(query)
        self.connection.commit()
    
    def product_lookup_get(self):
        query = (
            'SELECT id, name '
            'FROM Products'
        )
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        lookup = {name: product_id for product_id, name in rows}
        return lookup
    
    def product_create(self, product_name):
        query = (
            'INSERT INTO Products(name) '
            'VALUES (?) '
            'RETURNING id'
        )
        self.cursor.execute(query, (product_name,))
        product_id, = self.cursor.fetchone()
        self.connection.commit()
        return product_id

    def review_positions_get(self, product_id):
        query = (
            'SELECT position '
            'FROM Reviews '
            'WHERE product_id = ?'
        )
        self.cursor.execute(query, (product_id,))
        rows = cursor.fetchall()
        positions = [position for position, in rows]
        return positions
    
    def reviews_create(self, product_id, positions):
        query = (
            'INSERT INTO Reviews(product_id, position) '
            'VALUES (?,?)'
        )
        self.cursor.executemany(query, [(product_id, position) for position in positions])
        self.connection.commit()
    
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
    
    def close(self):
        self.cursor.close()
        self.connection.close()
    
    def database_path_get(base_path=None):
        if base_path is None:
            base_path = ''
        database_path = os.path.join(base_path, 'database/database.db')
        return database_path

