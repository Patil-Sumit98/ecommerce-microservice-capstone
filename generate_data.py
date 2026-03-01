import pandas as pd
from faker import Faker
import random
import os

fake = Faker()

def generate_product_data(num_products=100):
    products = []
    categories = ['Electronics', 'Apparel', 'Home Goods', 'Books', 'Toys', 'Groceries', 'Beauty']
    
    for i in range(1, num_products + 1):
        products.append({
            'product_id': f'PROD-{i:05d}',
            'name': fake.catch_phrase(),
            'description': fake.paragraph(nb_sentences=random.randint(3, 7)),
            'price': round(random.uniform(5.00, 500.00), 2),
            'category': random.choice(categories)
        })
        
    return pd.DataFrame(products)

if __name__ == '__main__':
    product_df = generate_product_data(num_products=100)
    csv_filename = 'product_catalog.csv'
    product_df.to_csv(csv_filename, index=False)
    print(f"Generated '{csv_filename}' with {len(product_df)} products.")