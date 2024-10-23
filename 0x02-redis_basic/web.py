#!/usr/bin/env python3
'''This module with tools for request caching and tracking.'''
import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()

def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data.'''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output.'''
        redis_store.incr(f'count:{url}')  # Increment the count for the URL
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')  # Decode the result if it exists in cache
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError if the status is 4xx, 5xx
            result = response.text
            redis_store.setex(f'result:{url}', 10, result.encode('utf-8'))  # Store the result in cache
            return result
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return ""
    return invoker

@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.'''
    pass  # The actual implementation is handled by the data_cacher decorator

if __name__ == "__main__":
    # Example usage
    url = "http://example.com"
    page_content = get_page(url)
    print(page_content)
