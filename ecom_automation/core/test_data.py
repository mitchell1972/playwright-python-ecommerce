"""
Test data management module.
Centralizes test data to separate it from test implementation.
"""
from typing import Dict, List, Any
import os
import json
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables that might contain test data
load_dotenv()

# Default test data directory
TEST_DATA_DIR = Path("ecom_automation/data")

class TestData:
    """
    Class for managing test data.
    Loads data from JSON files or environment variables.
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the test data manager.
        
        Args:
            data_path: Optional custom path to test data directory
        """
        self.data_dir = Path(data_path) if data_path else TEST_DATA_DIR
        self.data_dir.mkdir(exist_ok=True)
        self._cache = {}
    
    def load_data(self, data_file: str) -> Dict[str, Any]:
        """
        Load data from a JSON file.
        
        Args:
            data_file: Name of the JSON file to load
            
        Returns:
            Dictionary of data from the file
        """
        if data_file in self._cache:
            return self._cache[data_file]
            
        file_path = self.data_dir / data_file
        
        if not file_path.exists():
            logger.error(f"Test data file not found: {file_path}")
            return {}
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                self._cache[data_file] = data
                return data
        except Exception as e:
            logger.error(f"Error loading test data file {file_path}: {str(e)}")
            return {}
    
    def get_user_credentials(self, user_type: str = "standard") -> Dict[str, str]:
        """
        Get user credentials, with fallback to environment variables.
        
        Args:
            user_type: Type of user (standard, admin, etc.)
            
        Returns:
            Dictionary containing email and password
        """
        # Try loading from data file first
        users = self.load_data("users.json").get("users", {})
        user_data = users.get(user_type, {})
        
        # Fallback to environment variables if not found in file
        if not user_data:
            logger.info(f"User data for {user_type} not found in file, using environment variables")
            return {
                "email": os.getenv(f"{user_type.upper()}_USER_EMAIL", "demo@example.com"),
                "password": os.getenv(f"{user_type.upper()}_USER_PASSWORD", "demo123")
            }
            
        return user_data
    
    def get_products(self, category: str = None) -> List[Dict[str, Any]]:
        """
        Get product data filtered by optional category.
        
        Args:
            category: Optional category to filter products
            
        Returns:
            List of product data dictionaries
        """
        products = self.load_data("products.json").get("products", [])
        
        if category:
            return [p for p in products if p.get("category") == category]
            
        return products
    
    def get_shipping_address(self, country: str = "US") -> Dict[str, str]:
        """
        Get shipping address data for a specific country.
        
        Args:
            country: Country code for the address
            
        Returns:
            Dictionary containing address details
        """
        addresses = self.load_data("addresses.json").get("addresses", {})
        return addresses.get(country, {})
        
    def get_payment_method(self, method_type: str = "credit_card") -> Dict[str, Any]:
        """
        Get payment method data.
        
        Args:
            method_type: Type of payment method
            
        Returns:
            Dictionary containing payment details
        """
        payments = self.load_data("payments.json").get("payment_methods", {})
        return payments.get(method_type, {})


# Create a default instance for ease of use
test_data = TestData()
