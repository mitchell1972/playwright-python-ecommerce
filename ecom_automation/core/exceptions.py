"""
Custom exceptions for the ecom_automation framework.
"""
from typing import Optional, Any, Dict


class EcomBaseException(Exception):
    """Base exception class for all ecom_automation exceptions."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NavigationError(EcomBaseException):
    """Raised when navigation to a page fails."""
    pass


class ElementNotFoundError(EcomBaseException):
    """Raised when an element is not found on the page."""
    
    def __init__(self, selector: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or f"Element not found: {selector}"
        self.selector = selector
        super().__init__(message, details)


class ElementInteractionError(EcomBaseException):
    """Raised when interaction with an element fails."""
    
    def __init__(self, selector: str, action: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or f"Failed to {action} element: {selector}"
        self.selector = selector
        self.action = action
        super().__init__(message, details)


class CheckoutError(EcomBaseException):
    """Raised when there is an error during checkout process."""
    
    def __init__(self, step: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or f"Checkout failed at step: {step}"
        self.step = step
        super().__init__(message, details)


class PaymentError(EcomBaseException):
    """Raised when payment processing fails."""
    
    def __init__(self, payment_method: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or f"Payment failed with method: {payment_method}"
        self.payment_method = payment_method
        super().__init__(message, details)


class ApiMockError(EcomBaseException):
    """Raised when API mocking fails."""
    
    def __init__(self, endpoint: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or f"API mocking failed for endpoint: {endpoint}"
        self.endpoint = endpoint
        super().__init__(message, details)


class TestDataError(EcomBaseException):
    """Raised when there is an issue with test data."""
    
    def __init__(self, data_type: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or f"Test data error for type: {data_type}"
        self.data_type = data_type
        super().__init__(message, details)
