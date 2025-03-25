#!/usr/bin/env python3
"""
Main script for E-Commerce Automation with Playwright.
Provides a CLI interface to run automation with various options.
"""
import os
import sys
import argparse
import asyncio
from typing import Dict, List, Any
from pathlib import Path

from loguru import logger
from core.browser_manager import run_parallel_sessions
from core.reporting import generate_report


def setup_logger(log_level: str = "INFO", log_file: str = "automation.log"):
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Log file path
    """
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file logger
    logger.add(
        log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="1 week"
    )


async def main_async(args: argparse.Namespace) -> int:
    """
    Async main function that runs the automation.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        logger.info(f"Starting E-Commerce automation with {args.users} parallel users")
        logger.info(f"Headless mode: {args.headless}")
        
        # Create directories if they don't exist
        Path("screenshots").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        Path("reports").mkdir(exist_ok=True)
        
        # Run the automation with the specified number of users
        results = await run_parallel_sessions(args.users, args.headless)
        
        # Generate report if requested
        if args.report:
            report_path = generate_report(results)
            logger.info(f"Report generated: {report_path}")
            
            # Open the report if requested
            if args.open_report:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(report_path)}")
        
        # Calculate success rate
        total_runs = len(results)
        successful_runs = sum(1 for r in results if r.get("status") == "success")
        success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
        
        logger.info(f"Automation completed with {success_rate:.2f}% success rate ({successful_runs}/{total_runs})")
        
        # Return success if all runs were successful, otherwise return failure
        return 0 if success_rate == 100 else 1
        
    except Exception as e:
        logger.error(f"Error in automation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 2


def main() -> int:
    """
    Main entry point for the application.
    
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(description="E-Commerce Automation")
    
    # Required arguments
    parser.add_argument("--users", type=int, default=3, help="Number of parallel users (default: 3)")
    
    # Optional arguments
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--report", action="store_true", help="Generate PDF report")
    parser.add_argument("--open-report", action="store_true", help="Open the generated report")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                      default="INFO", help="Logging level (default: INFO)")
    parser.add_argument("--log-file", default="automation.log", 
                      help="Log file path (default: automation.log)")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(args.log_level, args.log_file)
    
    # Run the async main function
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main()) 