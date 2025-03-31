"""
Parameterized tests for e-commerce checkout flow.
"""
import os
import sys
import pytest
from playwright.async_api import Page

sys.path.insert(0, os.path.abspath("."))
from ecom_automation.core.test_data import test_data
from ecom_automation.core.config import BASE_URL
from ecom_automation.core.selector_utils import safe_click, safe_fill, find_element


@pytest.mark.asyncio
@pytest.mark.parametrize("product_category", ["apparel", "accessories", "electronics"])
async def test_product_search_by_category(page: Page, product_category: str):
    """
    Test searching for products by different categories.
    
    Args:
        page: Playwright page fixture
        product_category: Product category to test
    """
    # Get test products for this category
    products = test_data.get_products(product_category)
    assert len(products) > 0, f"No test products found for category: {product_category}"
    product = products[0]  # Use first product in category
    
    # Navigate to website
    await page.goto(BASE_URL)
    
    # Search for the product
    await safe_fill(page, "[data-testid=search-input]", product["search_term"], 
                   alternative_selector="input[placeholder*='Search']")
    await page.press("[data-testid=search-input]", "Enter")
    
    # Verify search results contain the product
    results_locator = await find_element(page, [
        "[data-testid=search-results]",
        ".search-results",
        ".product-list"
    ])
    assert results_locator is not None, "Search results not found"
    
    # Verify product is in results
    await page.wait_for_selector(f"text={product['name']}", timeout=5000)
    product_visible = await page.is_visible(f"text={product['name']}")
    assert product_visible, f"Product '{product['name']}' not found in search results"


@pytest.mark.asyncio
@pytest.mark.parametrize("user_type", ["standard", "premium"])
async def test_login_by_user_type(page: Page, user_type: str):
    """
    Test login functionality with different user types.
    
    Args:
        page: Playwright page fixture
        user_type: Type of user to test login with
    """
    # Get user credentials
    user = test_data.get_user_credentials(user_type)
    assert "email" in user and "password" in user, f"Missing credentials for user type: {user_type}"
    
    # Navigate to website
    await page.goto(f"{BASE_URL}/account/login/")
    
    # Fill login form
    await safe_fill(page, "[data-testid=email]", user["email"], 
                  alternative_selector="#email")
    await safe_fill(page, "[data-testid=password]", user["password"], 
                  alternative_selector="#password")
    
    # Submit form
    await safe_click(page, "[data-testid=login-button]", 
                   alternative_selector="button[type=submit]")
    
    # Verify successful login
    account_element = await find_element(page, [
        "[data-testid=user-account]",
        ".account-details",
        ".user-name"
    ])
    assert account_element is not None, f"Failed to log in as {user_type} user"


@pytest.mark.asyncio
@pytest.mark.parametrize("country", ["US", "UK", "DE"])
async def test_shipping_address_by_country(page: Page, country: str):
    """
    Test checkout with different shipping addresses by country.
    
    Args:
        page: Playwright page fixture
        country: Country code for shipping address
    """
    # Get shipping address for specified country
    address = test_data.get_shipping_address(country)
    assert address, f"No address data found for country: {country}"
    
    # Navigate to website and add a product to cart (simplified for example)
    await page.goto(BASE_URL)
    await page.click(".add-to-cart")
    await page.click("[data-testid=checkout-button]")
    
    # Fill shipping address form
    await safe_fill(page, "[data-testid=first-name]", address["first_name"])
    await safe_fill(page, "[data-testid=last-name]", address["last_name"])
    await safe_fill(page, "[data-testid=address1]", address["address_line1"])
    if address.get("address_line2"):
        await safe_fill(page, "[data-testid=address2]", address["address_line2"])
    await safe_fill(page, "[data-testid=city]", address["city"])
    await safe_fill(page, "[data-testid=postal-code]", address["zip_code"])
    
    # Select country
    await page.select_option("[data-testid=country]", address["country"])
    
    # Fill state if applicable
    if address.get("state"):
        await safe_fill(page, "[data-testid=state]", address["state"])
    
    # Submit form
    await safe_click(page, "[data-testid=continue-button]")
    
    # Verify shipping address was accepted
    shipping_summary = await find_element(page, [
        "[data-testid=shipping-summary]",
        ".shipping-details",
        ".address-summary"
    ])
    assert shipping_summary is not None, f"Shipping address for {country} not accepted"
