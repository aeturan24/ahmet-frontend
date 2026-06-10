import requests
import os
import time
import threading
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

def run_server():
    port = int(os.environ.get("PORT", 10000))
    # use_reloader=False prevents Flask from running twice in a thread
    app.run(host="0.0.0.0", port=port, use_reloader=False)

def fetch_data():
    api_url = os.getenv("STRAPI_API_URL", "")
    api_token = os.getenv("STRAPI_API_TOKEN", "")
    
    if not api_url or not api_token:
        print("Error: API URL or Token is missing.")
        return

    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        print("Fetching cities from Strapi backend...")
        response = requests.get(f"{api_url}/api/cities", headers=headers, params={"locale": "tr"}, timeout=10)
        if response.status_code == 200:
            cities_data = response.json().get('data', [])
            if not cities_data:
                print("No cities found.")
            for city in cities_data:
                c_attr = city['attributes']
                print(f"\n[CITY] {c_attr['name']} ({c_attr['country']})")
                print(f"Description: {c_attr.get('description', '')}")
                
                places_params = {
                    "filters[city][id][$eq]": city['id'],
                    "locale": "tr",
                    "populate": "image"
                }
                places_response = requests.get(f"{api_url}/api/places", headers=headers, params=places_params, timeout=10)
                if places_response.status_code == 200:
                    places_data = places_response.json().get('data', [])
                    for place in places_data:
                        p_attr = place['attributes']
                        rating = p_attr.get('rating', '0.0')
                        print(f"  -> [PLACE] {p_attr['name']} (Rating: {rating}/10)")
                else:
                    print(f"  -> Failed to fetch places for {c_attr['name']}")
        else:
            print(f"Failed to fetch cities: HTTP {response.status_code}")
    except Exception as e:
        print(f"Connection Error: {e}")

def bot_task():
    print("Starting background bot...")
    fetch_data()
    print("Data fetch task finished. Entering background sleep loop...")
    while True:
        time.sleep(60)
        print("Bot is alive and waiting...")

if __name__ == "__main__":
    # Start the Flask web server in a background thread to satisfy Render's port binding requirement
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Run the main bot logic in the main thread
    bot_task()
