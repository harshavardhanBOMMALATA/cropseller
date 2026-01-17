import csv
from database.models import Order, User, Product, Bidding

def run():
    with open("orders.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            Order.objects.update_or_create(
                order_id=row["order_id"],
                defaults={
                    "verdict": row["verdict"],
                    "user": User.objects.get(user_id=int(row["user_id"])),
                    "product": Product.objects.get(product_id=int(row["product_id"])),
                    "bidding": Bidding.objects.get(bidding_id=row["bidding_id"]),
                }
            )
