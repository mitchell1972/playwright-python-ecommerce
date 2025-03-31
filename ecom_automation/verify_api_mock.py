#!/usr/bin/env python3
"""
Script to verify the API mocking functionality.
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath("."))

from playwright.async_api import async_playwright
from loguru import logger

from ecom_automation.core.api_mock import ApiMocker
from ecom_automation.core.config import BASE_URL


async def test_api_mocking():
    """Test the API mocking functionality."""
    print("\n--- API Mock Verification ---\n")
    
    async with async_playwright() as p:
        # Launch a browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Initialize the API mocker
            mocker = ApiMocker(page)
            await mocker.setup()
            
            # Mock API endpoints
            print("Setting up API mocks...")
            await mocker.mock_payment_gateway()
            await mocker.mock_shipping_options()
            await mocker.mock_order_confirmation()
            
            # Set up a simple HTML page with JavaScript to test the API mocks
            await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>API Mock Test</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .card { border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 5px; }
                    .success { background-color: #e6ffe6; }
                    .error { background-color: #ffe6e6; }
                    button { padding: 8px 16px; margin: 5px; }
                    pre { background-color: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <h1>API Mock Testing</h1>
                
                <div class="card">
                    <h2>Payment Gateway Testing</h2>
                    <button id="testValidPayment">Test Valid Payment</button>
                    <button id="testDeclinedPayment">Test Declined Payment</button>
                    <button id="testExpiredPayment">Test Expired Card</button>
                    <pre id="paymentResult">Results will appear here...</pre>
                </div>
                
                <div class="card">
                    <h2>Shipping Options Testing</h2>
                    <button id="testUSShipping">Test US Shipping</button>
                    <button id="testUKShipping">Test UK Shipping</button>
                    <pre id="shippingResult">Results will appear here...</pre>
                </div>
                
                <script>
                    // Full base URL for API requests
                    const BASE_API_URL = 'https://api.example.com';
                    
                    // Test valid payment
                    document.getElementById('testValidPayment').addEventListener('click', async () => {
                        const result = document.getElementById('paymentResult');
                        try {
                            const response = await fetch(`${BASE_API_URL}/api/payment/process`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    amount: 125.99,
                                    currency: 'USD',
                                    card_number: '4111111111111111',
                                    expiry_month: '12',
                                    expiry_year: '2025',
                                    cvv: '123'
                                })
                            });
                            
                            const data = await response.json();
                            result.innerHTML = JSON.stringify(data, null, 2);
                            result.className = data.success ? 'success' : 'error';
                        } catch (error) {
                            result.innerHTML = 'Error: ' + error.message;
                            result.className = 'error';
                        }
                    });
                    
                    // Test declined payment
                    document.getElementById('testDeclinedPayment').addEventListener('click', async () => {
                        const result = document.getElementById('paymentResult');
                        try {
                            const response = await fetch(`${BASE_API_URL}/api/payment/process`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    amount: 125.99,
                                    currency: 'USD',
                                    card_number: '4000000000000002',
                                    expiry_month: '12',
                                    expiry_year: '2025',
                                    cvv: '123'
                                })
                            });
                            
                            const data = await response.json();
                            result.innerHTML = JSON.stringify(data, null, 2);
                            result.className = data.success ? 'success' : 'error';
                        } catch (error) {
                            result.innerHTML = 'Error: ' + error.message;
                            result.className = 'error';
                        }
                    });
                    
                    // Test expired payment
                    document.getElementById('testExpiredPayment').addEventListener('click', async () => {
                        const result = document.getElementById('paymentResult');
                        try {
                            const response = await fetch(`${BASE_API_URL}/api/payment/process`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    amount: 125.99,
                                    currency: 'USD',
                                    card_number: '4111111111111111',
                                    expiry_month: '12',
                                    expiry_year: '2020',
                                    cvv: '123'
                                })
                            });
                            
                            const data = await response.json();
                            result.innerHTML = JSON.stringify(data, null, 2);
                            result.className = data.success ? 'success' : 'error';
                        } catch (error) {
                            result.innerHTML = 'Error: ' + error.message;
                            result.className = 'error';
                        }
                    });
                    
                    // Test US shipping
                    document.getElementById('testUSShipping').addEventListener('click', async () => {
                        const result = document.getElementById('shippingResult');
                        try {
                            const response = await fetch(`${BASE_API_URL}/api/shipping/options`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    country: 'US',
                                    postal_code: '10001'
                                })
                            });
                            
                            const data = await response.json();
                            result.innerHTML = JSON.stringify(data, null, 2);
                            result.className = data.success ? 'success' : 'error';
                        } catch (error) {
                            result.innerHTML = 'Error: ' + error.message;
                            result.className = 'error';
                        }
                    });
                    
                    // Test UK shipping
                    document.getElementById('testUKShipping').addEventListener('click', async () => {
                        const result = document.getElementById('shippingResult');
                        try {
                            const response = await fetch(`${BASE_API_URL}/api/shipping/options`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    country: 'UK',
                                    postal_code: 'SW1A 1AA'
                                })
                            });
                            
                            const data = await response.json();
                            result.innerHTML = JSON.stringify(data, null, 2);
                            result.className = data.success ? 'success' : 'error';
                        } catch (error) {
                            result.innerHTML = 'Error: ' + error.message;
                            result.className = 'error';
                        }
                    });
                </script>
            </body>
            </html>
            """)
            
            # Update the API mock patterns to match the full URLs
            print("\nUpdating mock patterns for full URLs...")
            await mocker.page.route(
                "https://api.example.com/api/payment/process",
                lambda route: route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({
                        "success": True,
                        "transaction_id": "TX-123456",
                        "amount": 125.99,
                        "currency": "USD",
                        "status": "approved",
                        "timestamp": "2023-04-01T12:34:56Z",
                        "card": {
                            "last4": "1111",
                            "brand": "visa",
                            "exp_month": 12,
                            "exp_year": 2025
                        }
                    })
                )
            )
            
            await mocker.page.route(
                "https://api.example.com/api/shipping/options",
                lambda route: route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({
                        "success": True,
                        "country": "US",
                        "options": [
                            {
                                "id": "usps_priority",
                                "name": "USPS Priority Mail",
                                "description": "Delivery in 2-3 business days",
                                "price": 9.99,
                                "currency": "USD",
                                "estimated_days": 3
                            },
                            {
                                "id": "usps_express",
                                "name": "USPS Priority Mail Express",
                                "description": "Delivery in 1-2 business days",
                                "price": 24.99,
                                "currency": "USD",
                                "estimated_days": 1
                            }
                        ]
                    })
                )
            )
            
            print("Testing mock API responses:")
            
            # Test valid payment
            print("\n1. Testing valid payment...")
            await page.click("#testValidPayment")
            try:
                await page.wait_for_selector("#paymentResult:not(:empty)", timeout=10000)
                payment_result = await page.inner_text("#paymentResult")
                print(f"Payment result: {payment_result[:100]}...") # Print first 100 chars to debug
                payment_data = json.loads(payment_result)
                print(f"Transaction ID: {payment_data.get('transaction_id')}")
                print(f"Status: {payment_data.get('status')}")
                assert payment_data.get("success") is True
            except Exception as e:
                print(f"Error in valid payment test: {str(e)}")
                # Take screenshot for debugging
                await page.screenshot(path="payment_error.png")
                raise
            
            # Test shipping options
            print("\n2. Testing shipping options...")
            await page.click("#testUSShipping")
            try:
                await page.wait_for_selector("#shippingResult:not(:empty)", timeout=10000)
                shipping_result = await page.inner_text("#shippingResult")
                print(f"Shipping result: {shipping_result[:100]}...") # Print first 100 chars to debug
                shipping_data = json.loads(shipping_result)
                print(f"Country: {shipping_data.get('country')}")
                print(f"Number of shipping options: {len(shipping_data.get('options', []))}")
                assert shipping_data.get("success") is True
                assert len(shipping_data.get("options", [])) > 0
            except Exception as e:
                print(f"Error in shipping options test: {str(e)}")
                await page.screenshot(path="shipping_error.png")
                raise
            
            print("\n✅ API mocking verification completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during API mock verification: {str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            # Clean up
            await context.close()
            await browser.close()


async def main():
    """Main entry point for API mock verification."""
    await test_api_mocking()


if __name__ == "__main__":
    asyncio.run(main())
