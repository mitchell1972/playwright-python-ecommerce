"""
Enhanced API mocking module for intercepting and mocking API responses.
Provides more realistic and varied mock data, request validation, 
and more specific mocking capabilities.
"""
import json
import re
from typing import Dict, List, Any, Callable, Optional, Union, Pattern
from pathlib import Path
import random
from datetime import datetime

from playwright.async_api import Page, Route, Request, APIResponse
from loguru import logger

from .exceptions import ApiMockError


class ApiMocker:
    """
    Enhanced API mocker for intercepting and mocking API responses.
    """
    
    def __init__(self, page: Page, mock_data_dir: str = "ecom_automation/mock_data"):
        """
        Initialize the API mocker.
        
        Args:
            page: Playwright page to set up mocking on
            mock_data_dir: Directory containing mock response data files
        """
        self.page = page
        self.mock_data_dir = Path(mock_data_dir)
        self.mock_data_dir.mkdir(exist_ok=True, parents=True)
        
        # Store active route handlers for cleanup
        self._active_handlers: List[Pattern] = []
        
        # Store request validation callbacks
        self._request_validators: Dict[Pattern, Callable[[Request], bool]] = {}
        
        # Cache for loaded mock data
        self._mock_data_cache: Dict[str, Any] = {}
    
    async def setup(self):
        """Set up the API mocker with baseline route handling."""
        # Set up a catch-all handler that will only be used if no specific handler matches
        await self.page.route("**/*", self._default_handler)
    
    async def _default_handler(self, route: Route):
        """Default route handler that passes requests through."""
        await route.continue_()
    
    def _load_mock_data(self, filename: str) -> Any:
        """
        Load mock data from a JSON file.
        
        Args:
            filename: JSON file containing mock response data
            
        Returns:
            Parsed JSON data
        """
        if filename in self._mock_data_cache:
            return self._mock_data_cache[filename]
        
        try:
            filepath = self.mock_data_dir / filename
            with open(filepath, "r") as f:
                data = json.load(f)
                self._mock_data_cache[filename] = data
                return data
        except Exception as e:
            logger.error(f"Error loading mock data file {filename}: {str(e)}")
            return {}
    
    def _get_response_data(self, 
                          base_filename: str, 
                          request_data: Optional[Dict[str, Any]] = None,
                          scenario: Optional[str] = None) -> Dict[str, Any]:
        """
        Get appropriate response data based on request and scenario.
        
        Args:
            base_filename: Base filename for the mock data
            request_data: Optional request data to use for conditional responses
            scenario: Optional scenario name to use (e.g., "success", "error")
            
        Returns:
            Response data dictionary
        """
        # Try scenario-specific file first if provided
        if scenario:
            scenario_file = f"{base_filename}_{scenario}.json"
            scenario_data = self._load_mock_data(scenario_file)
            if scenario_data:
                return scenario_data
        
        # Fall back to base file
        return self._load_mock_data(f"{base_filename}.json")
    
    async def mock_api(self, 
                      url_pattern: str, 
                      mock_filename: str,
                      status: int = 200,
                      request_validator: Optional[Callable[[Request], bool]] = None,
                      scenario_selector: Optional[Callable[[Request], str]] = None):
        """
        Set up API mocking for a specific URL pattern.
        
        Args:
            url_pattern: URL pattern to match for interception
            mock_filename: Base filename for the mock response data (without .json extension)
            status: HTTP status code to return
            request_validator: Optional function to validate request data
            scenario_selector: Optional function to select response scenario based on request
        """
        pattern = re.compile(url_pattern)
        self._active_handlers.append(pattern)
        
        if request_validator:
            self._request_validators[pattern] = request_validator
        
        async def handler(route: Route, request: Request):
            try:
                # Validate request if validator provided
                if request_validator and not request_validator(request):
                    logger.warning(f"Request validation failed for {request.url}")
                    await route.fulfill(
                        status=400,
                        body=json.dumps({"error": "Invalid request"}),
                        headers={"Content-Type": "application/json"}
                    )
                    return
                
                # Parse request data if available
                request_data = None
                if request.post_data:
                    try:
                        request_data = json.loads(request.post_data)
                    except json.JSONDecodeError:
                        request_data = None
                
                # Select scenario if selector provided
                scenario = None
                if scenario_selector:
                    scenario = scenario_selector(request)
                
                # Get mock response data
                response_data = self._get_response_data(mock_filename, request_data, scenario)
                
                # Add dynamic data if needed
                response_data = self._add_dynamic_data(response_data)
                
                # Fulfill with mock data
                await route.fulfill(
                    status=status,
                    body=json.dumps(response_data),
                    headers={"Content-Type": "application/json"}
                )
                
                logger.debug(f"Mocked API response for {request.url} with {mock_filename}")
                
            except Exception as e:
                logger.error(f"Error in API mock handler for {request.url}: {str(e)}")
                # Continue the request if mocking fails
                await route.continue_()
        
        await self.page.route(pattern, handler)
    
    def _add_dynamic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add dynamic data to the response data.
        
        Args:
            data: Original response data
            
        Returns:
            Response data with dynamic values
        """
        # Make a deep copy to avoid modifying the original
        result = json.loads(json.dumps(data))
        
        # Replace special placeholders with dynamic values
        self._replace_placeholders(result)
        
        return result
    
    def _replace_placeholders(self, obj: Any):
        """
        Recursively replace placeholders in the object.
        
        Args:
            obj: Object to process
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    self._replace_placeholders(value)
                elif isinstance(value, str):
                    obj[key] = self._replace_placeholder_string(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    self._replace_placeholders(item)
                elif isinstance(item, str):
                    obj[i] = self._replace_placeholder_string(item)
    
    def _replace_placeholder_string(self, value: str) -> str:
        """
        Replace placeholder strings with dynamic values.
        
        Args:
            value: String value to process
            
        Returns:
            String with placeholders replaced
        """
        if value == "$TIMESTAMP$":
            return datetime.now().isoformat()
        elif value == "$ORDER_ID$":
            return f"ORD-{random.randint(10000, 99999)}"
        elif value == "$TRANSACTION_ID$":
            return f"TX-{random.randint(100000, 999999)}"
        elif value.startswith("$RANDOM_"):
            # Handle $RANDOM_INT(min,max)$ pattern
            match = re.match(r"\$RANDOM_INT\((\d+),(\d+)\)\$", value)
            if match:
                min_val, max_val = int(match.group(1)), int(match.group(2))
                return str(random.randint(min_val, max_val))
        
        return value
    
    async def mock_payment_gateway(self, card_type: str = "valid"):
        """
        Set up mocking for payment gateway API.
        
        Args:
            card_type: Type of card to simulate ("valid", "declined", "expired")
        """
        # Payment gateway mock based on card type
        payment_scenarios = {
            "valid": "success",
            "declined": "declined",
            "expired": "expired"
        }
        
        scenario = payment_scenarios.get(card_type, "success")
        
        def payment_validator(request: Request) -> bool:
            """Validate payment request data."""
            try:
                if not request.post_data:
                    return False
                
                data = json.loads(request.post_data)
                # Check for required payment fields
                required_fields = ["amount", "currency", "card_number", "expiry_month", "expiry_year", "cvv"]
                return all(field in data for field in required_fields)
            except:
                return False
        
        def payment_scenario_selector(request: Request) -> str:
            """Select payment scenario based on card details."""
            try:
                data = json.loads(request.post_data)
                card_number = data.get("card_number", "")
                
                # Detect card type from number
                if card_number.endswith("0002"):
                    return "declined"
                elif int(data.get("expiry_year", 2099)) < datetime.now().year:
                    return "expired"
                else:
                    return "success"
            except:
                return scenario
        
        await self.mock_api(
            url_pattern=r".*/api/payment/process",
            mock_filename="payment",
            status=200,
            request_validator=payment_validator,
            scenario_selector=payment_scenario_selector
        )
    
    async def mock_shipping_options(self, country: str = "US"):
        """
        Set up mocking for shipping options API.
        
        Args:
            country: Country code to provide shipping options for
        """
        def shipping_validator(request: Request) -> bool:
            """Validate shipping request data."""
            try:
                if not request.post_data:
                    return False
                
                data = json.loads(request.post_data)
                # Check for required shipping fields
                required_fields = ["country", "postal_code"]
                return all(field in data for field in required_fields)
            except:
                return False
        
        def shipping_scenario_selector(request: Request) -> str:
            """Select shipping scenario based on country."""
            try:
                data = json.loads(request.post_data)
                return data.get("country", country).lower()
            except:
                return country.lower()
        
        await self.mock_api(
            url_pattern=r".*/api/shipping/options",
            mock_filename="shipping",
            status=200,
            request_validator=shipping_validator,
            scenario_selector=shipping_scenario_selector
        )
    
    async def mock_order_confirmation(self):
        """Set up mocking for order confirmation API."""
        def order_validator(request: Request) -> bool:
            """Validate order request data."""
            try:
                if not request.post_data:
                    return False
                
                data = json.loads(request.post_data)
                # Check for required order fields
                required_fields = ["cart_id", "payment_method", "shipping_address"]
                return all(field in data for field in required_fields)
            except:
                return False
        
        await self.mock_api(
            url_pattern=r".*/api/orders/create",
            mock_filename="order",
            status=201,
            request_validator=order_validator
        )
    
    async def cleanup(self):
        """Clean up all active route handlers."""
        for pattern in self._active_handlers:
            await self.page.unroute(pattern)
        self._active_handlers = []


# Helper function to set up complete API mocking for checkout flow
async def setup_checkout_mocks(page: Page, card_type: str = "valid", country: str = "US"):
    """
    Set up complete API mocking for checkout flow.
    
    Args:
        page: Playwright page
        card_type: Card type to simulate
        country: Country for shipping options
        
    Returns:
        ApiMocker instance
    """
    mocker = ApiMocker(page)
    await mocker.setup()
    await mocker.mock_payment_gateway(card_type)
    await mocker.mock_shipping_options(country)
    await mocker.mock_order_confirmation()
    return mocker
