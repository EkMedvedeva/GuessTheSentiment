from base_request_handler import MyBaseRequestHandler, InvalidRequestData, InternalError
import json
import random
import command_helper
import time


class ReviewLoader:

    def __init__(self):
        with open('reviews/mattress/data.json', 'r') as file:
            mattress_data = json.loads(file.read())
        
        self.product = mattress_data['product']
        self.reviews = mattress_data['reviews']

    def get_random_review(self):
        return random.choice(self.reviews)


class MyRequestHandler(MyBaseRequestHandler):
    
    def request_handle(self, full_path):
        
        if full_path == ('GET', '/'):
            with open('website/static/home.html', 'rb') as file:
                data = file.read()
            self._send_html(data)
        
        elif full_path == ('GET', '/style.css'):
            with open('website/static/style.css', 'rb') as file:
                data = file.read()
            self._send_css(data)
        
        elif full_path == ('GET', '/script.js'):
            with open('website/static/script.js', 'rb') as file:
                data = file.read()
            self._send_js(data)
        
        elif full_path == ('GET', '/review'):
            review = review_loader.get_random_review()
            review_rating = review['rating']
            review_title = review['title']
            review_text = review['review']
            data = {
                'product': review_loader.product['name'],
                'product_description': review_loader.product['description'],
                'review': f'Rating: {review_rating}/5\nTitle: {review_title}\nComment: {review_text}'
            }
            self._send_json(data)
        
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
            
            command = ['python3', 'deployment/deployment_manager.py']
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

