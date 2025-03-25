"""
Core checkout flow implementation for e-commerce automation.
"""
import os
import time
import random
from typing import Dict, Any, List, Optional
from pathlib import Path

from loguru import logger
from playwright.async_api import Page, TimeoutError
from retry import retry

from core.api_mock import mock_payment_api


class CheckoutError(Exception):
    """Exception raised for errors during checkout process."""
    pass


async def take_screenshot(page: Page, name: str, user_id: int) -> str:
    """
    Take a screenshot of the current page state.
    
    Args:
        page: Playwright page object
        name: Name for the screenshot
        user_id: User ID for the session
        
    Returns:
        Path to the saved screenshot
    """
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    timestamp = int(time.time())
    filename = f"user_{user_id}_{name}_{timestamp}.png"
    filepath = screenshots_dir / filename
    
    await page.screenshot(path=str(filepath), full_page=True)
    logger.info(f"Screenshot saved: {filepath}")
    
    return str(filepath)


@retry(exceptions=TimeoutError, tries=3, delay=1, backoff=2)
async def navigate_to_page(page: Page, url: str, wait_selector: str) -> None:
    """
    Navigate to a page with retry mechanism.
    
    Args:
        page: Playwright page object
        url: URL to navigate to
        wait_selector: Selector to wait for after navigation
    """
    try:
        await page.goto(url)
        await page.wait_for_selector(wait_selector, timeout=10000)
    except TimeoutError as e:
        logger.warning(f"Timeout navigating to {url}, retrying...")
        raise


async def login(page: Page, user_id: int) -> bool:
    """
    Log in to the e-commerce site.
    
    Args:
        page: Playwright page object
        user_id: User ID for the session
        
    Returns:
        True if login was successful
    """
    try:
        logger.info(f"User {user_id}: Logging in")
        
        # For demo purposes, using a demo e-commerce site
        # In a real scenario, you would use the actual site URL
        await navigate_to_page(
            page, 
            "https://demo.saleor.io/account/login/", 
            "button[type='submit']"
        )
        
        # Fill login credentials - using test credentials for demo
        await page.fill("input[name='email']", f"test_user{user_id}@example.com")
        await page.fill("input[name='password']", f"Password123!")
        
        # Take screenshot before submitting
        await take_screenshot(page, "before_login", user_id)
        
        # Click login button
        await page.click("button[type='submit']")
        
        # Wait for successful login
        try:
            # Check if login was successful by waiting for the dashboard or home page
            await page.wait_for_selector(".navbar-user-email", timeout=10000)
            
            logger.info(f"User {user_id}: Login successful")
            await take_screenshot(page, "after_login", user_id)
            return True
            
        except TimeoutError:
            # Check if there's an error message
            error_visible = await page.is_visible("text=Invalid email or password")
            
            if error_visible:
                logger.error(f"User {user_id}: Login failed - Invalid credentials")
                await take_screenshot(page, "login_error", user_id)
                return False
            else:
                # If no error message but login still timed out
                logger.error(f"User {user_id}: Login timed out")
                await take_screenshot(page, "login_timeout", user_id)
                return False
                
    except Exception as e:
        logger.error(f"User {user_id}: Login exception - {str(e)}")
        await take_screenshot(page, "login_exception", user_id)
        return False


async def search_product(page: Page, user_id: int, product_name: str = "T-Shirt") -> bool:
    """
    Search for a product.
    
    Args:
        page: Playwright page object
        user_id: User ID for the session
        product_name: Name of the product to search for
        
    Returns:
        True if product search was successful
    """
    try:
        logger.info(f"User {user_id}: Searching for product: {product_name}")
        
        # Click on search icon
        await page.click("[data-testid='search-button']")
        
        # Enter search term
        await page.fill("[placeholder='Search products']", product_name)
        
        # Press Enter to search
        await page.press("[placeholder='Search products']", "Enter")
        
        # Wait for search results
        await page.wait_for_selector("[data-testid='productsList']", timeout=10000)
        
        # Take screenshot of search results
        await take_screenshot(page, f"search_results_{product_name}", user_id)
        
        # Check if any products were found
        products = await page.query_selector_all("[data-testid='productTile']")
        
        if len(products) > 0:
            logger.info(f"User {user_id}: Found {len(products)} products for '{product_name}'")
            return True
        else:
            logger.warning(f"User {user_id}: No products found for '{product_name}'")
            return False
            
    except Exception as e:
        logger.error(f"User {user_id}: Product search exception - {str(e)}")
        await take_screenshot(page, "search_exception", user_id)
        return False


async def add_to_cart(page: Page, user_id: int) -> bool:
    """
    Add a product to cart.
    
    Args:
        page: Playwright page object
        user_id: User ID for the session
        
    Returns:
        True if product was added to cart successfully
    """
    try:
        logger.info(f"User {user_id}: Adding product to cart")
        
        # Click on the first product in the search results
        products = await page.query_selector_all("[data-testid='productTile']")
        
        if len(products) == 0:
            logger.error(f"User {user_id}: No products available to add to cart")
            return False
        
        # Click on a random product from the first 3 (or fewer if less than 3 results)
        product_index = random.randint(0, min(2, len(products) - 1))
        await products[product_index].click()
        
        # Wait for product details page
        await page.wait_for_selector("[data-testid='addProductToCartButton']", timeout=10000)
        
        # Select size if available
        size_selectors = await page.query_selector_all("[data-testid='variantSelector'] button")
        if len(size_selectors) > 0:
            # Pick a random size
            size_index = random.randint(0, len(size_selectors) - 1)
            await size_selectors[size_index].click()
        
        # Take screenshot before adding to cart
        await take_screenshot(page, "before_add_to_cart", user_id)
        
        # Click Add to Cart button
        await page.click("[data-testid='addProductToCartButton']")
        
        # Wait for cart confirmation
        await page.wait_for_selector("[data-testid='cartCounter']:text('1')", timeout=10000)
        
        logger.info(f"User {user_id}: Product added to cart successfully")
        await take_screenshot(page, "after_add_to_cart", user_id)
        return True
        
    except Exception as e:
        logger.error(f"User {user_id}: Add to cart exception - {str(e)}")
        await take_screenshot(page, "add_to_cart_exception", user_id)
        return False


async def proceed_to_checkout(page: Page, user_id: int) -> bool:
    """
    Proceed to checkout.
    
    Args:
        page: Playwright page object
        user_id: User ID for the session
        
    Returns:
        True if proceeding to checkout was successful
    """
    try:
        logger.info(f"User {user_id}: Proceeding to checkout")
        
        # Open cart
        await page.click("[data-testid='cartCounter']")
        
        # Wait for cart drawer to open
        await page.wait_for_selector("[data-testid='cartSidebar']", timeout=10000)
        
        # Take screenshot of cart
        await take_screenshot(page, "cart_contents", user_id)
        
        # Click on Checkout button
        await page.click("[data-testid='checkoutButton']")
        
        # Wait for checkout page
        await page.wait_for_selector("[data-testid='checkoutPageHeader']", timeout=15000)
        
        logger.info(f"User {user_id}: Proceeded to checkout successfully")
        await take_screenshot(page, "checkout_page", user_id)
        return True
        
    except Exception as e:
        logger.error(f"User {user_id}: Proceed to checkout exception - {str(e)}")
        await take_screenshot(page, "checkout_exception", user_id)
        return False


async def fill_shipping_details(page: Page, user_id: int) -> bool:
    """
    Fill shipping details in checkout.
    
    Args:
        page: Playwright page object
        user_id: User ID for the session
        
    Returns:
        True if shipping details were filled successfully
    """
    try:
        logger.info(f"User {user_id}: Filling shipping details")
        
        # Check if shipping details are required
        shipping_form_visible = await page.is_visible("[data-testid='shippingAddressForm']")
        
        if not shipping_form_visible:
            logger.info(f"User {user_id}: Shipping details already filled or not required")
            return True
        
        # Fill shipping address form
        await page.fill("[name='firstName']", "Test")
        await page.fill("[name='lastName']", f"User{user_id}")
        await page.fill("[name='streetAddress1']", "123 Test Street")
        await page.fill("[name='city']", "Test City")
        await page.fill("[name='postalCode']", "12345")
        
        # Select country if required
        country_selector = await page.query_selector("[data-testid='addressFormCountrySelect']")
        if country_selector:
            await country_selector.click()
            # Select USA (would need to be adjusted for different demo sites)
            await page.click("text=United States of America")
        
        # Fill phone number (optional on some sites)
        phone_field = await page.query_selector("[name='phone']")
        if phone_field:
            await page.fill("[name='phone']", "1234567890")
        
        # Take screenshot before continuing
        await take_screenshot(page, "shipping_details", user_id)
        
        # Continue to next step
        await page.click("[data-testid='continueToShippingButton']")
        
        # Wait for shipping method selection or payment page
        try:
            await page.wait_for_selector("[data-testid='shippingMethodList'], [data-testid='paymentForm']", timeout=10000)
            logger.info(f"User {user_id}: Shipping details filled successfully")
            return True
        except TimeoutError:
            logger.error(f"User {user_id}: Timeout after shipping details")
            await take_screenshot(page, "shipping_details_timeout", user_id)
            return False
        
    except Exception as e:
        logger.error(f"User {user_id}: Fill shipping details exception - {str(e)}")
        await take_screenshot(page, "shipping_details_exception", user_id)
        return False


async def select_shipping_method(page: Page, user_id: int) -> bool:
    """
    Select a shipping method.
    
    Args:
        page: Playwright page object
        user_id: User ID for the session
        
    Returns:
        True if shipping method was selected successfully
    """
    try:
        logger.info(f"User {user_id}: Selecting shipping method")
        
        # Check if shipping method selection is required
        shipping_method_visible = await page.is_visible("[data-testid='shippingMethodList']")
        
        if not shipping_method_visible:
            logger.info(f"User {user_id}: Shipping method already selected or not required")
            return True
        
        # Select the first shipping method
        shipping_methods = await page.query_selector_all("[data-testid='shippingMethodOption']")
        
        if len(shipping_methods) == 0:
            logger.error(f"User {user_id}: No shipping methods available")
            await take_screenshot(page, "no_shipping_methods", user_id)
            return False
        
        await shipping_methods[0].click()
        
        # Take screenshot after selection
        await take_screenshot(page, "shipping_method_selected", user_id)
        
        # Continue to payment
        await page.click("[data-testid='continueToPaymentButton']")
        
        # Wait for payment form
        await page.wait_for_selector("[data-testid='paymentForm']", timeout=10000)
        
        logger.info(f"User {user_id}: Shipping method selected successfully")
        return True
        
    except Exception as e:
        logger.error(f"User {user_id}: Select shipping method exception - {str(e)}")
        await take_screenshot(page, "shipping_method_exception", user_id)
        return False


async def handle_payment(page: Page, user_id: int) -> bool:
    """
    Handle payment process.
    
    Args:
        page: Playwright page object
        user_id: User ID for the session
        
    Returns:
        True if payment was processed successfully
    """
    try:
        logger.info(f"User {user_id}: Handling payment")
        
        # Setup payment API mocking
        await mock_payment_api(page)
        
        # Check if we need to enter card details
        card_form_visible = await page.is_visible("[data-testid='creditCardForm']")
        
        if card_form_visible:
            # Mock credit card details
            await page.fill("[name='cardNumber']", "4111 1111 1111 1111")
            await page.fill("[name='expDate']", "12/25")
            await page.fill("[name='cvc']", "123")
            
            # Take screenshot of payment form
            await take_screenshot(page, "payment_form", user_id)
        else:
            # Some sites might have different payment methods
            # For demo, we'll check for other common payment options
            payment_methods = await page.query_selector_all("[data-testid='paymentMethod']")
            
            if len(payment_methods) > 0:
                # Select the first payment method
                await payment_methods[0].click()
            else:
                logger.warning(f"User {user_id}: No payment methods found, but continuing")
        
        # Click the pay and place order button
        await page.click("[data-testid='placeOrderButton']")
        
        # Wait for order confirmation
        await page.wait_for_selector("[data-testid='orderConfirmation']", timeout=15000)
        
        # Take screenshot of confirmation
        await take_screenshot(page, "order_confirmation", user_id)
        
        logger.info(f"User {user_id}: Payment processed successfully")
        return True
        
    except Exception as e:
        logger.error(f"User {user_id}: Payment exception - {str(e)}")
        await take_screenshot(page, "payment_exception", user_id)
        return False


async def handle_captcha(page: Page, user_id: int) -> bool:
    """
    Handle CAPTCHA if present (mock implementation).
    
    Args:
        page: Playwright page object
        user_id: User ID for the session
        
    Returns:
        True if CAPTCHA was handled successfully
    """
    try:
        # Check if CAPTCHA is present (this would be site-specific)
        captcha_visible = await page.is_visible("#captcha, .g-recaptcha, iframe[title*='recaptcha']")
        
        if not captcha_visible:
            return True
        
        logger.info(f"User {user_id}: Handling CAPTCHA")
        
        # In a real scenario, you might:
        # 1. Use a CAPTCHA solving service
        # 2. Bypass it in test environments
        # 3. Ask for human intervention
        
        # For this demo, we'll mock bypassing the CAPTCHA
        # This is a simplified example of CAPTCHA bypassing for testing purposes
        
        # Take screenshot of CAPTCHA
        await take_screenshot(page, "captcha", user_id)
        
        # Simulate CAPTCHA solving by injecting JavaScript to bypass it
        # Note: This is for demo purposes only and won't work on real sites
        await page.evaluate("""
            // Mock solving CAPTCHA by directly setting the verification token
            // This is for demonstration only and won't work on real sites
            if (typeof grecaptcha !== 'undefined') {
                document.querySelector('[name="g-recaptcha-response"]').innerHTML = 'MOCKED_CAPTCHA_RESPONSE';
                // Trigger callback if it exists
                if (typeof captchaCallback === 'function') {
                    captchaCallback('MOCKED_CAPTCHA_RESPONSE');
                }
            }
        """)
        
        logger.info(f"User {user_id}: CAPTCHA handled successfully (mocked)")
        return True
        
    except Exception as e:
        logger.error(f"User {user_id}: CAPTCHA handling exception - {str(e)}")
        return False


async def run_checkout(page: Page, user_id: int) -> Dict[str, Any]:
    """
    Run the complete checkout flow.
    
    Args:
        page: Playwright page object
        user_id: User ID for the session
        
    Returns:
        Result dictionary with checkout data
    """
    result = {
        "status": "pending",
        "steps_completed": [],
        "screenshots": [],
        "order_id": None,
        "error": None
    }
    
    try:
        # Step 1: Login
        if not await login(page, user_id):
            raise CheckoutError("Login failed")
        result["steps_completed"].append("login")
        
        # Step 2: Search for a product
        if not await search_product(page, user_id):
            raise CheckoutError("Product search failed")
        result["steps_completed"].append("search")
        
        # Step 3: Add product to cart
        if not await add_to_cart(page, user_id):
            raise CheckoutError("Add to cart failed")
        result["steps_completed"].append("add_to_cart")
        
        # Step 4: Proceed to checkout
        if not await proceed_to_checkout(page, user_id):
            raise CheckoutError("Proceed to checkout failed")
        result["steps_completed"].append("proceed_to_checkout")
        
        # Step 5: Handle CAPTCHA if present
        if not await handle_captcha(page, user_id):
            raise CheckoutError("CAPTCHA handling failed")
        result["steps_completed"].append("handle_captcha")
        
        # Step 6: Fill shipping details
        if not await fill_shipping_details(page, user_id):
            raise CheckoutError("Fill shipping details failed")
        result["steps_completed"].append("fill_shipping_details")
        
        # Step 7: Select shipping method
        if not await select_shipping_method(page, user_id):
            raise CheckoutError("Select shipping method failed")
        result["steps_completed"].append("select_shipping_method")
        
        # Step 8: Handle payment
        if not await handle_payment(page, user_id):
            raise CheckoutError("Payment failed")
        result["steps_completed"].append("payment")
        
        # Extract order ID
        try:
            order_id_element = await page.query_selector("[data-testid='orderNumber']")
            if order_id_element:
                order_id = await order_id_element.text_content()
                result["order_id"] = order_id.strip()
        except Exception:
            logger.warning(f"User {user_id}: Could not extract order ID")
        
        # Take final screenshot
        final_screenshot = await take_screenshot(page, "checkout_complete", user_id)
        result["screenshots"].append(final_screenshot)
        
        # Mark checkout as successful
        result["status"] = "success"
        logger.info(f"User {user_id}: Checkout completed successfully")
        
    except CheckoutError as e:
        # Handle expected checkout errors
        result["status"] = "failed"
        result["error"] = str(e)
        logger.error(f"User {user_id}: Checkout failed - {str(e)}")
        
    except Exception as e:
        # Handle unexpected errors
        result["status"] = "error"
        result["error"] = f"Unexpected error: {str(e)}"
        logger.error(f"User {user_id}: Unexpected error - {str(e)}")
        
        # Take error screenshot
        error_screenshot = await take_screenshot(page, "error", user_id)
        result["screenshots"].append(error_screenshot)
    
    return result 