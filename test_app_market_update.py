
import sys
import os
import logging

# Add the project directory to sys.path
sys.path.append(os.getcwd())

# Configure logging to capture output
logging.basicConfig(level=logging.INFO)

from app import update_global_market_data, global_market_cache

def test_app_update():
    print("Testing update_global_market_data()...")
    success = update_global_market_data()
    
    print(f"\nUpdate Success: {success}")
    print(f"Cache Data: {global_market_cache['data']}")
    
    if global_market_cache['data']:
        print(f"Indices: {global_market_cache['data'].get('indices')}")
        print(f"Themes: {global_market_cache['data'].get('themes')}")
    else:
        print("Cache is empty.")

if __name__ == "__main__":
    test_app_update()
