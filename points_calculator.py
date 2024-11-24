from datetime import datetime
from typing import Dict, List, Union


def _get_retailer_name_points(retailer: str) -> int:
    """Calculate points based on alphanumeric characters in retailer name (Rule 1).

    One point awarded for every alphanumeric character in the retailer name.
    Example: "M&M Corner Market" = 14 points ('&' is not alphanumeric)

    Args:
        retailer: The name of the retailer

    Returns:
        Number of alphanumeric characters in the retailer name
    """
    return sum(c.isalnum() for c in retailer)


def _get_total_amount_points(total: str) -> int:
    """Calculate points based on total amount rules (Rules 2 & 3).

    - 50 points if the total is a round dollar amount with no cents
    - 25 points if the total is a multiple of 0.25
    Example: "9.00" = 75 points (50 for round dollar + 25 for multiple of 0.25)

    Args:
        total: The total amount as a string

    Returns:
        Points awarded for round dollar amounts and multiples of 0.25
    """
    points = 0
    total_float = float(total)

    if total_float.is_integer():
        points += 50
    if total_float % 0.25 == 0:
        points += 25
    return points


def _get_items_count_points(items: List[Dict[str, str]]) -> int:
    """Calculate points based on number of items (Rule 4).

    5 points for every two items on the receipt.
    Example: 4 items = 10 points (2 pairs × 5 points)

    Args:
        items: List of items from the receipt

    Returns:
        Points awarded for every two items
    """
    return (len(items) // 2) * 5


def _get_description_length_points(items: List[Dict[str, str]]) -> int:
    """Calculate points based on item description lengths (Rule 5).

    If the trimmed length of the item description is a multiple of 3,
    multiply the price by 0.2 and round up to the nearest integer.
    Example: "Emils Cheese Pizza" (18 chars) with price $12.25
            12.25 * 0.2 = 2.45, rounded up = 3 points

    Args:
        items: List of items from the receipt

    Returns:
        Points awarded for descriptions with length multiple of 3
    """
    points = 0
    for item in items:
        description = item["shortDescription"].strip()
        if len(description) % 3 == 0:
            points += int(float(item["price"]) * 0.2 + 0.99)
    return points


def _get_purchase_date_points(purchase_date: str) -> int:
    """Calculate points based on purchase date (Rule 6).

    6 points if the day in the purchase date is odd.
    Example: "2022-01-01" = 6 points (1 is odd)

    Args:
        purchase_date: Purchase date in YYYY-MM-DD format

    Returns:
        Points awarded for odd numbered days
    """
    date = datetime.strptime(purchase_date, "%Y-%m-%d")
    return 6 if date.day % 2 == 1 else 0


def _get_purchase_time_points(purchase_time: str) -> int:
    """Calculate points based on purchase time (Rule 7).

    10 points if the time of purchase is after 2:00pm and before 4:00pm.
    Example: "14:33" = 10 points (2:33pm is between 2:00pm and 4:00pm)

    Args:
        purchase_time: Purchase time in HH:MM format

    Returns:
        Points awarded for purchases between 2:00pm and 4:00pm
    """
    time = datetime.strptime(purchase_time, "%H:%M")
    return 10 if 14 <= time.hour < 16 else 0


def calculate_points(receipt: Dict[str, Union[str, List[Dict[str, str]]]]) -> int:
    """Calculate total points for a receipt based on all rules.

    Rules:
    1. One point for every alphanumeric character in the retailer name
    2. 50 points if the total is a round dollar amount with no cents
    3. 25 points if the total is a multiple of 0.25
    4. 5 points for every two items on the receipt
    5. If the trimmed length of the item description is a multiple of 3,
       multiply the price by 0.2 and round up to the nearest integer
    6. 6 points if the day in the purchase date is odd
    7. 10 points if the time of purchase is after 2:00pm and before 4:00pm

    Args:
        receipt: Dictionary containing receipt information including:
                - retailer: str
                - purchaseDate: str (YYYY-MM-DD)
                - purchaseTime: str (HH:MM)
                - items: List[Dict[str, str]]
                - total: str

    Returns:
        Total points awarded for the receipt

    Example:
        >>> receipt = {
        ...     "retailer": "Target",
        ...     "purchaseDate": "2022-01-01",
        ...     "purchaseTime": "13:01",
        ...     "items": [
        ...         {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
        ...         {"shortDescription": "Emils Cheese Pizza", "price": "12.25"}
        ...     ],
        ...     "total": "18.74"
        ... }
        >>> calculate_points(receipt)
        14
    """
    points = 0
    points += _get_retailer_name_points(receipt["retailer"])
    points += _get_total_amount_points(receipt["total"])
    points += _get_items_count_points(receipt["items"])
    points += _get_description_length_points(receipt["items"])
    points += _get_purchase_date_points(receipt["purchaseDate"])
    points += _get_purchase_time_points(receipt["purchaseTime"])

    return points
