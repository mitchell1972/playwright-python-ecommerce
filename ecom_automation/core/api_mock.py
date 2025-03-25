"""
API mocking functionality for payment and external systems.
"""
import json
from typing import Dict, Any, Callable, Optional, Pattern, Union
import re

from loguru import logger
from playwright.async_api import Page, Route, Request


async def mock_payment_api(page: Page) -> None:
    """
    Mock payment API calls to avoid real transactions.
    
    Args:
        page: Playwright page object
    """
    logger.info("Setting up payment API mocks")
    
    # Define payment API patterns to intercept
    payment_patterns = [
        "**/api/payment*",
        "**/api/checkout*",
        "**/api/transactions*",
        "**/payments/process*",
        "**/stripe*",
        "**/paypal*",
        "**/braintree*",
    ]
    
    # Mock all payment API endpoints
    for pattern in payment_patterns:
        await page.route(pattern, handle_payment_route)
    
    logger.info("Payment API mocks configured")


async def handle_payment_route(route: Route) -> None:
    """
    Handle payment API routes with mock responses.
    
    Args:
        route: The route to handle
    """
    request = route.request
    url = request.url
    method = request.method
    
    logger.debug(f"Intercepted payment request: {method} {url}")
    
    # Extract any request data
    request_data = {}
    if method in ["POST", "PUT", "PATCH"]:
        try:
            post_data = await request.post_data()
            if post_data:
                try:
                    # Try to parse as JSON
                    request_data = json.loads(post_data)
                except json.JSONDecodeError:
                    # Handle form data
                    request_data = {k: v for k, v in (item.split('=') for item in post_data.split('&') if '=' in item)}
        except Exception as e:
            logger.warning(f"Could not parse request data: {e}")
    
    # Generate appropriate mock response based on the URL and method
    if "payment" in url.lower() or "checkout" in url.lower():
        if method == "POST":
            # Mock a successful payment response
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "status": "success",
                    "transaction_id": "mock_txn_" + generate_mock_id(),
                    "payment_method": "credit_card",
                    "amount": request_data.get("amount", "100.00"),
                    "currency": request_data.get("currency", "USD"),
                    "message": "Payment processed successfully",
                })
            )
        else:
            # For other methods, return a generic success response
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "status": "success"
                })
            )
    
    elif "stripe" in url.lower():
        # Mock Stripe API responses
        await route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "id": "pm_" + generate_mock_id(),
                "object": "payment_method",
                "created": 1652121287,
                "customer": "cus_" + generate_mock_id(),
                "livemode": False,
                "type": "card",
                "card": {
                    "brand": "visa",
                    "country": "US",
                    "exp_month": 12,
                    "exp_year": 2024,
                    "last4": "4242"
                },
                "billing_details": {
                    "address": {
                        "city": "Test City",
                        "country": "US",
                        "postal_code": "12345",
                        "state": "CA"
                    },
                    "email": "customer@example.com",
                    "name": "Test Customer"
                }
            })
        )
    
    elif "paypal" in url.lower():
        # Mock PayPal API responses
        await route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "id": "PAYID-" + generate_mock_id().upper(),
                "intent": "CAPTURE",
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "reference_id": "default",
                        "amount": {
                            "currency_code": "USD",
                            "value": request_data.get("amount", "100.00")
                        }
                    }
                ],
                "payer": {
                    "email_address": "customer@example.com",
                    "payer_id": "PAYERID" + generate_mock_id()
                }
            })
        )
    
    else:
        # For any other payment-related URLs
        await route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "success": True,
                "transaction_id": "txn_" + generate_mock_id()
            })
        )


def generate_mock_id(length: int = 10) -> str:
    """
    Generate a random alphanumeric ID for mock responses.
    
    Args:
        length: Length of the ID to generate
        
    Returns:
        Random alphanumeric ID
    """
    import random
    import string
    
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


async def mock_analytics_calls(page: Page) -> None:
    """
    Mock analytics and tracking API calls.
    
    Args:
        page: Playwright page object
    """
    # Define analytics patterns to intercept
    analytics_patterns = [
        "**/google-analytics.com/*",
        "**/analytics.js*",
        "**/gtm.js*",
        "**/gtag/*",
        "**/collect*",
        "**/pixel*",
        "**/track*",
        "**/hotjar*",
        "**/clarity*"
    ]
    
    # Mock all analytics endpoints
    for pattern in analytics_patterns:
        await page.route(pattern, lambda route: route.abort())
    
    logger.info("Analytics API calls blocked")


async def setup_api_mocking(page: Page) -> None:
    """
    Set up all API mocking for the page.
    
    Args:
        page: Playwright page object
    """
    # Mock payment APIs
    await mock_payment_api(page)
    
    # Mock analytics calls (optional, improves performance)
    await mock_analytics_calls(page)
    
    logger.info("All API mocking configured") 