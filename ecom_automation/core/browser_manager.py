"""
Browser manager for parallel execution of multiple browser sessions.
"""
import os
import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from loguru import logger
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from tqdm import tqdm

from core.checkout_flow import run_checkout


class BrowserManager:
    """
    Manages multiple browser sessions for parallel execution.
    """
    
    def __init__(
        self,
        headless: bool = True,
        browser_type: str = "chromium",
        slow_mo: int = 50,
        screenshots_dir: str = "screenshots",
        timeout: int = 30000,
    ):
        """
        Initialize the browser manager.
        
        Args:
            headless: Whether to run browsers in headless mode
            browser_type: Type of browser to use (chromium, firefox, webkit)
            slow_mo: Slow down interactions by specified milliseconds
            screenshots_dir: Directory to save screenshots
            timeout: Default timeout for operations in milliseconds
        """
        self.headless = headless
        self.browser_type = browser_type
        self.slow_mo = slow_mo
        self.timeout = timeout
        
        # Setup screenshots directory
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Performance tracking
        self.start_time = 0
        self.end_time = 0
    
    async def setup_browser(self, user_id: int) -> Tuple[Browser, BrowserContext, Page]:
        """
        Set up a browser instance.
        
        Args:
            user_id: Unique identifier for this browser session
            
        Returns:
            Tuple of (browser, context, page)
        """
        playwright = await async_playwright().start()
        
        if self.browser_type == "chromium":
            browser = await playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
            )
        elif self.browser_type == "firefox":
            browser = await playwright.firefox.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
            )
        elif self.browser_type == "webkit":
            browser = await playwright.webkit.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
            )
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
        
        # Create a unique browser context for this session
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        )
        
        # Set default timeout
        context.set_default_timeout(self.timeout)
        
        # Enable request interception for API mocking
        await context.route("**/*", lambda route: route.continue_())
        
        # Create a new page
        page = await context.new_page()
        
        # Setup page event listeners
        page.on("console", lambda msg: logger.debug(f"Browser {user_id} console {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: logger.error(f"Browser {user_id} page error: {err}"))
        
        return browser, context, page
    
    async def run_single_browser(self, user_id: int) -> Dict[str, Any]:
        """
        Run a single browser session.
        
        Args:
            user_id: Unique identifier for this browser session
            
        Returns:
            Results dictionary with session data
        """
        browser = None
        context = None
        
        try:
            logger.info(f"Starting browser session {user_id}")
            browser, context, page = await self.setup_browser(user_id)
            
            # Record start time
            session_start = time.time()
            
            # Run the checkout flow
            result = await run_checkout(page, user_id)
            
            # Record end time
            session_end = time.time()
            result["duration"] = session_end - session_start
            result["user_id"] = user_id
            
            return result
            
        except Exception as e:
            logger.error(f"Error in browser session {user_id}: {str(e)}")
            session_end = time.time()
            
            return {
                "user_id": user_id,
                "status": "error",
                "error": str(e),
                "duration": session_end - session_start if 'session_start' in locals() else 0,
            }
            
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()
    
    async def run_parallel_sessions(self, num_users: int) -> List[Dict[str, Any]]:
        """
        Run multiple browser sessions in parallel.
        
        Args:
            num_users: Number of parallel browser sessions to run
            
        Returns:
            List of result dictionaries from each session
        """
        self.start_time = time.time()
        logger.info(f"Starting {num_users} parallel browser sessions")
        
        # Create tasks for each browser session
        tasks = [self.run_single_browser(i) for i in range(num_users)]
        
        # Run tasks with progress bar
        with tqdm(total=num_users, desc="Running sessions", unit="user") as progress:
            results = []
            for task in asyncio.as_completed(tasks):
                result = await task
                results.append(result)
                progress.update(1)
        
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        
        logger.info(f"Completed {num_users} sessions in {total_duration:.2f} seconds")
        
        # Calculate success rate
        success_count = sum(1 for r in results if r.get("status") == "success")
        success_rate = (success_count / num_users) * 100
        
        logger.info(f"Success rate: {success_rate:.2f}% ({success_count}/{num_users})")
        
        return results


async def run_parallel_sessions(num_users: int, headless: bool = True) -> List[Dict[str, Any]]:
    """
    Run parallel browser sessions.
    
    Args:
        num_users: Number of parallel browser sessions to run
        headless: Whether to run browsers in headless mode
        
    Returns:
        List of result dictionaries from each session
    """
    manager = BrowserManager(headless=headless)
    return await manager.run_parallel_sessions(num_users) 