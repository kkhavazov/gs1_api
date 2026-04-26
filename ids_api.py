from keys import gs1_token

import requests
import time

# --- Configuration ---
BASE_URL = "https://serviceplattform.gs1.de/api/master_data_service/v1/product"
TOKEN = gs1_token
OUTPUT_FILE = "product_ids.txt"
TOTAL_PAGES = 654
PAGE_SIZE = 10  # Standard GS1 page size, adjust if your limit is higher

headers = {
    'Authorization': f'Bearer {gs1_token}',
    'Content-Type': 'application/json',
    'Accept': '*/*',
}

def fetch_ids():
    with requests.Session() as session:
        session.headers.update(headers)
        
        with open(OUTPUT_FILE, "a") as f:
            for page in range(1, TOTAL_PAGES + 1):
                params = {"page": page, "pageSize": PAGE_SIZE}
                
                try:
                    response = session.get(BASE_URL, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        ids = []
                        for prod in response.json().get("content",[]):
                            f.write(f"{prod["id"]}\n")
                        
                        print(f"Successfully processed page {page}/{TOTAL_PAGES}")
                        
                    elif response.status_code == 429:
                        print("Rate limit hit! Sleeping for 60 seconds...")
                        time.sleep(60)
                    else:
                        print(f"Error on page {page}: {response.status_code}")
                
                except Exception as e:
                    print(f"Connection error on page {page}: {e}")
                    time.sleep(5) # Brief pause before retrying

if __name__ == "__main__":
    fetch_ids()