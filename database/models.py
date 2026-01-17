from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    email = models.EmailField(max_length=255)
    photo = models.CharField(max_length=255)


class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    location = models.CharField(max_length=150)
    delivery = models.CharField(max_length=200)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    photo_url = models.URLField(max_length=500)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    created_at = models.DateTimeField()

    # NEW COLUMNS
    description = models.CharField(max_length=500)
    fssai_license = models.CharField(max_length=200)
    organic_certified = models.CharField(max_length=200)
    moisture = models.CharField(max_length=200)
    crop_year = models.CharField(max_length=200)
    packaging = models.CharField(max_length=200)
    supply_capacity = models.CharField(max_length=200)
    enddate=models.CharField(max_length=200)




    def __str__(self):
        return self.product_name


class Bidding(models.Model):
    bidding_id = models.CharField(max_length=100, primary_key=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    bid_price = models.DecimalField(max_digits=10, decimal_places=2)
    bid_quantity = models.IntegerField()
    created_time = models.CharField(max_length=100)

    # ✅ NEW COLUMN
    verdict = models.CharField(max_length=20)

    def __str__(self):
        return self.bidding_id


class Order(models.Model):
    order_id = models.CharField(max_length=10, primary_key=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_id'
    )

    bidding = models.ForeignKey(
        Bidding,
        on_delete=models.CASCADE,
        db_column='bidding_id'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )

    verdict = models.CharField(max_length=20)


    def __str__(self):
        return self.order_id


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=10, primary_key=True)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column='order_id'
    )

    payment_method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20)
    transaction_date = models.DateTimeField()


    def __str__(self):
        return self.transaction_id


class Transportation(models.Model):
    transportation_id = models.CharField(max_length=10, primary_key=True)

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column='order_id'
    )

    vehicle_number = models.CharField(max_length=20)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)

    start_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    start_longitude = models.DecimalField(max_digits=10, decimal_places=7)

    current_latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    current_longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    destination_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    destination_longitude = models.DecimalField(max_digits=10, decimal_places=7)


    def __str__(self):
        return self.transportation_id
