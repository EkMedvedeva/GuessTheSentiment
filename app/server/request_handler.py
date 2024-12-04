import json
import random
import time
from dataclasses import dataclass

from database.database_manager import DatabaseManager
from server.base_request_handler import MyBaseRequestHandler, InvalidRequestData, InternalError
from helpers import command_helper


SESSION_REVIEW_COUNT = 20


@dataclass
class Session:
    session_id: int
    user_id: int
    experiment_id: int
    metric_id: int
    product_id: int
    review_ids: list[int]

@dataclass
class Connection:
    user_id: int


class UserNameHelper:
    
    def __init__(self):
        with open('misc/default_user_names.json', 'r') as file:
            self.default_names = json.loads(file.read())
    
    def sanitize(self, user_name):
        user_name = user_name[:32]
        return user_name
    
    def generate_random(self):
        user_name = ' '.join([
            random.choice(self.default_names['adjectives']),
            random.choice(self.default_names['nouns']),
            random.choice(self.default_names['emojis'])
        ])
        return self.sanitize(user_name)


class ReviewLoader:
    
    def __init__(self):
        self.product_lookup = database_manager.product_lookup_get()
        self.product_category_lookup = database_manager.product_category_lookup_get()
        
        self.product_descriptions = {}
        self.product_reviews = {}
        self.product_images = {}
        for product_name, product_id in self.product_lookup.items():
            
            with open(f'reviews/{product_name}/data.json', 'r') as file:
                product_data = json.loads(file.read())
            self.product_descriptions[product_id] = product_data['description']
            self.product_reviews[product_id] = product_data['reviews']
            
            with open(f'reviews/{product_name}/image.jpg', 'rb') as file:
                image = file.read()
            self.product_images[product_id] = image
        
        self.products = database_manager.products_get()
        self.reviews = database_manager.reviews_get()
        self.experiments = database_manager.experiments_get()
        self.metrics = database_manager.metrics_get()
        self.active_sessions = {}
        self.active_connections = {}


class MyRequestHandler(MyBaseRequestHandler):
    
    def request_handle(self, full_path):
        
        if full_path == ('GET', '/'):
            with open('website/static/home.html', 'rb') as file:
                data = file.read()
            self._send_html(data)
        
        elif full_path == ('GET', '/rules'):
            with open('website/static/rules.html', 'rb') as file:
                data = file.read()
            self._send_html(data)
        
        elif full_path == ('GET', '/products'):
            with open('website/static/products.html', 'rb') as file:
                data = file.read()
            self._send_html(data)
        
        elif full_path[0] == 'GET' and full_path[1] in ('/video-game', '/mattress', '/restaurant', '/shampoo', '/book'):
            with open('website/static/product_description.html', 'rb') as file:
                data = file.read()
            self._send_html(data)
        
        elif full_path[0] == 'GET' and full_path[1] in ('/video-game/guess', '/mattress/guess', '/restaurant/guess', '/shampoo/guess', '/book/guess'):
            with open('website/static/review.html', 'rb') as file:
                data = file.read()
            self._send_html(data)
        
        elif full_path == ('GET', '/thankyou'):
            with open('website/static/thankyou.html', 'rb') as file:
                data = file.read()
            self._send_html(data)

        elif full_path == ('GET', '/about/project'):
            with open('website/static/about_project.html', 'rb') as file:
                data = file.read()
            self._send_html(data)

        elif full_path == ('GET', '/about/author'):
            with open('website/static/about_author.html', 'rb') as file:
                data = file.read()
            self._send_html(data)

        elif full_path == ('GET', '/style_base.css'):
            with open('website/static/style_base.css', 'rb') as file:
                data = file.read()
            self._send_css(data)
        
        elif full_path == ('GET', '/style_home.css'):
            with open('website/static/style_home.css', 'rb') as file:
                data = file.read()
            self._send_css(data)
        
        elif full_path == ('GET', '/style_rules.css'):
            with open('website/static/style_rules.css', 'rb') as file:
                data = file.read()
            self._send_css(data)
        
        elif full_path == ('GET', '/style_products.css'):
            with open('website/static/style_products.css', 'rb') as file:
                data = file.read()
            self._send_css(data)
        
        elif full_path == ('GET', '/style_product_description.css'):
            with open('website/static/style_product_description.css', 'rb') as file:
                data = file.read()
            self._send_css(data)
        
        elif full_path == ('GET', '/style_review.css'):
            with open('website/static/style_review.css', 'rb') as file:
                data = file.read()
            self._send_css(data)
        
        elif full_path == ('GET', '/style_thankyou.css'):
            with open('website/static/style_thankyou.css', 'rb') as file:
                data = file.read()
            self._send_css(data)

        elif full_path == ('GET', '/style_about_project.css'):
            with open('website/static/style_about_project.css', 'rb') as file:
                data = file.read()
            self._send_css(data)

        elif full_path == ('GET', '/style_about_author.css'):
            with open('website/static/style_about_author.css', 'rb') as file:
                data = file.read()
            self._send_css(data)
            
        elif full_path == ('GET', '/script_base.js'):
            with open('website/static/script_base.js', 'rb') as file:
                data = file.read()
            self._send_js(data)
        
        elif full_path == ('GET', '/script_product_description.js'):
            with open('website/static/script_product_description.js', 'rb') as file:
                data = file.read()
            self._send_js(data)
        
        elif full_path == ('GET', '/script_review.js'):
            with open('website/static/script_review.js', 'rb') as file:
                data = file.read()
            self._send_js(data)
        
        # elif full_path == ('GET', '/admin/check-update'):
            # data = []
            
            # command = ['git', 'remote', 'update']
            # command_result = command_helper.command_run(command, cwd='../source')
            # data.append(command_result.asdict())
            
            # command = ['git', 'status', '-uno']
            # command_result = command_helper.command_run(command, cwd='../source')
            # data.append(command_result.asdict())
            
            # self._send_json(data)
        
        # elif full_path == ('GET', '/admin/deploy-update'):
            # command = ['git', 'pull']
            # command_result = command_helper.command_run(command, cwd='../source')
            # data = command_result.asdict()
            # self._send_chunked_json(data, first=True)
            
            # self.server.deployment_start()
            
            # command = ['python3', 'app/main.py', 'deploy']
            # command_result = command_helper.command_run(command, timeout=60, cwd='../source')
            # data = command_result.asdict()
            # self._send_chunked_json(data)
            
            # for i in range(2):
                # time.sleep(2)
                # self._send_chunked_json({'test': str(i)})
            
            # self._send_chunked_json(None)
            # self.server.deployment_finalize()
        
        elif full_path == ('POST', '/connection/create'):
            data = self._receive_json()
            creation_time = int(time.time())
            user_name = data.get('username')
            user_id = None
            
            if user_name is not None:
                user_name = user_name_helper.sanitize(user_name)
                try:
                    user_id = database_manager.user_id_get(user_name)
                except Exception as error:
                    pass

            if user_id is None:
                # Generate a random user name which doesn't exist yet and add it to the database
                for _ in range(100):
                    user_name = user_name_helper.generate_random()
                    try:
                        user_id = database_manager.user_create(user_name, creation_time)
                        break
                    except Exception as error:
                        pass
            
            if user_id is None:
                raise InternalError()

            connection_id = database_manager.connection_create(user_id, creation_time)
            # Generate a random hash that doesn't exist yet
            for _ in range(100):
                connection_hash = random.getrandbits(30)
                if connection_hash not in review_loader.active_connections:
                    break
                connection_hash = None
            
            if connection_hash is None:
                raise InternalError()

            connection = Connection(user_id=user_id)
            review_loader.active_connections[connection_hash] = connection
            
            data = {'username': user_name, 'hash': connection_hash}
            self._send_json(data)
        
        elif full_path == ('POST', '/session/create'):
            data = self._receive_json()
            creation_time = int(time.time())
            try:
                connection_hash = int(data['connectionHash'])
                connection = review_loader.active_connections[connection_hash]
                user_id = connection.user_id
            except Exception as error:
                raise InvalidRequestData('"connectionHash" needs to be a valid connection hash')
            try:
                category_name = data['category'].replace('-', '_')
                category_id = review_loader.product_category_lookup[category_name]
            except Exception as error:
                raise InvalidRequestData('"category" needs to be a valid category name')
            # Get the product with the most unguessed reviews
            unguessed_reviews = database_manager.unguessed_reviews_get(user_id, category_id)
            product_id = max(unguessed_reviews, key=lambda product_id: len(unguessed_reviews[product_id]))
            # Randomly get some unguessed reviews from that product
            review_ids = random.sample(unguessed_reviews[product_id], SESSION_REVIEW_COUNT)
            # Get a random experiment and its metric
            experiment_id, metric_id = random.choice(list(review_loader.experiments.items()))
            # Create the session in the database
            session_id = database_manager.session_create(user_id, metric_id, product_id, creation_time)
            session = Session(
                session_id=session_id,
                user_id=user_id,
                experiment_id=experiment_id,
                metric_id=metric_id,
                product_id=product_id,
                review_ids=review_ids
            )
            review_loader.active_sessions[user_id] = session
            product_name = review_loader.products[product_id]
            data = {'product': product_name}
            self._send_json(data)
        
        elif full_path == ('GET', '/product/description'):
            data = self._receive_json()
            try:
                product_name = data['product'].replace('-', '_')
                product_id = review_loader.product_lookup[product_name]
                product_description = review_loader.product_descriptions[product_id]
            except Exception as e:
                raise InvalidRequestData('"product" needs to be a valid product name')
            self._send_json(product_description)
        
        elif full_path == ('GET', '/product/image'):
            data = self._receive_json()
            try:
                product_name = data['product'].replace('-', '_')
                product_id = review_loader.product_lookup[product_name]
                image = review_loader.product_images[product_id]
            except Exception as e:
                raise InvalidRequestData('"product" needs to be a valid product name')
            self._send_image(image)
        
        elif full_path == ('GET', '/reviews'):
            data = self._receive_json()
            try:
                connection_hash = int(data['connectionHash'])
                connection = review_loader.active_connections[connection_hash]
                user_id = connection.user_id
                session = review_loader.active_sessions[user_id]
            except Exception as error:
                raise InvalidRequestData('"connectionHash" needs to be a valid connection hash')
            reviews = []
            for review_id in session.review_ids:
                product_id, position = review_loader.reviews[review_id]
                review = review_loader.product_reviews[product_id][position]
                reviews.append(review)
            question = review_loader.metrics[session.metric_id]
            data = {'question': question, 'reviews': reviews}
            self._send_json(data)
        
        elif full_path == ('PUT', '/review/rate'):
            data = self._receive_json()
            try:
                connection_hash = int(data['connectionHash'])
                connection = review_loader.active_connections[connection_hash]
                user_id = connection.user_id
                session = review_loader.active_sessions[user_id]
            except Exception as error:
                raise InvalidRequestData('"connectionHash" needs to be a valid connection hash')
            try:
                rating = int(data['rating'])
                if rating not in range(11):
                    raise Exception()
            except Exception as e:
                raise InvalidRequestData('"rating" needs to be a valid integer')
            try:
                index = int(data['index'])
                review_id = session.review_ids[index]
            except Exception as e:
                raise InvalidRequestData('"index" needs to be a valid integer')
            try:
                duration_ms = int(1000*data['duration'])
                if duration_ms < 0:
                    raise Exception()
            except Exception as e:
                raise InvalidRequestData('"duration" needs to be a valid duration')
            database_manager.guess_create(session.session_id, review_id, rating, duration_ms)
            
            self._send_json({})

        elif full_path == ('GET', '/favicon.ico'):
            with open('website/static/icon.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/stars_1_5.svg'):
            with open('website/static/stars_1_5.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/stars_2_5.svg'):
            with open('website/static/stars_2_5.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/stars_3_5.svg'):
            with open('website/static/stars_3_5.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/stars_4_5.svg'):
            with open('website/static/stars_4_5.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/stars_5_5.svg'):
            with open('website/static/stars_5_5.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/thumb_up.svg'):
            with open('website/static/thumb_up.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/thumb_down.svg'):
            with open('website/static/thumb_down.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/copy_icon.svg'):
            with open('website/static/copy_icon.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/pdf_icon.svg'):
            with open('website/static/pdf_icon.svg', 'rb') as file:
                image = file.read()
            self._send_svg(image)

        elif full_path == ('GET', '/author-image.jpg'):
            with open('website/static/author_image.jpg', 'rb') as file:
                image = file.read()
            self._send_image(image)

        elif full_path == ('GET', '/cv-english.pdf'):
            with open('website/static/cv_english.pdf', 'rb') as file:
                data = file.read()
            self._send_pdf(data)

        elif full_path == ('GET', '/cv-french.pdf'):
            with open('website/static/cv_french.pdf', 'rb') as file:
                data = file.read()
            self._send_pdf(data)

        else:
            print(f'Unhandled method and path:\n{full_path}')


database_manager = DatabaseManager()
database_manager.open()
user_name_helper = UserNameHelper()
review_loader = ReviewLoader()

