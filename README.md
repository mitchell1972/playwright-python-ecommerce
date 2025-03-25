# Playwright Python E-Commerce Automation Framework

A comprehensive web testing and automation framework developed in Python using Playwright for automating e-commerce functionality testing and checkout flows.

## 📋 Project Overview

This project demonstrates the implementation of a modular, scalable automation framework for testing e-commerce websites. It leverages Playwright's powerful capabilities for browser automation and provides various features such as parallel test execution, API mocking, and HTML reporting.

## 🚀 Main Features

- **Multi-Step Workflow Automation**
  - Login to e-commerce sites with credential management
  - Search for products with customizable queries
  - Add products to cart with variant selection
  - Complete checkout process end-to-end
  - Handle CAPTCHA verification (via mocking)

- **Parallel Execution Engine**
  - Run multiple browser sessions simultaneously
  - Configurable number of parallel users
  - Progress tracking with real-time status updates
  - Balanced resource utilization

- **Advanced API Mocking**
  - Intercept payment gateway calls
  - Mock Stripe, PayPal, and other provider responses
  - Prevent actual financial transactions
  - Simulate various payment scenarios

- **Resilient Error Recovery**
  - Automatic retry for flaky operations
  - Screenshot capture on failures
  - Detailed logging of each step
  - Custom exception handling
  - Smart handling of cookie consent dialogs

- **Comprehensive Reporting**
  - Generate HTML reports with metrics
  - Visual charts for success rates
  - Step completion analysis
  - Performance benchmarking
  - Screenshot integration

## 🗂️ Repository Structure

This repository is organized as follows:

```
ecom_automation/
├── core/                     # Core functionality
│   ├── __init__.py
│   ├── api_mock.py           # Payment API interception
│   ├── browser_manager.py    # Parallel browser orchestration
│   ├── checkout_flow.py      # E-commerce checkout steps
│   └── reporting.py          # HTML report generation
├── tests/                    # Test suite
│   ├── __init__.py
│   └── test_flow.py          # Pytest-based tests
├── screenshots/              # Generated screenshots
├── reports/                  # Generated HTML reports
├── data/                     # Extracted data storage
├── main.py                   # CLI entry point
└── requirements.txt          # Dependencies
```

## 🔍 Implementation Highlights

The framework implements several advanced automation patterns:

1. **Context Managers**: Proper resource management with async context managers
2. **Page Object Pattern**: Modular approach to page interactions
3. **Async/Await**: Leveraging Python's asyncio for better performance
4. **Pytest Fixtures**: Reusable test components with pytest fixtures
5. **Selective Retries**: Smart retry mechanisms for flaky UI elements
6. **Direct Navigation**: Fallback strategies for unreliable UI interactions

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/playwright-python-automation.git
   cd playwright-python-automation
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r ecom_automation/requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install
   ```

## 🚦 Running the Automation

### Basic Usage

Run the automation with default settings (3 parallel users):

```bash
python ecom_automation/main.py
```

### Advanced Options

```bash
# Run with 5 parallel users in headless mode
python ecom_automation/main.py --users 5 --headless

# Generate an HTML report
python ecom_automation/main.py --report

# Generate and automatically open the report
python ecom_automation/main.py --report --open-report

# Set custom logging level
python ecom_automation/main.py --log-level DEBUG

# Combine multiple options
python ecom_automation/main.py --users 10 --headless --report --log-level INFO
```

## 🧪 Running Tests

The framework includes comprehensive tests to validate functionality:

```bash
# Run all tests
pytest ecom_automation/tests/

# Run a specific test
pytest ecom_automation/tests/test_flow.py::test_api_mocking

# Run with verbose output
pytest ecom_automation/tests/ -v

# Suppress warnings
pytest ecom_automation/tests/ -v -p no:warnings
```

## 🔍 Implementation Details

### Browser Manager (`browser_manager.py`)

The `BrowserManager` class orchestrates parallel browser sessions:

```python
# Create multiple browser sessions
manager = BrowserManager(headless=True)
results = await manager.run_parallel_sessions(num_users=5)
```

Key features:
- Browser session lifecycle management
- Resource cleanup with context managers
- Configurable timeouts and retry logic
- Custom user agent and viewport settings
- Cookie consent dialog handling

### Checkout Flow (`checkout_flow.py`)

The checkout module handles e-commerce workflows:

```python
# Run end-to-end checkout
result = await run_checkout(page, user_id=1)
```

Implementation includes:
- Step-by-step checkout flow
- Error handling with recovery
- Screenshot capture at critical points
- Result tracking and metrics collection
- Smart retry mechanisms for flaky interactions

### API Mocking (`api_mock.py`)

Intercepts and mocks payment gateway APIs:

```python
# Setup payment mocking
await mock_payment_api(page)
```

Features:
- Pattern-based request interception
- Mock responses for payment gateways
- Request data extraction and analysis
- Analytics call blocking for performance

### Reporting (`reporting.py`)

Generates detailed HTML reports:

```python
# Generate performance report
report_path = generate_report(results)
```

Report includes:
- Success rate metrics
- Step completion analysis
- Performance charts
- Error summaries and screenshots
- Interactive HTML elements

### Test Stability Improvements

The framework includes several stability enhancements:

- **Cookie Consent Handling**: Automatically detects and handles cookie consent dialogs
- **Force Clicks**: Uses force:true for clicks when elements might be covered by overlays
- **Smart Selectors**: Fallback selectors when primary selectors fail
- **Direct Navigation**: Uses direct URL navigation as fallback for UI interactions
- **Screenshot Debugging**: Captures screenshots on errors for easy debugging
- **Timeout Configuration**: Customizable timeouts for different operations

## 📊 Screenshots and Example Output

The framework generates several artifacts during execution:

- **Screenshots**: Captured at key steps (login, product selection, checkout)
- **HTML Reports**: Detailed analysis of automation runs
- **Log Files**: Comprehensive logging with configurable detail level

## 🛠️ Customization

### Targeting Different E-Commerce Sites

The framework is pre-configured for a demo e-commerce site. To adapt to other sites:

1. Modify the selectors in `checkout_flow.py`
2. Update the URL in the login function
3. Adjust the payment flow based on the site's checkout process
4. Configure site-specific cookie consent selectors

### Adding Custom Steps

To add a new step to the checkout flow:

1. Create a new function in `checkout_flow.py`
2. Add the step to the `run_checkout` function
3. Update the step completion tracking

### Extending Reporting

The HTML reporting system can be extended:

1. Modify the HTML template in `reporting.py`
2. Add new metrics to the data collection
3. Create custom visualizations with additional charts

## 🧠 Testing Best Practices

This framework implements several testing best practices:

- **Isolation**: Each test runs in a fresh browser context
- **Modularity**: Tests are modular and focused on specific functionality
- **Resilience**: Error handling and recovery mechanisms
- **Documentation**: Clear comments and documentation
- **Configuration**: Externalized configuration for easy adjustment
- **Async Patterns**: Modern async/await patterns for better performance

## 🌟 Key Achievements

This framework demonstrates several technical achievements:

- **Resilient Automation**: Stable automation even with challenging UI elements
- **Performance Optimization**: Efficient execution through parallel processing
- **Modularity**: Easily extendable automation components
- **Comprehensive Reporting**: Detailed, visually appealing test reports
- **Error Recovery**: Smart retry mechanisms and fallback strategies

## 🤝 Contributing

Contributions to this project are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Playwright](https://playwright.dev/) - Modern web testing and automation framework
- [pytest](https://docs.pytest.org/) - Testing framework
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) - Async support for pytest
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine for HTML reports
- [Matplotlib](https://matplotlib.org/) - Data visualization
- [Loguru](https://github.com/Delgan/loguru) - Python logging
