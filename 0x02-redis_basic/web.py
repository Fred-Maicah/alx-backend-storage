#!/usr/bin/env python3
'''This module provides tools for request caching and tracking.'''
import redis
import requests
from functools import wraps
from typing import Callable

# Create a Redis client connection
redis_store = redis.Redis()

def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data and tracks URL access count.'''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output.'''
        redis_store.incr(f'count:{url}')  # Increment the access count for the URL
        cached_result = redis_store.get(f'result:{url}')
        
        # If cached result exists, return it
        if cached_result:
            return cached_result.decode('utf-8')
        
        # Fetch the URL content if not cached
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            result = response.text
            
            # Cache the result with a 10-second expiration time
            redis_store.setex(f'result:{url}', 10, result.encode('utf-8'))
            return result
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return ""
    
    return invoker

@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.'''
    pass  # The implementation is handled by the data_cacher decorator

if __name__ == "__main__":
    # Example usage
    url = "http://slowwly.robertomurray.co.uk"  # Use slowwly for simulating slow response
    page_content = get_page(url)
    print(page_content)
