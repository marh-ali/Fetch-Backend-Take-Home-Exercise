from datetime import datetime
from typing import Dict, List, Union
import re


def _validate_required_fields(
    receipt: Dict[str, Union[str, List[Dict[str, str]]]]
) -> None:
    """Validate that all required fields are present in the receipt.

    Required fields are: retailer, purchaseDate, purchaseTime, items, total

    Args:
        receipt: The receipt dictionary to validate

    Raises:
        ValueError: If any required field is missing

    Example:
        >>> receipt = {"retailer": "Target", "total": "10.00"}  # Missing fields
        >>> _validate_required_fields(receipt)
        ValueError: Missing required field: purchaseDate
    """
    required_fields = ["retailer", "purchaseDate", "purchaseTime", "items", "total"]
    for field in required_fields:
        if field not in receipt:
            raise ValueError(f"Missing required field: {field}")


def _validate_retailer(retailer: str) -> None:
    """Validate the retailer name format.

    Retailer name must only contain alphanumeric characters, spaces, hyphens, and ampersands.

    Args:
        retailer: The retailer name to validate

    Raises:
        ValueError: If retailer name contains invalid characters

    Example:
        >>> _validate_retailer("Target")  # Valid
        >>> _validate_retailer("M&M Corner Market")  # Valid
        >>> _validate_retailer("Target!")  # Invalid - contains !
        ValueError: Invalid retailer name format
    """
    if not re.match(r"^[\w\s\-&]+$", retailer):
        raise ValueError("Invalid retailer name format")


def _validate_purchase_date(date_str: str) -> None:
    """Validate the purchase date format.

    Date must be in YYYY-MM-DD format and be a valid date.

    Args:
        date_str: The date string to validate

    Raises:
        ValueError: If date format is invalid or date is not valid

    Example:
        >>> _validate_purchase_date("2022-01-01")  # Valid
        >>> _validate_purchase_date("2022-13-01")  # Invalid month
        ValueError: Invalid purchase date format
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid purchase date format")


def _validate_purchase_time(time_str: str) -> None:
    """Validate the purchase time format.

    Time must be in 24-hour HH:MM format and be a valid time.

    Args:
        time_str: The time string to validate

    Raises:
        ValueError: If time format is invalid or time is not valid

    Example:
        >>> _validate_purchase_time("13:45")  # Valid
        >>> _validate_purchase_time("25:00")  # Invalid hour
        ValueError: Invalid purchase time format
    """
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        raise ValueError("Invalid purchase time format")


def _validate_item_format(item: Dict[str, str]) -> None:
    """Validate the format of a single item.

    Each item must be a dictionary with 'shortDescription' and 'price' keys.
    Description must contain only alphanumeric characters, spaces, and hyphens.
    Price must be in format XX.XX (dollars.cents).

    Args:
        item: The item dictionary to validate

    Raises:
        ValueError: If item format is invalid

    Example:
        >>> item = {"shortDescription": "Mountain Dew 12PK", "price": "6.49"}  # Valid
        >>> _validate_item_format(item)
    """
    if not isinstance(item, dict):
        raise ValueError("Each item must be an object")
    if "shortDescription" not in item or "price" not in item:
        raise ValueError("Items must have shortDescription and price")
    if not re.match(r"^[\w\s\-]+$", item["shortDescription"]):
        raise ValueError("Invalid item description format")
    if not re.match(r"^\d+\.\d{2}$", item["price"]):
        raise ValueError("Invalid item price format")


def _validate_item_price(price_str: str, description: str) -> float:
    """Validate and convert an item's price.

    Price must be a positive number.

    Args:
        price_str: The price string to validate
        description: The item description (for error messages)

    Returns:
        float: The validated price value

    Raises:
        ValueError: If price is invalid or negative

    Example:
        >>> _validate_item_price("10.99", "Sample Item")  # Valid
        10.99
        >>> _validate_item_price("-1.00", "Sample Item")  # Invalid
        ValueError: Item price cannot be negative
    """
    try:
        price = float(price_str)
        if price < 0:
            raise ValueError("Item price cannot be negative")
        return price
    except ValueError:
        raise ValueError(f"Invalid price value for item: {description}")


def _validate_items_array(items: List[Dict[str, str]]) -> float:
    """Validate the array of items and calculate their total sum.

    Must be a non-empty list of valid items.

    Args:
        items: List of item dictionaries to validate

    Returns:
        float: Sum of all item prices

    Raises:
        ValueError: If items array is invalid or empty

    Example:
        >>> items = [
        ...     {"shortDescription": "Item 1", "price": "10.00"},
        ...     {"shortDescription": "Item 2", "price": "5.00"}
        ... ]
        >>> _validate_items_array(items)
        15.00
    """
    if not isinstance(items, list) or len(items) < 1:
        raise ValueError("Items must be a non-empty array")

    total_sum = 0
    for item in items:
        _validate_item_format(item)
        total_sum += _validate_item_price(item["price"], item["shortDescription"])
    return total_sum


def _validate_total(total_str: str, items_sum: float) -> None:
    """Validate the receipt total.

    Total must be in format XX.XX, be positive, and match the sum of item prices.
    A small difference (≤ $0.01) is allowed to account for rounding.

    Args:
        total_str: The total amount string to validate
        items_sum: The calculated sum of all items

    Raises:
        ValueError: If total format is invalid or doesn't match items sum

    Example:
        >>> _validate_total("15.00", 15.00)  # Valid
        >>> _validate_total("15.00", 14.00)  # Invalid - doesn't match
        ValueError: Receipt total (15.0) does not match sum of items (14.0)
    """
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


def validate_receipt(receipt: Dict[str, Union[str, List[Dict[str, str]]]]) -> bool:
    """Validate all aspects of a receipt.

    Performs comprehensive validation of a receipt including:
    - Required fields presence
    - Retailer name format
    - Purchase date and time formats
    - Items array format and validity
    - Total amount and its match with items sum

    Args:
        receipt: The complete receipt dictionary to validate

    Returns:
        bool: True if receipt is valid

    Raises:
        ValueError: If any validation fails

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
        >>> validate_receipt(receipt)
        True
    """
    _validate_required_fields(receipt)
    _validate_retailer(receipt["retailer"])
    _validate_purchase_date(receipt["purchaseDate"])
    _validate_purchase_time(receipt["purchaseTime"])

    items_sum = _validate_items_array(receipt["items"])
    _validate_total(receipt["total"], items_sum)

    return True
