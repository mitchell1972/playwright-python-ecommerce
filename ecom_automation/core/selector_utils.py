"""
Selector utilities for robust element interactions.
Provides fallback mechanisms and best practices for element selection.
"""
from typing import Optional, List, Union
from playwright.async_api import Page, Locator
from loguru import logger

async def safe_click(page: Page, selector: str, alternative_selector: Optional[str] = None, 
                    timeout: Optional[int] = None) -> bool:
    """
    Safely click on an element with fallback selector.
    
    Args:
        page: Playwright page object
        selector: Primary selector to use (preferably data-testid)
        alternative_selector: Fallback selector if primary fails
        timeout: Optional timeout override
        
    Returns:
        True if click was successful, False otherwise
    """
    try:
        if timeout:
            await page.click(selector, timeout=timeout)
        else:
            await page.click(selector)
        logger.debug(f"Successfully clicked on '{selector}'")
        return True
    except Exception as e:
        logger.warning(f"Click on '{selector}' failed: {str(e)}")
        if alternative_selector:
            try:
                logger.info(f"Trying alternative selector: '{alternative_selector}'")
                if timeout:
                    await page.click(alternative_selector, timeout=timeout)
                else:
                    await page.click(alternative_selector)
                logger.debug(f"Successfully clicked on alternative '{alternative_selector}'")
                return True
            except Exception as alt_e:
                logger.error(f"Click on alternative '{alternative_selector}' also failed: {str(alt_e)}")
                return False
        return False

async def safe_fill(page: Page, selector: str, text: str, alternative_selector: Optional[str] = None,
                   timeout: Optional[int] = None) -> bool:
    """
    Safely fill a text field with fallback selector.
    
    Args:
        page: Playwright page object
        selector: Primary selector to use (preferably data-testid)
        text: Text to fill into the field
        alternative_selector: Fallback selector if primary fails
        timeout: Optional timeout override
        
    Returns:
        True if fill was successful, False otherwise
    """
    try:
        if timeout:
            await page.fill(selector, text, timeout=timeout)
        else:
            await page.fill(selector, text)
        logger.debug(f"Successfully filled '{selector}' with text")
        return True
    except Exception as e:
        logger.warning(f"Fill on '{selector}' failed: {str(e)}")
        if alternative_selector:
            try:
                logger.info(f"Trying alternative selector: '{alternative_selector}'")
                if timeout:
                    await page.fill(alternative_selector, text, timeout=timeout)
                else:
                    await page.fill(alternative_selector, text)
                logger.debug(f"Successfully filled alternative '{alternative_selector}' with text")
                return True
            except Exception as alt_e:
                logger.error(f"Fill on alternative '{alternative_selector}' also failed: {str(alt_e)}")
                return False
        return False

async def safe_select(page: Page, selector: str, value: str, alternative_selector: Optional[str] = None,
                     timeout: Optional[int] = None) -> bool:
    """
    Safely select an option with fallback selector.
    
    Args:
        page: Playwright page object
        selector: Primary selector to use (preferably data-testid)
        value: Value to select
        alternative_selector: Fallback selector if primary fails
        timeout: Optional timeout override
        
    Returns:
        True if selection was successful, False otherwise
    """
    try:
        if timeout:
            await page.select_option(selector, value, timeout=timeout)
        else:
            await page.select_option(selector, value)
        logger.debug(f"Successfully selected option '{value}' in '{selector}'")
        return True
    except Exception as e:
        logger.warning(f"Selection in '{selector}' failed: {str(e)}")
        if alternative_selector:
            try:
                logger.info(f"Trying alternative selector: '{alternative_selector}'")
                if timeout:
                    await page.select_option(alternative_selector, value, timeout=timeout)
                else:
                    await page.select_option(alternative_selector, value)
                logger.debug(f"Successfully selected option '{value}' in alternative '{alternative_selector}'")
                return True
            except Exception as alt_e:
                logger.error(f"Selection in alternative '{alternative_selector}' also failed: {str(alt_e)}")
                return False
        return False

async def find_element(page: Page, selectors: List[str], timeout: Optional[int] = None) -> Optional[Locator]:
    """
    Try multiple selectors in order until an element is found.
    
    Args:
        page: Playwright page object
        selectors: List of selectors to try in order
        timeout: Optional timeout override
        
    Returns:
        Locator object if element found, None otherwise
    """
    for selector in selectors:
        try:
            locator = page.locator(selector)
            count = await locator.count()
            if count > 0:
                logger.debug(f"Found element with selector: '{selector}'")
                return locator
        except Exception as e:
            logger.debug(f"Selector '{selector}' failed: {str(e)}")
    
    logger.warning(f"Failed to find element with any of these selectors: {selectors}")
    return None
