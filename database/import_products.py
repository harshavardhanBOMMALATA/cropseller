import csv
from database.models import Product, User
from django.utils import timezone

def run():
    with open("products.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            Product.objects.update_or_create(
                product_id=int(row["product_id"]),
                defaults={
                    "product_name": row["product_name"],
                    "quantity": int(row["quantity"]),
                    "location": row["location"],
                    "delivery": row["delivery"],
                    "price_per_kg": row["price_per_kg"],
                    "photo_url": row["photo_url"],
                    "description": row["description"],
                    "fssai_license": row["fssai_license"],
                    "organic_certified": row["organic_certified"],
                    "moisture": row["moisture"],
                    "crop_year": row["crop_year"],
                    "packaging": row["packaging"],
                    "supply_capacity": row["supply_capacity"],
                    "enddate": row["enddate"],
                    "created_at": timezone.now(),
                    "user": User.objects.get(user_id=int(row["user_id"])),
                }
            )
