import json
import random
import time

from server.base_request_handler import MyBaseRequestHandler, InvalidRequestData, InternalError
from helpers import command_helper


class ReviewLoader:

    def __init__(self):
        self.products = {}
        self.images = {}
        for product_name in ('mattress', 'no_mans_sky'):
            
            with open(f'reviews/{product_name}/data.json', 'r') as file:
                product_data = json.loads(file.read())
            self.products[product_name] = product_data
            
            with open(f'reviews/{product_name}/image.jpg', 'rb') as file:
                image = file.read()
            self.images[product_name] = image

    def get_random_review(self):
        return random.choice(self.reviews)


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
        
        elif full_path[0] == 'GET' and full_path[1].startswith('/products/'):
            with open('website/static/product_description.html', 'rb') as file:
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
        
        elif full_path == ('GET', '/script.js'):
            with open('website/static/script.js', 'rb') as file:
                data = file.read()
            self._send_js(data)
        
        elif full_path == ('GET', '/script_product_description.js'):
            with open('website/static/script_product_description.js', 'rb') as file:
                data = file.read()
            self._send_js(data)
        
##        elif full_path == ('GET', '/review'):
##            review = review_loader.get_random_review()
##            review_rating = review['rating']
##            review_title = review['title']
##            review_text = review['review']
##            data = {
##                'product': review_loader.product['name'],
##                'product_description': review_loader.product['description'],
##                'review': f'Rating: {review_rating}/5\nTitle: {review_title}\nComment: {review_text}'
##            }
##            self._send_json(data)
        
        elif full_path[0] == 'GET' and full_path[1].startswith('/product-descriptions/'):
            product_name = full_path[1].split('/', maxsplit=2)[2].replace('-', '_')
            if product_name not in review_loader.products:
                raise InvalidRequestData(f"Unknown product '{product_name}'")
            product_data = review_loader.products[product_name]['product']
            self._send_json(product_data)
        
        elif full_path[0] == 'GET' and full_path[1].startswith('/product-images/'):
            product_name = full_path[1].split('/', maxsplit=2)[2].replace('-', '_')
            if product_name not in review_loader.products:
                raise InvalidRequestData(f"Unknown product '{product_name}'")
            image = review_loader.images[product_name]
            self._send_image(image)
        
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

            for i in range(10):
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


review_loader = ReviewLoader()

