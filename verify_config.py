#!/usr/bin/env python3
"""
Simple script to verify configuration is properly loaded from .env file
"""
import os
import sys

# Add the ecom_automation directory to the Python path
sys.path.insert(0, os.path.abspath("ecom_automation"))

from ecom_automation.core.config import BASE_URL, BROWSER, HEADLESS, TIMEOUT

def main():
    print("Configuration values loaded from .env file:")
    print(f"BASE_URL: {BASE_URL}")
    print(f"BROWSER: {BROWSER}")
    print(f"HEADLESS: {HEADLESS}")
    print(f"TIMEOUT: {TIMEOUT}")
    
    print("\nVerifying values match what's in .env file...")
    
    # Read .env file values directly for verification
    env_vars = {}
    with open(".env", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                env_vars[key] = value
    
    # Check each value
    assert BASE_URL == env_vars.get("BASE_URL", ""), "BASE_URL doesn't match .env"
    assert BROWSER == env_vars.get("BROWSER", ""), "BROWSER doesn't match .env"
    assert HEADLESS == (env_vars.get("HEADLESS", "").lower() == "true"), "HEADLESS doesn't match .env"
    assert TIMEOUT == int(env_vars.get("TIMEOUT", "0")), "TIMEOUT doesn't match .env"
    
    print("✅ Success! Configuration is correctly loaded from .env file")

if __name__ == "__main__":
    main()
