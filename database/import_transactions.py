import csv
from database.models import Transaction, Order
from django.utils import timezone

def run():
    with open("transactions.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            Transaction.objects.update_or_create(
                transaction_id=row["transaction_id"],
                defaults={
                    "payment_method": row["payment_method"],
                    "amount": row["amount"],
                    "status": row["status"],
                    "transaction_date": timezone.now(),
                    "order": Order.objects.get(order_id=row["order_id"]),
                }
            )
