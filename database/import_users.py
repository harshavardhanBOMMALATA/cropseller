import csv
from database.models import User

def run():
    with open("users.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            User.objects.update_or_create(
                user_id=int(row["user_id"]),
                defaults={
                    "name": row["name"],
                    "password": row["password"],
                    "phone_number": row["phone_number"],
                    "address": row["address"],
                    "email": row["email"],
                    "photo": row["photo"],
                }
            )
