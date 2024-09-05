import chrono24
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import time

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

def get_watch_prices(category):
    # Query the Chrono24 API using the category
    listings = list(chrono24.query(category).search(40000))  # Convert the generator to a list
    return listings

def insert_watch_data(watch_data, category):
    try:
        # Establish database connection
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get the current date for the date_gathered field
        current_date = time.strftime('%Y-%m-%d')
        
        # SQL insert query with schema name
        insert_query = """
            INSERT INTO chrono.watch_prices (
                listing_id, category, brand, model, price, shipping_price, certification_status, 
                currency, condition, description, url, merchant_name, location, badge, image_url, date_gathered
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # SQL query to check if the listing_id already exists in the database
        check_query = "SELECT 1 FROM chrono.watch_prices WHERE listing_id = %s"

        for watch in watch_data:
            # Extract and convert listing_id to an integer
            listing_id = int(watch.get('id', '0'))  # Convert the id from string to int
            brand = watch.get('manufacturer', 'Unknown')
            model = watch.get('title', 'Unknown')

            # Ensure the price and shipping price are numeric
            try:
                price = float(watch.get('price', '0').replace('$', '').replace(',', ''))
            except ValueError:
                price = 0.0

            try:
                shipping_price = float(watch.get('shipping_price', '0').replace('$', '').replace(',', ''))
            except ValueError:
                shipping_price = 0.0

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

            # check if the listing_id already exists in the database
            cursor.execute(check_query, (listing_id,))
            exists = cursor.fetchone()

            if not exists:
                # Execute the insert query with the current date for date_gathered
                cursor.execute(insert_query, (
                    listing_id, category, brand, model, price, shipping_price, certification_status, 
                    currency, condition, description, url, merchant_name, location, badge, single_image_url, current_date
                ))
        
        # Commit the transaction
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Inserted {len(watch_data)} records for category {category}")
    
    except Exception as e:
        print(f"Error inserting data: {e}")

# Main function to gather data and insert it into the database
def main():
    for category in CATEGORIES:
        watch_data = get_watch_prices(category)
        if watch_data:
            insert_watch_data(watch_data, category)
            time.sleep(5)  # Sleep for 5 seconds after processing each category

if __name__ == "__main__":
    main()
