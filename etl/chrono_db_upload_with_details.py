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
    listings = list(chrono24.query(category).search_detail(40000))  # Convert the generator to a list
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
            INSERT INTO chrono.watch_details (
                listing_id, production_year, delivery_scope, availability, case_diameter, bracelet_color, anticipated_delivery, merchant_rating, merchant_reviews, date_gathered) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        

        for watch in watch_data:
            # Extract and convert listing_id to an integer
            listing_id = int(watch.get('id', '0'))  # Convert the id from string to int
            production_year = watch.get('year_of_production', 'Unknown')
            delivery_scope = watch.get('scope_of_delivery', 'Unknown')
            availability = watch.get('availability', 'Unknown')
            case_diameter = watch.get('case_diameter', 'Unknown')
            bracelet_color = watch.get('bracelet_color', 'Unknown')
            anticipated_delivery = watch.get('anticipated_delivery', 'Unknown')

            # Ensure the merchant rating  are numeric
            try:
                merchant_rating = float(watch.get('merchant_rating', '0').replace('$', '').replace(',', ''))
            except ValueError:
                merchant_rating = 0.0

            try:
                merchant_reviews = float(watch.get('merchant_reviews', '0').replace('$', '').replace(',', ''))
            except ValueError:
                merchant_reviews = 0

            # Check if the listing_id already exists in the database
            
            # Execute the insert query with the current date for date_gathered
            cursor.execute(insert_query, (
                    listing_id, production_year, delivery_scope, availability, case_diameter, bracelet_color, anticipated_delivery, merchant_rating, merchant_reviews, current_date
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
