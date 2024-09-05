import chrono24
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm

# Load environment variables from a .env file
load_dotenv()

# Configuration for the PostgreSQL database connection
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Categories to query from the Chrono24 API
CATEGORIES = ["Rolex", "Richard Mille", "Seiko", "Omega", "Patek Philippe", "Panerai", "Breitling", "Audemars Piguet"]

def get_db_connection():
    """Establish and return a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error establishing database connection: {e}")
        return None

def get_watch_prices(category):
    """Query watch prices from the Chrono24 API."""
    listings = list(chrono24.query(category).search(40000))  # Convert the generator to a list
    return listings

def insert_or_update_watch_data(watch_data, category, conn):
    """Insert or update watch data in the PostgreSQL database."""
    try:
        cursor = conn.cursor()
        
        # Get the current date for the date_gathered field
        current_date = time.strftime('%Y-%m-%d')

        # Wrap the loop with tqdm for a progress bar
        for watch in tqdm(watch_data, desc=f"Processing {category}", unit="watch"):
            # Extract and convert listing_id to a string
            listing_id = str(watch.get('id', '0'))
            brand = watch.get('manufacturer', 'Unknown')
            model = watch.get('title', 'Unknown')

            try:
                price = float(watch.get('price', '0').replace('$', '').replace(',', ''))
            except ValueError:
                price = 0.0

            try:
                shipping_price = float(watch.get('shipping_price', '0').replace('$', '').replace(',', ''))
            except ValueError:
                shipping_price = 0.0

            if price > 0:
                certification_status = watch.get('certification_status', 'Unknown')
                currency = 'USD'  # Assuming USD as default
                condition = 'Unknown'
                description = watch.get('description', 'No description available')
                url = watch.get('url', '')
                merchant_name = watch.get('merchant_name', 'Unknown')
                location = watch.get('location', 'Unknown')
                badge = watch.get('badge', 'Unknown')

                # Just grab the first image
                image_urls = watch.get('image_urls', [])
                single_image_url = image_urls[0] if image_urls else ''

                # Check if the listing already exists in the database for today's date
                cursor.execute("""
                    SELECT price FROM chrono.watch_prices 
                    WHERE listing_id = %s AND date_gathered = %s
                """, (listing_id, current_date))

                result = cursor.fetchone()

                if result:
                    # If the price has changed, update the existing record
                    if result[0] != price:
                        cursor.execute("""
                            UPDATE chrono.watch_prices
                            SET price = %s
                            WHERE listing_id = %s AND date_gathered = %s
                        """, (price, listing_id, current_date))
                else:
                    # Insert new record if not found or if it's a new listing
                    cursor.execute("""
                        INSERT INTO chrono.watch_prices (
                            listing_id, category, brand, model, price, shipping_price, certification_status, 
                            currency, condition, description, url, merchant_name, location, badge, image_url, date_gathered
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        listing_id, category, brand, model, price, shipping_price, certification_status, 
                        currency, condition, description, url, merchant_name, location, badge, single_image_url, current_date
                    ))
        
        # Commit the transaction
        conn.commit()
        print(f"Processed {len(watch_data)} records for category {category}")
    
    except Exception as e:
        print(f"Error processing data: {e}")
        conn.rollback()

def process_categories():
    """Process all categories by fetching and updating watch data."""
    start_time = time.time()  # Capture start time

    conn = get_db_connection()
    if conn is None:
        return

    # Wrap the outer loop with tqdm for a progress bar for categories
    for category in tqdm(CATEGORIES, desc="Categories"):
        watch_data = get_watch_prices(category)
        if watch_data:
            insert_or_update_watch_data(watch_data, category, conn)
            time.sleep(5)  # Sleep for 5 seconds after processing each category

    conn.close()

    end_time = time.time()  # Capture end time
    total_runtime = end_time - start_time  # Calculate total runtime
    print(f"Total runtime: {total_runtime:.2f} seconds")

def run_update():
    """Function to be called elsewhere in the code to trigger the update process."""
    process_categories()

if __name__ == "__main__":
    run_update()