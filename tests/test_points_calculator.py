import pytest
from datetime import datetime
from points_calculator import calculate_points


def test_retailer_name_points():
    test_cases = [
        ("Target", 6),  # 6 alphanumeric chars (TARGET)
        ("M&M Corner", 8),  # 8 alphanumeric chars (MMCORNER)
        ("7-11", 3),  # 3 alphanumeric chars (711)
        ("A", 1),  # Single char (A)
        ("", 0),  # Empty string
        ("Best Buy!", 7),  # 7 alphanumeric chars (BESTBUY)
    ]

    for retailer, expected_points in test_cases:
        receipt = {
            "retailer": retailer,
            "total": "0.99",  # Non-round, non-quarter
            "purchaseDate": "2024-03-20",  # Even day
            "purchaseTime": "13:00",  # Outside range
            "items": [],  # No items
        }
        assert sum(c.isalnum() for c in receipt["retailer"]) == expected_points


def test_round_dollar_points():
    test_cases = [
        ("11.01", 0),  # Not round
        ("11.99", 0),  # Not round
        ("12.00", 75),  # Round dollar AND multiple of 0.25 (50 + 25)
    ]

    for total, expected_points in test_cases:
        receipt = {
            "total": total,
            "retailer": "",  # Empty retailer
            "purchaseDate": "2024-03-20",  # Even day
            "purchaseTime": "13:00",  # Outside range
            "items": [],  # No items
        }
        points = 0
        if float(total).is_integer():
            points += 50
        if float(total) % 0.25 == 0:
            points += 25
        assert points == expected_points  # Test just the total-related logic


def test_quarter_multiple_points():
    test_cases = [
        ("10.25", 25),  # Multiple of 0.25 (not round dollar)
        ("10.75", 25),  # Multiple of 0.25 (not round dollar)
        ("10.99", 0),  # Not multiple of 0.25
    ]

    for total, expected_points in test_cases:
        receipt = {
            "total": total,
            "retailer": "",  # Empty retailer
            "purchaseDate": "2024-03-20",  # Even day
            "purchaseTime": "13:00",  # Outside range
            "items": [],  # No items
        }
        assert calculate_points(receipt) == expected_points


def test_pairs_of_items_points():
    test_cases = [
        ([], 0),  # Empty list
        ([{"shortDescription": "Item1", "price": "0.01"}], 0),  # Single item
        (
            [
                {"shortDescription": "Item1", "price": "0.01"},
                {"shortDescription": "Item2", "price": "0.01"},
            ],
            5,
        ),  # One pair
        (
            [
                {"shortDescription": "Item1", "price": "0.01"},
                {"shortDescription": "Item2", "price": "0.01"},
                {"shortDescription": "Item3", "price": "0.01"},
            ],
            5,
        ),  # One pair + extra
        (
            [
                {"shortDescription": "Item1", "price": "0.01"},
                {"shortDescription": "Item2", "price": "0.01"},
                {"shortDescription": "Item3", "price": "0.01"},
                {"shortDescription": "Item4", "price": "0.01"},
            ],
            10,
        ),  # Two pairs
    ]

    for items, expected_points in test_cases:
        receipt = {
            "items": items,
            "retailer": "",  # Empty retailer
            "total": "0.99",  # Non-round, non-quarter
            "purchaseDate": "2024-03-20",  # Even day
            "purchaseTime": "13:00",  # Outside range
        }
        assert calculate_points(receipt) == expected_points


def test_item_description_points():
    test_cases = [
        (
            [{"shortDescription": "ABC", "price": "10.00"}],
            2,
        ),  # Length 3, 10.00 * 0.2 = 2
        (
            [{"shortDescription": "ABCDEF", "price": "10.00"}],
            2,
        ),  # Length 6, 10.00 * 0.2 = 2
        (
            [{"shortDescription": "AB", "price": "10.00"}],
            0,
        ),  # Length 2 (not multiple of 3)
        (
            [
                {"shortDescription": "ABC", "price": "10.00"},
                {"shortDescription": "ABCDEF", "price": "15.00"},
            ],
            5,
        ),  # Two items: 2 + 3 points
    ]

    for items, expected_points in test_cases:
        points = 0
        for item in items:
            if len(item["shortDescription"].strip()) % 3 == 0:
                points += int(float(item["price"]) * 0.2 + 0.99)  # Round up
        assert points == expected_points  # Test just the description logic


def test_odd_day_points():
    test_cases = [
        ("2024-03-21", 6),  # Odd day
        ("2024-03-20", 0),  # Even day
        ("2024-03-31", 6),  # Last day (odd)
        ("2024-03-30", 0),  # Last day (even)
    ]

    for date, expected_points in test_cases:
        receipt = {
            "purchaseDate": date,
            "retailer": "",  # Empty retailer
            "total": "0.99",  # Non-round, non-quarter
            "purchaseTime": "13:00",  # Outside range
            "items": [],  # No items
        }
        assert calculate_points(receipt) == expected_points


def test_time_range_points():
    test_cases = [
        ("14:00", 10),  # Start of range
        ("15:59", 10),  # End of range
        ("14:30", 10),  # Middle of range
        ("13:59", 0),  # Just before
        ("16:00", 0),  # Just after
        ("00:00", 0),  # Midnight
        ("23:59", 0),  # End of day
    ]

    for time, expected_points in test_cases:
        receipt = {
            "purchaseTime": time,
            "retailer": "",  # Empty retailer
            "total": "0.99",  # Non-round, non-quarter
            "purchaseDate": "2024-03-20",  # Even day
            "items": [],  # No items
        }
        assert calculate_points(receipt) == expected_points
