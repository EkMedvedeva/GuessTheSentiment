import json
import random
import time

from server.base_request_handler import MyBaseRequestHandler, InvalidRequestData, InternalError
from helpers import command_helper


class ReviewLoader:

    def __init__(self):
        self.product_categories = {}
        self.products = {}
        self.images = {}
        for product_name in ('mattress', 'no_mans_sky'):
            
            with open(f'reviews/{product_name}/data.json', 'r') as file:
                product_data = json.loads(file.read())
            product_data['description']['image'] = f'/product-images/{product_name}'
            
            category = product_data['database']['category']
            self.products[product_name] = product_data
            # If the category doesn't exist yet, create the category with an empty list
            if category not in self.product_categories:
                self.product_categories[category] = []
            self.product_categories[category].append(product_name)
            
            with open(f'reviews/{product_name}/image.jpg', 'rb') as file:
                image = file.read()
            self.images[product_name] = image

    def get_random_product(self, category):
        return random.choice(self.product_categories[category])
    
    def get_random_review(self, product_name):
        return random.choice(self.products[product_name]['reviews'])


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
        
        elif full_path[0] == 'GET' and full_path[1] in ('/video-game', '/mattress'):
            with open('website/static/product_description.html', 'rb') as file:
                data = file.read()
            self._send_html(data)
        
        elif full_path[0] == 'GET' and full_path[1] in ('/video-game/guess', '/mattress/guess'):
            with open('website/static/review.html', 'rb') as file:
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
        
        elif full_path == ('GET', '/script.js'):
            with open('website/static/script.js', 'rb') as file:
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
            
        elif full_path == ('GET', '/product-description'):
            data = self._receive_json()
            try:
                category_name = data['category'].replace('-', '_')
                product_name = review_loader.get_random_product(category_name)
            except Exception as e:
                raise InvalidRequestData('"category" needs to be a valid category name')
            product_description = review_loader.products[product_name]['description']
            self._send_json(product_description)
        
        elif full_path[0] == 'GET' and full_path[1].startswith('/product-images/'):
            product_name = full_path[1].split('/', maxsplit=2)[2].replace('-', '_')
            if product_name not in review_loader.products:
                raise InvalidRequestData(f'Unknown product "{product_name}"')
            image = review_loader.images[product_name]
            self._send_image(image)
        
        elif full_path == ('GET', '/review'):
            data = self._receive_json()
            try:
                category_name = data['category'].replace('-', '_')
                product_name = review_loader.get_random_product(category_name)
                review = review_loader.get_random_review(product_name)
            except Exception as e:
                raise InvalidRequestData('"category" needs to be a valid category name')
            self._send_json(review)
        
        elif full_path == ('GET', '/admin/check-update'):
            data = []
            
            command = ['git', 'remote', 'update']
            command_result = command_helper.command_run(command, cwd='../source')
            data.append(command_result.asdict())
            
            command = ['git', 'status', '-uno']
            command_result = command_helper.command_run(command, cwd='../source')
            data.append(command_result.asdict())
            
            self._send_json(data)
        
        elif full_path == ('GET', '/admin/deploy-update'):
            command = ['git', 'pull']
            command_result = command_helper.command_run(command, cwd='../source')
            data = command_result.asdict()
            self._send_chunked_json(data, first=True)
            
            self.server.deployment_start()
            
            command = ['python3', 'app/main.py', 'deploy']
            command_result = command_helper.command_run(command, timeout=60, cwd='../source')
            data = command_result.asdict()
            self._send_chunked_json(data)

            for i in range(2):
                time.sleep(2)
                self._send_chunked_json({'test': str(i)})
            
            self._send_chunked_json(None)
            self.server.deployment_finalize()

        elif full_path == ('PUT', '/rate'):
            data = self._receive_json()
            try:
                rating = int(data['rating'])
            except Exception as e:
                raise InvalidRequestData('rating needs to be an integer')
            self._send_json({})

        elif full_path == ('GET', '/favicon.ico'):
            pass

        else:
            print(f'Unhandled method and path:\n{full_path}')


review_loader = ReviewLoader()

