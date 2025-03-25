"""
Reporting functionality for generating PDF reports with automation metrics.
"""
import os
import time
import io
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from loguru import logger
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from weasyprint import HTML, CSS
from jinja2 import Template


class ReportGenerator:
    """
    Generates detailed PDF reports for automation runs.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Report metadata
        self.report_date = datetime.now()
        self.report_id = f"report_{int(time.time())}"
    
    def _generate_summary_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary metrics from run results.
        
        Args:
            results: List of run result dictionaries
            
        Returns:
            Dictionary with summary metrics
        """
        total_runs = len(results)
        successful_runs = sum(1 for result in results if result.get("status") == "success")
        success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
        
        # Calculate timing metrics
        durations = [result.get("duration", 0) for result in results]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        # Get common failure points
        failed_steps = {}
        for result in results:
            if result.get("status") != "success" and result.get("error"):
                error = result.get("error")
                failed_steps[error] = failed_steps.get(error, 0) + 1
        
        # Sort by frequency
        common_failures = sorted(
            [(error, count) for error, count in failed_steps.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": total_runs - successful_runs,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "max_duration": max_duration,
            "min_duration": min_duration,
            "common_failures": common_failures[:5],  # Top 5 most common failures
        }
    
    def _generate_performance_chart(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a performance chart as a base64-encoded image.
        
        Args:
            results: List of run result dictionaries
            
        Returns:
            Base64-encoded image of the chart
        """
        # Extract data
        user_ids = [result.get("user_id", i) for i, result in enumerate(results)]
        durations = [result.get("duration", 0) for result in results]
        statuses = [result.get("status", "unknown") for result in results]
        
        # Create a color map
        colors = {
            "success": "green",
            "failed": "red",
            "error": "orange",
            "pending": "blue",
            "unknown": "gray"
        }
        
        bar_colors = [colors.get(status, "gray") for status in statuses]
        
        # Create chart
        plt.figure(figsize=(10, 6))
        plt.bar(user_ids, durations, color=bar_colors)
        plt.xlabel("User ID")
        plt.ylabel("Duration (seconds)")
        plt.title("E-commerce Checkout Duration by User")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        
        # Save to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_base64
    
    def _generate_step_completion_chart(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a chart showing step completion rates.
        
        Args:
            results: List of run result dictionaries
            
        Returns:
            Base64-encoded image of the chart
        """
        # Get all possible steps
        all_steps = set()
        for result in results:
            steps = result.get("steps_completed", [])
            all_steps.update(steps)
        
        # Calculate completion rates
        total_runs = len(results)
        step_counts = {step: 0 for step in all_steps}
        
        for result in results:
            steps = result.get("steps_completed", [])
            for step in steps:
                step_counts[step] += 1
        
        # Convert to percentage
        step_rates = {step: (count / total_runs) * 100 for step, count in step_counts.items()}
        
        # Sort steps
        step_order = [
            "login", "search", "add_to_cart", "proceed_to_checkout", 
            "handle_captcha", "fill_shipping_details", "select_shipping_method", "payment"
        ]
        
        # Filter and order steps that are in the data
        ordered_steps = [step for step in step_order if step in step_rates]
        
        # Create chart
        plt.figure(figsize=(12, 6))
        ordered_rates = [step_rates[step] for step in ordered_steps]
        plt.bar(ordered_steps, ordered_rates, color="skyblue")
        plt.xlabel("Checkout Step")
        plt.ylabel("Completion Rate (%)")
        plt.title("Step Completion Rate")
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        
        # Add percentage labels on top of bars
        for i, v in enumerate(ordered_rates):
            plt.text(i, v + 1, f"{v:.1f}%", ha='center')
        
        # Save to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_base64
    
    def _create_html_report(self, results: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
        """
        Create HTML report content.
        
        Args:
            results: List of run result dictionaries
            summary: Summary metrics dictionary
            
        Returns:
            HTML report content
        """
        # Generate charts
        performance_chart = self._generate_performance_chart(results)
        step_chart = self._generate_step_completion_chart(results)
        
        # Format date
        formatted_date = self.report_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Build HTML report
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>E-commerce Automation Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                }}
                .header h1 {{
                    margin-bottom: 5px;
                    color: #2c3e50;
                }}
                .header p {{
                    color: #7f8c8d;
                    margin: 0;
                }}
                .summary {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 30px;
                }}
                .summary h2 {{
                    margin-top: 0;
                    color: #2c3e50;
                }}
                .metrics {{
                    display: flex;
                    flex-wrap: wrap;
                    margin: 0 -10px;
                }}
                .metric {{
                    flex: 1;
                    margin: 10px;
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    min-width: 200px;
                }}
                .metric h3 {{
                    margin-top: 0;
                    color: #2c3e50;
                    font-size: 16px;
                }}
                .metric p {{
                    font-size: 24px;
                    font-weight: bold;
                    margin: 10px 0 0;
                    color: #3498db;
                }}
                .metric p.error {{
                    color: #e74c3c;
                }}
                .metric p.success {{
                    color: #27ae60;
                }}
                .charts {{
                    margin-bottom: 30px;
                }}
                .chart {{
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .chart h2 {{
                    margin-top: 0;
                    color: #2c3e50;
                }}
                .chart img {{
                    width: 100%;
                    height: auto;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                    color: #2c3e50;
                }}
                tr:hover {{
                    background-color: #f9f9f9;
                }}
                .success-rate {{
                    text-align: center;
                    font-size: 72px;
                    font-weight: bold;
                    margin: 30px 0;
                    color: #27ae60;
                }}
                .failures {{
                    background-color: #fff5f5;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 30px;
                }}
                .failures h2 {{
                    margin-top: 0;
                    color: #c0392b;
                }}
                .failures table {{
                    width: 100%;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #7f8c8d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>E-commerce Automation Report</h1>
                    <p>Generated on {formatted_date}</p>
                </div>
                
                <div class="summary">
                    <h2>Summary</h2>
                    <div class="metrics">
                        <div class="metric">
                            <h3>Total Runs</h3>
                            <p>{summary["total_runs"]}</p>
                        </div>
                        <div class="metric">
                            <h3>Successful Runs</h3>
                            <p class="success">{summary["successful_runs"]}</p>
                        </div>
                        <div class="metric">
                            <h3>Failed Runs</h3>
                            <p class="error">{summary["failed_runs"]}</p>
                        </div>
                        <div class="metric">
                            <h3>Average Duration</h3>
                            <p>{summary["avg_duration"]:.2f}s</p>
                        </div>
                    </div>
                    
                    <div class="success-rate">
                        {summary["success_rate"]:.1f}%
                    </div>
                </div>
                
                <div class="charts">
                    <div class="chart">
                        <h2>Performance by User</h2>
                        <img src="data:image/png;base64,{performance_chart}" alt="Performance Chart">
                    </div>
                    
                    <div class="chart">
                        <h2>Step Completion Rate</h2>
                        <img src="data:image/png;base64,{step_chart}" alt="Step Completion Chart">
                    </div>
                </div>
        """
        
        # Add failure section if there are failures
        if summary["common_failures"]:
            html += """
                <div class="failures">
                    <h2>Common Failures</h2>
                    <table>
                        <tr>
                            <th>Error</th>
                            <th>Count</th>
                        </tr>
            """
            
            for error, count in summary["common_failures"]:
                html += f"""
                        <tr>
                            <td>{error}</td>
                            <td>{count}</td>
                        </tr>
                """
                
            html += """
                    </table>
                </div>
            """
        
        # Add detailed results table
        html += """
                <h2>Detailed Results</h2>
                <table>
                    <tr>
                        <th>User ID</th>
                        <th>Status</th>
                        <th>Steps Completed</th>
                        <th>Duration (s)</th>
                        <th>Order ID</th>
                    </tr>
        """
        
        for result in results:
            status = result.get("status", "unknown")
            user_id = result.get("user_id", "N/A")
            duration = result.get("duration", 0)
            steps = result.get("steps_completed", [])
            steps_text = ", ".join(steps) if steps else "None"
            order_id = result.get("order_id", "N/A")
            
            html += f"""
                    <tr>
                        <td>{user_id}</td>
                        <td>{status}</td>
                        <td>{steps_text}</td>
                        <td>{duration:.2f}</td>
                        <td>{order_id}</td>
                    </tr>
            """
        
        html += """
                </table>
                
                <div class="footer">
                    <p>Generated with Playwright Python Automation Framework</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a PDF report from run results.
        
        Args:
            results: List of run result dictionaries
            
        Returns:
            Path to the generated PDF report
        """
        logger.info("Generating automation report")
        
        # Generate summary metrics
        summary = self._generate_summary_metrics(results)
        
        # Create HTML report
        html_content = self._create_html_report(results, summary)
        
        # Generate PDF from HTML
        html = HTML(string=html_content)
        css = CSS(string="""
            @page {
                margin: 1cm;
            }
        """)
        
        # Generate filename with timestamp
        timestamp = self.report_date.strftime("%Y%m%d_%H%M%S")
        filename = f"automation_report_{timestamp}.pdf"
        output_path = self.output_dir / filename
        
        # Generate PDF
        html.write_pdf(str(output_path), stylesheets=[css])
        
        logger.info(f"Report generated: {output_path}")
        
        return str(output_path)


def generate_report(results: List[Dict]) -> str:
    """
    Generate an HTML report from test results.
    
    Args:
        results: List of test result dictionaries
        
    Returns:
        Path to the generated report file
    """
    from datetime import datetime
    import os
    from jinja2 import Template
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    # Generate report filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"reports/automation_report_{timestamp}.html"
    
    # HTML template for the report
    template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Automation Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { text-align: center; margin-bottom: 30px; }
                .summary { margin-bottom: 30px; }
                .test-case { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }
                .success { background-color: #dff0d8; }
                .failed { background-color: #f2dede; }
                .steps { margin-left: 20px; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Automation Test Report</h1>
                <p>Generated on: {{ timestamp }}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {{ results|length }}</p>
                <p>Successful: {{ results|selectattr('status', 'equalto', 'success')|list|length }}</p>
                <p>Failed: {{ results|selectattr('status', 'equalto', 'failed')|list|length }}</p>
            </div>
            
            <div class="test-cases">
                <h2>Test Cases</h2>
                {% for result in results %}
                <div class="test-case {{ result.status }}">
                    <h3>Test Case #{{ result.user_id }}</h3>
                    <p>Status: {{ result.status }}</p>
                    <p>Duration: {{ result.duration }}s</p>
                    {% if result.order_id %}
                    <p>Order ID: {{ result.order_id }}</p>
                    {% endif %}
                    <div class="steps">
                        <h4>Steps Completed:</h4>
                        <ul>
                        {% for step in result.steps_completed %}
                            <li>{{ step }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                    {% if result.error %}
                    <div class="error">
                        <h4>Error:</h4>
                        <p>{{ result.error }}</p>
                    </div>
                    {% endif %}
                    {% if result.screenshots %}
                    <div class="screenshots">
                        <h4>Screenshots:</h4>
                        <ul>
                        {% for screenshot in result.screenshots %}
                            <li>{{ screenshot }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </body>
        </html>
    """)
    
    # Generate HTML content
    html_content = template.render(
        results=results,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # Write HTML to file
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    return output_path 