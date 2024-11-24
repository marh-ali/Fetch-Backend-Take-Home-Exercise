from datetime import datetime
import re


def _validate_required_fields(receipt):
    required_fields = ["retailer", "purchaseDate", "purchaseTime", "items", "total"]
    for field in required_fields:
        if field not in receipt:
            raise ValueError(f"Missing required field: {field}")


def _validate_retailer(retailer):
    if not re.match(r"^[\w\s\-&]+$", retailer):
        raise ValueError("Invalid retailer name format")


def _validate_purchase_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid purchase date format")


def _validate_purchase_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        raise ValueError("Invalid purchase time format")


def _validate_item_format(item):
    if not isinstance(item, dict):
        raise ValueError("Each item must be an object")
    if "shortDescription" not in item or "price" not in item:
        raise ValueError("Items must have shortDescription and price")
    if not re.match(r"^[\w\s\-]+$", item["shortDescription"]):
        raise ValueError("Invalid item description format")
    if not re.match(r"^\d+\.\d{2}$", item["price"]):
        raise ValueError("Invalid item price format")


def _validate_item_price(price_str, description):
    try:
        price = float(price_str)
        if price < 0:
            raise ValueError("Item price cannot be negative")
        return price
    except ValueError:
        raise ValueError(f"Invalid price value for item: {description}")


def _validate_items_array(items):
    if not isinstance(items, list) or len(items) < 1:
        raise ValueError("Items must be a non-empty array")

    total_sum = 0
    for item in items:
        _validate_item_format(item)
        total_sum += _validate_item_price(item["price"], item["shortDescription"])
    return total_sum


def _validate_total(total_str, items_sum):
    if not re.match(r"^\d+\.\d{2}$", total_str):
        raise ValueError("Invalid total format")

    try:
        total = float(total_str)
        if total < 0:
            raise ValueError("Total cannot be negative")

        if abs(total - items_sum) > 0.01:
            raise ValueError(
                f"Receipt total ({total}) does not match sum of items ({items_sum})"
            )
    except ValueError as e:
        if str(e).startswith("Receipt total"):
            raise e
        raise ValueError("Invalid total value")


def validate_receipt(receipt):
    _validate_required_fields(receipt)
    _validate_retailer(receipt["retailer"])
    _validate_purchase_date(receipt["purchaseDate"])
    _validate_purchase_time(receipt["purchaseTime"])

    items_sum = _validate_items_array(receipt["items"])
    _validate_total(receipt["total"], items_sum)

    return True
