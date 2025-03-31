#!/usr/bin/env python3
"""
Script to verify that test data loading works correctly.
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath("."))

from ecom_automation.core.test_data import test_data


def main():
    """Verify test data loading functionality."""
    print("\n--- Test Data Verification ---\n")
    
    # Verify user data
    print("User Credentials:")
    for user_type in ["standard", "premium", "admin"]:
        user = test_data.get_user_credentials(user_type)
        print(f"  - {user_type}: {user.get('email')} / {user.get('password')}")
    
    # Verify product data
    print("\nProduct Categories:")
    all_products = test_data.get_products()
    categories = set(p.get("category") for p in all_products)
    
    for category in categories:
        products = test_data.get_products(category)
        print(f"  - {category}: {len(products)} products")
        for product in products:
            print(f"    * {product.get('name')} - {product.get('search_term')}")
    
    # Verify address data
    print("\nShipping Addresses:")
    for country in ["US", "UK", "DE"]:
        address = test_data.get_shipping_address(country)
        if address:
            print(f"  - {country}: {address.get('first_name')} {address.get('last_name')}, {address.get('city')}")
    
    # Verify payment data
    print("\nPayment Methods:")
    for payment_type in ["credit_card", "credit_card_declined", "paypal", "gift_card"]:
        payment = test_data.get_payment_method(payment_type)
        if payment:
            if payment.get("type") == "credit_card":
                print(f"  - {payment_type}: **** **** **** {payment.get('card_number')[-4:]} (expires: {payment.get('expiry_month')}/{payment.get('expiry_year')})")
            else:
                print(f"  - {payment_type}: {payment.get('type')}")
    
    print("\n--- Verification Complete ---")


if __name__ == "__main__":
    main()
