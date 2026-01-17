import csv
from database.models import Bidding, User, Product

def run():
    with open("biddings.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            Bidding.objects.update_or_create(
                bidding_id=row["bidding_id"],
                defaults={
                    "bid_price": row["bid_price"],
                    "bid_quantity": int(row["bid_quantity"]),
                    "created_time": row["created_time"],
                    "verdict": row["verdict"],
                    "user": User.objects.get(user_id=int(row["user_id"])),
                    "product": Product.objects.get(product_id=int(row["product_id"])),
                }
            )
