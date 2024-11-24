from datetime import datetime


def calculate_points(receipt):
    points = 0

    # Rule 1: One point for every alphanumeric character in the retailer name
    points += sum(c.isalnum() for c in receipt["retailer"])

    # Rule 2: 50 points if the total is a round dollar amount
    if float(receipt["total"]).is_integer():
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if float(receipt["total"]) % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items
    points += (len(receipt["items"]) // 2) * 5

    # Rule 5: Points for item descriptions that are multiples of 3
    for item in receipt["items"]:
        description = item["shortDescription"].strip()
        if len(description) % 3 == 0:
            points += int(float(item["price"]) * 0.2 + 0.99)  # Round up

    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt["purchaseDate"], "%Y-%m-%d")
    if purchase_date.day % 2 == 1:
        points += 6

    # Rule 7: 10 points if the time is between 2:00pm and 4:00pm
    purchase_time = datetime.strptime(receipt["purchaseTime"], "%H:%M")
    if 14 <= purchase_time.hour < 16:
        points += 10

    return points
