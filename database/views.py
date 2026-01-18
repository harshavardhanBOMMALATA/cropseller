import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User,Product,Bidding,Order,Transaction,Transportation
from django.db import connection
import random
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import models



import traceback

@csrf_exempt
def user_login(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'status': 'error'}, status=405)

        data = json.loads(request.body.decode('utf-8'))
        email = data.get('username')
        password = data.get('password')

        user = User.objects.get(email=email, password=password)
        request.session['email'] = user.email

        return JsonResponse({'status': 'success'})

    except Exception as e:
        print("LOGIN ERROR:", e)
        traceback.print_exc()
        return JsonResponse({'status': 'error'}, status=500)



@csrf_exempt
def signup(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'fail'})

    data = json.loads(request.body)

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    address=data.get('address')
    photo='https://res.cloudinary.com/dz1i8o4w6/image/upload/v1768451654/noprofile_zyfp6k.jpg'

    # check if email already exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({'status': 'fail', 'message': 'email exists'})

    # generate unique 7-digit user_id
    while True:
        user_id = random.randint(1000000, 9999999)
        if not User.objects.filter(user_id=user_id).exists():
            break

    User.objects.create(
        user_id=user_id,
        name=name,
        email=email,
        password=password,
        phone_number=phone,
        address=name,
        photo=photo,
    )

    return JsonResponse({'status': 'success'})


@csrf_exempt
def products(request):
    email = request.session.get('email')

    id = user.getId(email)
    user = User.objects.get(id=id)

    products_qs = Product.objects.exclude(user=user)

    result = []

    for p in products_qs:
        result.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "quantity": p.quantity,
            "location": p.location,
            "delivery": p.delivery,
            "price_per_kg": float(p.price_per_kg),
            "photo_url": p.photo_url,
            "user_id": p.user_id,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return JsonResponse({"results": result})


@csrf_exempt
def userdetails(request):
    email = request.session.get('email')

    user = User.objects.get(email=email)

    result = {
        "username": user.name,
        "email": user.email,
        "user_id": user.user_id,
        "phonenumber":user.phone_number,
        "address":user.address,
        "photo":user.photo,
    }

    return JsonResponse({"result": result})


@csrf_exempt
def userdetailsedit(request):
    try:
        email = request.session.get('email')
        user = User.objects.get(email=email)

        data = json.loads(request.body)

        user.name = data.get("username")
        user.phone_number = data.get("phonenumber")
        user.address = data.get("address")
        user.email = data.get("email")

        user.save()
        return JsonResponse({"status": "success"})
    except:
        return JsonResponse({"status": "failure"})


@csrf_exempt
def productdetail(request, productid):
    product = Product.objects.get(product_id=productid)

    # get logged-in user
    email = request.session.get('email')
    userid = getId(email)   # your existing helper

    # owner check
    isowner = (userid == product.user_id)

    return JsonResponse({
        "product_id": product.product_id,
        "product_name": product.product_name,
        "quantity": product.quantity,
        "location": product.location,
        "delivery": product.delivery,
        "price_per_kg": str(product.price_per_kg),
        "photo_url": product.photo_url,
        "fssai_license": product.fssai_license,
        "organic_certified": product.organic_certified,
        "moisture": product.moisture,
        "crop_year": product.crop_year,
        "packaging": product.packaging,
        "supply_capacity": product.supply_capacity,
        "isowner": isowner,
        'description':product.description,
    })


from django.utils.timezone import now
from datetime import timedelta

@csrf_exempt
def producthistory(request, productid):
    today = now()

    buckets = {
        "30d": (today - timedelta(days=30), today - timedelta(days=25)),
        "25d": (today - timedelta(days=25), today - timedelta(days=20)),
        "20d": (today - timedelta(days=20), today - timedelta(days=15)),
        "15d": (today - timedelta(days=15), today - timedelta(days=10)),
        "10d": (today - timedelta(days=10), today - timedelta(days=5)),
        "5d":  (today - timedelta(days=5), today),
    }

    result = []

    for label, (start, end) in buckets.items():
        count = Bidding.objects.filter(
            product_id=productid,
            created_time__gte=start,
            created_time__lt=end
        ).count()
        result.append(count)

    return JsonResponse(result, safe=False)




@csrf_exempt
def placebid(request, bid_quantity, bid_price, id, product_id):
    try:
        # generate UNIQUE bidding_id (digits 1–6 only)
        while True:
            bidding_id = "".join(str(random.randint(1, 6)) for _ in range(8))
            if not Bidding.objects.filter(bidding_id=bidding_id).exists():
                break

        product = Product.objects.get(product_id=product_id)
        user = User.objects.get(user_id=id)

        Bidding.objects.create(
            bidding_id=bidding_id,
            product=product,
            user=user,
            bid_price=bid_price,
            bid_quantity=bid_quantity,
            created_time = models.DateTimeField(auto_now_add=True)
        )

        return JsonResponse(True, safe=False)

    except Exception:
        return JsonResponse(False, safe=False)


def getId(email):
    user=User.objects.get(email=email)
    return user.user_id


@csrf_exempt
def productspostedcount(request, user_id):
    count = Product.objects.filter(user_id=user_id).count()
    return JsonResponse({
        "status": "success",
        "products_posted": count
    })


@csrf_exempt
def biddingspostedcount(request, user_id):
    count = Bidding.objects.filter(user_id=user_id).count()
    return JsonResponse({
        "status": "success",
        "bids_made": count
    })



def mybiddings(request, id):
    biddings = (
        Bidding.objects
        .filter(user_id=id)
        .select_related("product", "product__user")
    )

    data = []
    for bid in biddings:
        product = bid.product              
        seller = product.user              

        data.append({
            "bidding_id": bid.bidding_id,

            # product info
            "product_id": product.product_id,
            "product_name": product.product_name,
            "photo_url": product.photo_url,
            "delivery": product.delivery,

            # quantities & prices
            "ordered_quantity": bid.bid_quantity,
            "available_quantity": product.quantity,
            "bid_price": float(bid.bid_price),
            "actual_price": float(product.price_per_kg),

            # verdict rule
            "verdict": "success" if bid.verdict == "accepted" else bid.verdict,

            # seller info (derived correctly)
            "seller_id": seller.user_id,
            "seller_name": seller.name,
            "seller_contact_number": seller.phone_number,

            "created_time": bid.created_time
        })

    return data



def myorders(request, userid):

    orders_qs = (
        Order.objects
        .filter(user_id=userid)
        .select_related('product', 'bidding')
        .order_by('-order_id')
    )

    orders = []

    for o in orders_qs:
        orders.append({
            "order_id": o.order_id,
            "verdict": o.verdict,

            # Product details
            "product_id": o.product.product_id,
            "product_name": o.product.product_name,
            "product_image": o.product.photo_url,
            "product_location": o.product.location,

            # Bidding details
            "bid_price": float(o.bidding.bid_price),
            "bid_quantity": o.bidding.bid_quantity,

            # Tracking
            "current_latitude": float(o.current_latitude),
            "current_longitude": float(o.current_longitude),
            "target_latitude": float(o.target_latitude),
            "target_longitude": float(o.target_longitude),
        })

    return orders


@csrf_exempt
def transaction(request, userid, orderid, productid):

    try:
        # Fetch order with relations
        order = (
            Order.objects
            .select_related('product', 'bidding', 'user')
            .get(order_id=orderid, user_id=userid, product_id=productid)
        )

        # Fetch transaction for this order
        txn = Transaction.objects.get(order_id=order.order_id)

        # Seller (product owner)
        seller = order.product.user

        data = {
            "order": {
                "order_id": order.order_id,
                "verdict": order.verdict,

                # Product
                "product_id": order.product.product_id,
                "product_name": order.product.product_name,
                "product_image": order.product.photo_url,
                "product_location": order.product.location,

                # Bidding
                "bid_price": float(order.bidding.bid_price),
                "bid_quantity": order.bidding.bid_quantity,

                # Tracking
                "current_latitude": float(order.current_latitude),
                "current_longitude": float(order.current_longitude),
                "target_latitude": float(order.target_latitude),
                "target_longitude": float(order.target_longitude),

                # Seller
                "seller": {
                    "seller_id": seller.user_id,
                    "name": seller.name,
                    "phone": seller.phone_number,
                    "location": seller.address,
                },

                # Transaction
                "transaction": {
                    "transaction_id": txn.transaction_id,
                    "payment_method": txn.payment_method,
                    "amount": float(txn.amount),
                    "status": txn.status,
                    "transaction_date": txn.transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
                }
            }
        }

        return JsonResponse(data, status=200)

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    except Transaction.DoesNotExist:
        return JsonResponse({"error": "Transaction not found for this order"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def myproducts(request, userid):
    products = Product.objects.filter(user_id=userid)

    data = []
    for p in products:
        data.append({
            "product_id":p.product_id,
            "product_name": p.product_name,
            "price_per_kg": float(p.price_per_kg),
            "quantity": p.quantity,
            "photo_url": p.photo_url,
            "enddate":p.enddate,
        })

    return JsonResponse({
        "success": True,
        "count": len(data),
        "products": data
    })



def addproduct(request, product):
    try:
        email = request.session.get('email')
        user = User.objects.get(email=email)


        while True:
            product_id = random.randint(1, 999999)
            if not Product.objects.filter(product_id=product_id).exists():
                break

        Product.objects.create(
            product_id=product_id,
            product_name=product["product_name"],
            quantity=product["quantity"],
            location=product["location"],
            delivery=product["delivery"],
            price_per_kg=product["price_per_kg"],
            photo_url=product["photo_url"],
            description=product["description"],
            fssai_license=product["fssai_license"],
            organic_certified=product["organic_certified"],
            moisture=product["moisture"],
            crop_year=product["crop_year"],
            packaging=product["packaging"],
            supply_capacity=product["supply_capacity"],
            user=user,
            created_at =timezone.now()
        )

        return JsonResponse({
            "success": True,
            "product_id": product_id
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)
    


@csrf_exempt
def updateproduct(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)

    product = Product.objects.get(product_id=data["product_id"])

    product.product_name = data["product_name"]
    product.quantity = data["quantity"]
    product.price_per_kg = data["price_per_kg"]
    product.location = data["location"]
    product.delivery = data["delivery"]
    product.supply_capacity = data["supply_capacity"]
    product.fssai_license = data["fssai_license"]
    product.organic_certified = data["organic_certified"]
    product.moisture = data["moisture"]
    product.crop_year = data["crop_year"]
    product.packaging = data["packaging"]
    product.description = data["description"]
    product.photo_url = data["photo_url"]

    product.save()

    return JsonResponse({"success": True})


@csrf_exempt
def allbiddings(request, productid):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        product = Product.objects.get(product_id=productid)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    bids_qs = Bidding.objects.filter(product=product)

    # --------------------------------
    # Parse created_time (string → dt)
    # --------------------------------
    parsed_bids = []
    for bid in bids_qs:
        try:
            bid_time = datetime.fromisoformat(bid.created_time)
            parsed_bids.append((bid, bid_time))
        except Exception:
            continue

    # --------------------------------
    # ⭐ IF PRODUCT ENDED → TAKE LAST BID DATE ONLY
    # --------------------------------
    if product.enddate == "end" and parsed_bids:
        latest_date = max(t.date() for _, t in parsed_bids)
        parsed_bids = [
            (b, t) for b, t in parsed_bids if t.date() == latest_date
        ]

    # --------------------------------
    # BASIC COUNTS
    # --------------------------------
    total_bids = len(parsed_bids)
    bid_prices = [float(b.bid_price) for b, _ in parsed_bids]

    highest_bid = max(bid_prices) if bid_prices else 0
    lowest_bid = min(bid_prices) if bid_prices else 0
    average_bid = round(sum(bid_prices) / total_bids, 2) if total_bids else 0

    highest_bid_count = bid_prices.count(highest_bid)
    lowest_bid_count = bid_prices.count(lowest_bid)
    average_bid_count = sum(
        1 for price in bid_prices if abs(price - average_bid) <= 1
    )

    # --------------------------------
    # WEEKLY ANALYTICS (UNCHANGED)
    # --------------------------------
    now = datetime.now()
    week_ranges = {
        "week1": (now - timedelta(days=7), now),
        "week2": (now - timedelta(days=14), now - timedelta(days=7)),
        "week3": (now - timedelta(days=21), now - timedelta(days=14)),
        "week4": (now - timedelta(days=30), now - timedelta(days=21)),
    }

    weekly = {}
    for week, (start, end) in week_ranges.items():
        week_bids = [b for b, t in parsed_bids if start <= t < end]
        prices = [float(b.bid_price) for b in week_bids]

        weekly[week] = {
            "bids_count": len(week_bids),
            "highest_bid": max(prices) if prices else 0
        }

    # --------------------------------
    # BID DETAILS
    # --------------------------------
    bid_list = []
    for bid, bid_time in parsed_bids:
        order = Order.objects.filter(bidding=bid).first()
        order_id = order.order_id if order else "ORD001"

        bid_list.append({
            "bidding_id": bid.bidding_id,
            "order_id": order_id,
            "buyer_id": bid.user.user_id,
            "buyer_name": bid.user.name,
            "buyer_contact_number": bid.user.phone_number,
            "user_photo_url": bid.user.photo,
            "bid_price": float(bid.bid_price),
            "bid_quantity": bid.bid_quantity,
            "created_time": bid.created_time,
            "verdict": bid.verdict,
            "profit": float(bid.bid_price) * bid.bid_quantity
        })

    return JsonResponse({
        "end": True if product.enddate == "end" else False,
        "product": {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "base_price": float(product.price_per_kg),
            "available_quantity": product.quantity
        },
        "summary": {
            "total_bids": total_bids,
            "highest_bid": highest_bid,
            "lowest_bid": lowest_bid,
            "average_bid": average_bid,
            "highest_bid_count": highest_bid_count,
            "lowest_bid_count": lowest_bid_count,
            "average_bid_count": average_bid_count
        },
        "weekly": weekly,
        "bids": bid_list
    })



def biddingverdict(request, biddingid, verdict):
    try:
        bidding = Bidding.objects.get(bidding_id=biddingid)
        bidding.verdict = verdict
        bidding.save(update_fields=["verdict"])

        user = bidding.user

        return JsonResponse({
            "status": "success",
            "buyer_id": user.user_id,
            "buyer_name": user.name,
            "phone_number": user.phone_number
        })
    except Bidding.DoesNotExist:
        return JsonResponse({"status": "failure"})


@csrf_exempt
def makeorder(request, biddingid, userid):
    if request.method != "POST":
        return JsonResponse({"status": "failure", "message": "Invalid request method"})

    try:
        bidding = Bidding.objects.get(bidding_id=biddingid)
        product = bidding.product
        user = User.objects.get(user_id=userid)

        # generate unique 10-character order_id using numbers 1–6 only
        while True:
            order_id = ''.join(str(random.randint(1, 6)) for _ in range(10))
            if not Order.objects.filter(order_id=order_id).exists():
                break

        Order.objects.create(
            order_id=order_id,
            product=product,
            bidding=bidding,
            user=user,
            verdict="placed"
        )

        return JsonResponse({
            "status": "success",
            "order_id": order_id
        })

    except Bidding.DoesNotExist:
        return JsonResponse({"status": "failure", "message": "Bidding not found"})

    except User.DoesNotExist:
        return JsonResponse({"status": "failure", "message": "User not found"})

    except Exception as e:
        return JsonResponse({"status": "failure", "message": str(e)})


@csrf_exempt
def createtransaction(request, order_id):
    if request.method != "POST":
        return JsonResponse({"status": "failure", "message": "Invalid request method"})

    try:
        order = Order.objects.get(order_id=order_id)

        while True:
            transaction_id = "TXN" + ''.join(str(random.randint(0, 9)) for _ in range(7))
            if not Transaction.objects.filter(transaction_id=transaction_id).exists():
                break

        Transaction.objects.create(
            transaction_id=transaction_id,
            order=order,
            payment_method="pending",
            amount=0.00,
            status="pending",
            transaction_date=timezone.now()
        )

        return JsonResponse({
            "status": "success",
            "transaction_id": transaction_id
        })

    except Order.DoesNotExist:
        return JsonResponse({"status": "failure", "message": "Order not found"})

    except Exception as e:
        return JsonResponse({"status": "failure", "message": str(e)})



@csrf_exempt
def createtransportation(request, order_id):
    if request.method != "POST":
        return JsonResponse({"status": "failure", "message": "Invalid request method"})

    try:
        order = Order.objects.get(order_id=order_id)

        while True:
            transportation_id = "TRN" + ''.join(str(random.randint(0, 9)) for _ in range(7))
            if not Transportation.objects.filter(transportation_id=transportation_id).exists():
                break

        Transportation.objects.create(
            transportation_id=transportation_id,
            order=order,
            vehicle_number="pending",
            driver_name="pending",
            driver_phone="pending",
            start_latitude=0.0000000,
            start_longitude=0.0000000,
            current_latitude=None,
            current_longitude=None,
            destination_latitude=0.0000000,
            destination_longitude=0.0000000
        )

        return JsonResponse({
            "status": "success",
            "transportation_id": transportation_id
        })

    except Order.DoesNotExist:
        return JsonResponse({"status": "failure", "message": "Order not found"})

    except Exception as e:
        return JsonResponse({"status": "failure", "message": str(e)})



@csrf_exempt
def orderdetails(request, order_id):
    if request.method != "GET":
        return JsonResponse({"status": "failure", "message": "Invalid request method"})

    try:
        order = Order.objects.select_related(
            "user",
            "product",
            "bidding"
        ).get(order_id=order_id)

        transaction = Transaction.objects.filter(order=order).first()
        transportation = Transportation.objects.filter(order=order).first()

        response = {
            # -------------------------
            # ORDER INFO
            # -------------------------
            "order": {
                "order_id": order.order_id,
                "status": order.verdict
            },

            # -------------------------
            # BUYER INFO
            # -------------------------
            "buyer": {
                "buyer_id": order.user.user_id,
                "buyer_name": order.user.name,
                "phone": order.user.phone_number,
                "email": order.user.email,
                "address": order.user.address
            },

            # -------------------------
            # PRODUCT INFO
            # -------------------------
            "product": {
                "product_name": order.product.product_name,
                "quantity": order.bidding.bid_quantity,
                "price_per_kg": float(order.bidding.bid_price),
                "total_price": float(order.bidding.bid_price) * order.bidding.bid_quantity,
                "photo_url": order.product.photo_url
            },

            # -------------------------
            # TRANSACTION INFO
            # -------------------------
            "transaction": None if not transaction else {
                "transaction_id": transaction.transaction_id,
                "amount": float(transaction.amount),
                "payment_method": transaction.payment_method,
                "status": transaction.status,
                "date": transaction.transaction_date
            },

            # -------------------------
            # TRANSPORTATION INFO
            # -------------------------
            "transportation": None if not transportation else {
                "transportation_id": transportation.transportation_id,
                "driver_name": transportation.driver_name,
                "driver_phone": transportation.driver_phone,
                "vehicle_number": transportation.vehicle_number,
                "current_latitude": transportation.current_latitude,
                "current_longitude": transportation.current_longitude,
                "destination_latitude": transportation.destination_latitude,
                "destination_longitude": transportation.destination_longitude
            }
        }

        return JsonResponse({
            "status": "success",
            "data": response
        })

    except Order.DoesNotExist:
        return JsonResponse({
            "status": "failure",
            "message": "Order not found"
        })


@csrf_exempt
def orderdetails_helper(request, order_id):
    if request.method != "GET":
        return JsonResponse({
            "status": "failure",
            "message": "Invalid request method"
        })

    try:
        order = Order.objects.select_related(
            "user",
            "product",
            "bidding"
        ).get(order_id=order_id)

        transaction = Transaction.objects.filter(order=order).first()
        transportation = Transportation.objects.filter(order=order).first()

        return JsonResponse({
            "status": "success",
            "data": {
                "order_id": order.order_id,
                "order_status": order.verdict,

                "buyer": {
                    "buyer_id": order.user.user_id,
                    "buyer_name": order.user.name,
                    "buyer_phone": order.user.phone_number,
                    "buyer_email": order.user.email,
                    "buyer_address": order.user.address,
                },

                "product": {
                    "product_name": order.product.product_name,
                    "quantity": order.bidding.bid_quantity,
                    "price_per_kg": float(order.bidding.bid_price),
                    "total_price": float(order.bidding.bid_price) * order.bidding.bid_quantity,
                    "photo_url": order.product.photo_url,
                },

                "transaction": None if not transaction else {
                    "transaction_id": transaction.transaction_id,
                    "amount": float(transaction.amount),
                    "payment_method": transaction.payment_method,
                    "status": transaction.status,
                    "transaction_date": transaction.transaction_date,
                },

                "transportation": None if not transportation else {
                    "transportation_id": transportation.transportation_id,
                    "driver_name": transportation.driver_name,
                    "driver_phone": transportation.driver_phone,
                    "vehicle_number": transportation.vehicle_number,
                    "current_latitude": transportation.current_latitude,
                    "current_longitude": transportation.current_longitude,
                    "destination_latitude": transportation.destination_latitude,
                    "destination_longitude": transportation.destination_longitude,
                }
            }
        })

    except Order.DoesNotExist:
        return JsonResponse({
            "status": "failure",
            "message": "Order not found"
        })


@csrf_exempt
def endbid(request, productid):
    if request.method != "GET":
        return JsonResponse({
            "status": "failure"
        })

    try:
        product = Product.objects.get(product_id=productid)
        product.enddate = "end"
        product.save(update_fields=["enddate"])

        return JsonResponse({
            "status": "success"
        })

    except Product.DoesNotExist:
        return JsonResponse({
            "status": "failure"
        })


@csrf_exempt
def checking():
    return JsonResponse({"status":"working"})