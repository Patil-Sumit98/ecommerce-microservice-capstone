import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os

# Database connection parameters (matches your docker-compose.yaml)
DB_PARAMS = {
    "host": "localhost",
    "port": "5432",
    "dbname": "productdb",
    "user": "user",
    "password": "password"
}

CSV_FILENAME = 'product_catalog.csv'

def setup_database_and_load_data():
    if not os.path.exists(CSV_FILENAME):
        print(f"Error: {CSV_FILENAME} not found. Run generate_data.py first.")
        return

    # 1. Read the CSV
    df = pd.read_csv(CSV_FILENAME)
    print(f"Loaded {len(df)} products from CSV.")

    conn = None
    try:
        # 2. Connect to Postgres container
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # 3. Create Tables (Schema)
        print("Creating database schema...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            );
        """)

        # 4. Insert Unique Categories
        unique_categories = df['category'].unique()
        category_insert_query = "INSERT INTO categories (name) VALUES %s ON CONFLICT (name) DO NOTHING;"
        execute_values(cursor, category_insert_query, [(cat,) for cat in unique_categories])
        
        # 5. Fetch Category IDs to map to products
        cursor.execute("SELECT category_id, name FROM categories;")
        category_map = {name: cat_id for cat_id, name in cursor.fetchall()}
        
        # Map the string category to the integer category_id
        df['category_id'] = df['category'].map(category_map)
        
        # Prepare final product data
        product_data = df[['product_id', 'name', 'description', 'price', 'category_id']].to_numpy()

        # 6. Insert Products
        print("Inserting product data...")
        product_insert_query = """
            INSERT INTO products (product_id, name, description, price, category_id)
            VALUES %s
            ON CONFLICT (product_id) DO NOTHING;
        """
        execute_values(cursor, product_insert_query, product_data)

        # Commit all changes
        conn.commit()
        print("Data loaded successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    setup_database_and_load_data()