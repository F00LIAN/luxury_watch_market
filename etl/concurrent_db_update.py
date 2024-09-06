import chrono24
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm
import concurrent.futures

# Load environment variables from a .env file
load_dotenv()

# Database Connection Manager
class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }

    def get_connection(self):
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None

    def close_connection(self, conn, cursor):
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Watch Data Fetcher
class WatchDataFetcher:
    @staticmethod
    def get_basic_watch_prices(category):
        try:
            return list(chrono24.query(category).search(10000))  # Convert generator to list
        except Exception as e:
            print(f"Error fetching basic data for {category}: {e}")
            return []

    @staticmethod
    def get_detailed_watch_prices(category):
        try:
            return list(chrono24.query(category).search_detail(10000))  # Convert generator to list
        except Exception as e:
            print(f"Error fetching detailed data for {category}: {e}")
            return []

# Data Inserter
class DataInserter:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def insert_basic_watch_data(self, watch_data, category):
        conn = self.db_manager.get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        current_date = time.strftime('%Y-%m-%d')

        try:
            for watch in tqdm(watch_data, desc=f"Processing Basic {category}", unit="watch"):
                listing_id = str(watch.get('id', '0'))
                brand = watch.get('manufacturer', 'Unknown')
                model = watch.get('title', 'Unknown')
                price = float(watch.get('price', '0').replace('$', '').replace(',', '')) if watch.get('price') else 0.0
                shipping_price = float(watch.get('shipping_price', '0').replace('$', '').replace(',', '')) if watch.get('shipping_price') else 0.0
                certification_status = watch.get('certification_status', 'Unknown')
                description = watch.get('description', 'No description available')
                url = watch.get('url', '')
                merchant_name = watch.get('merchant_name', 'Unknown')
                location = watch.get('location', 'Unknown')
                image_urls = watch.get('image_urls', [])
                single_image_url = image_urls[0] if image_urls else ''

                cursor.execute("""
                    INSERT INTO chrono.watch_prices (
                        listing_id, category, brand, model, price, shipping_price, certification_status, description, 
                        url, merchant_name, location, image_url, date_gathered
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    listing_id, category, brand, model, price, shipping_price, certification_status, description,
                    url, merchant_name, location, single_image_url, current_date
                ))

            conn.commit()
            print(f"Processed {len(watch_data)} basic records for category {category}")
        except Exception as e:
            print(f"Error inserting basic data: {e}")
        finally:
            self.db_manager.close_connection(conn, cursor)

    def insert_detailed_watch_data(self, watch_data, category):
        conn = self.db_manager.get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        current_date = time.strftime('%Y-%m-%d')

        try:
            for watch in tqdm(watch_data, desc=f"Processing Detailed {category}", unit="watch"):
                listing_id = str(watch.get('id', '0'))
                production_year = watch.get('year_of_production', 'Unknown')
                delivery_scope = watch.get('scope_of_delivery', 'Unknown')
                availability = watch.get('availability', 'Unknown')
                case_diameter = watch.get('case_diameter', 'Unknown')
                bracelet_color = watch.get('bracelet_color', 'Unknown')
                anticipated_delivery = watch.get('anticipated_delivery', 'Unknown')
                merchant_rating = watch.get('merchant_rating', '0').replace(',', '') if watch.get('merchant_rating') else '0'
                merchant_reviews = watch.get('merchant_reviews', '0').replace(',', '') if watch.get('merchant_reviews') else '0'

                cursor.execute("""
                    INSERT INTO chrono.watch_details (
                        listing_id, production_year, delivery_scope, availability, case_diameter, bracelet_color, 
                        anticipated_delivery, merchant_rating, merchant_reviews, date_gathered
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    listing_id, production_year, delivery_scope, availability, case_diameter, bracelet_color,
                    anticipated_delivery, merchant_rating, merchant_reviews, current_date
                ))

            conn.commit()
            print(f"Processed {len(watch_data)} detailed records for category {category}")
        except Exception as e:
            print(f"Error inserting detailed data: {e}")
        finally:
            self.db_manager.close_connection(conn, cursor)

# Main Update Runner
class WatchPriceUpdater:
    def __init__(self):
        self.categories = ["Rolex", "Richard Mille", "Seiko", "Omega", "Patek Philippe", "Panerai", "Breitling", "Audemars Piguet"]
        self.data_fetcher = WatchDataFetcher()
        self.data_inserter = DataInserter()

    def update_watch_prices(self):
        start_time = time.time()

        for category in tqdm(self.categories, desc="Categories"):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Fetch and process both basic and detailed data in parallel
                basic_future = executor.submit(self.data_fetcher.get_basic_watch_prices, category)
                detailed_future = executor.submit(self.data_fetcher.get_detailed_watch_prices, category)

                # Wait for both to complete
                basic_watch_data = basic_future.result()
                detailed_watch_data = detailed_future.result()

                # Insert data into respective tables
                if basic_watch_data:
                    self.data_inserter.insert_basic_watch_data(basic_watch_data, category)
                if detailed_watch_data:
                    self.data_inserter.insert_detailed_watch_data(detailed_watch_data, category)

                time.sleep(5)  # Sleep for 5 seconds between category queries

        total_runtime = time.time() - start_time
        print(f"Total runtime: {total_runtime:.2f} seconds")

# Final callable function
def run_update():
    updater = WatchPriceUpdater()
    updater.update_watch_prices()

# If running as a script
if __name__ == "__main__":
    run_update()
