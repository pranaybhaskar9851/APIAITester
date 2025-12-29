
from jinja2 import Template
from junit_xml import TestSuite, TestCase
import os
from collections import defaultdict
import re

def generate_html_report(results, path, metadata=None):
    """Generate HTML report at the specified path"""
    # Ensure directory exists
    dir_path = os.path.dirname(path)
    if dir_path:  # Only create if there's a directory component
        os.makedirs(dir_path, exist_ok=True)
    
    # Extract run_id from path for display
    run_id = os.path.basename(path).replace('report_', '').replace('.html', '')
    
    # Extract metadata if provided
    if metadata is None:
        metadata = {}
    timings = metadata.get('timings', {})
    generation_method = metadata.get('generation_method', 'Unknown')
    llm_model = metadata.get('llm_model')
    base_url = metadata.get('base_url', 'N/A')
    total_tests_generated = metadata.get('total_tests', len(results))

    # Group results by endpoint
    endpoint_groups = defaultdict(list)
    for r in results:
        # Extract endpoint path (without query params and base URL)
        url = r.get('url', '')
        # Extract path from full URL
        if '/api/' in url:
            endpoint = '/' + url.split('/api/', 1)[1].split('?')[0]
        else:
            endpoint = r.get('url', 'Unknown')
        endpoint_groups[endpoint].append(r)
    
    # Calculate statistics
    total_endpoints = len(endpoint_groups)
    total_tests = len(results)
    total_passed = sum(1 for r in results if r.get('passed'))
    total_failed = total_tests - total_passed
    
    # Calculate per-endpoint statistics
    endpoint_stats = {}
    for endpoint, tests in endpoint_groups.items():
        passed = sum(1 for t in tests if t.get('passed'))
        failed = len(tests) - passed
        endpoint_stats[endpoint] = {
            'total': len(tests),
            'passed': passed,
            'failed': failed,
            'tests': tests
        }

    tpl = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Test Report - {{run_id}}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
            h2 { color: #333; margin-top: 40px; border-left: 4px solid #667eea; padding-left: 15px; }
            
            .execution-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }
            .execution-info h3 { margin-top: 0; color: #667eea; }
            .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; }
            .info-item { padding: 10px; background: white; border-radius: 4px; border: 1px solid #e0e0e0; }
            .info-item label { font-weight: 600; color: #666; font-size: 12px; text-transform: uppercase; display: block; margin-bottom: 5px; }
            .info-item value { color: #333; font-size: 16px; display: block; }
            
            .timing-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; margin: 30px 0; }
            .timing-section h3 { margin: 0 0 20px 0; font-size: 20px; }
            .timing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .timing-card { background: rgba(255,255,255,0.15); padding: 15px; border-radius: 6px; backdrop-filter: blur(10px); }
            .timing-card label { font-size: 12px; opacity: 0.9; display: block; margin-bottom: 8px; }
            .timing-card .time { font-size: 28px; font-weight: bold; }
            .timing-card .unit { font-size: 14px; opacity: 0.8; margin-left: 4px; }
            
            .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }
            .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-card h3 { margin: 0; font-size: 14px; opacity: 0.9; }
            .stat-card .number { font-size: 36px; font-weight: bold; margin: 10px 0; }
            .stat-card.success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
            .stat-card.failed { background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }
            .stat-card.endpoints { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
            
            .endpoint-section { margin: 30px 0; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
            .endpoint-header { background: #f8f9fa; padding: 15px 20px; border-bottom: 2px solid #667eea; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
            .endpoint-header:hover { background: #e9ecef; }
            .endpoint-title { font-size: 18px; font-weight: bold; color: #333; }
            .endpoint-stats { display: flex; gap: 15px; font-size: 14px; }
            .endpoint-stats span { padding: 5px 12px; border-radius: 4px; font-weight: 600; }
            .endpoint-stats .total { background: #e3f2fd; color: #1976d2; }
            .endpoint-stats .pass { background: #e8f5e9; color: #388e3c; }
            .endpoint-stats .fail { background: #ffebee; color: #d32f2f; }
            
            table { width: 100%; border-collapse: collapse; }
            th { background: #667eea; color: white; padding: 12px; text-align: left; font-weight: 600; }
            td { padding: 10px 12px; border-bottom: 1px solid #eee; }
            tr:hover { background: #f8f9fa; }
            .passed-true { color: #388e3c; font-weight: bold; }
            .passed-false { color: #d32f2f; font-weight: bold; }
            .test-id { font-family: monospace; background: #f5f5f5; padding: 4px 8px; border-radius: 4px; }
            .error-cell { color: #d32f2f; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>API AI Tester Report - {{run_id}}</h1>
            
            {% if timings %}
            <div class="timing-section">
                <h3>Execution Timeline</h3>
                <div class="timing-grid">
                    {% if timings.swagger_load > 0 %}
                    <div class="timing-card">
                        <label>SWAGGER SPEC LOAD</label>
                        <div class="time">{{\"%.2f\"|format(timings.swagger_load)}}<span class="unit">sec</span></div>
                    </div>
                    {% endif %}
                    {% if timings.test_generation > 0 %}
                    <div class="timing-card">
                        <label>TEST GENERATION</label>
                        <div class="time">{{\"%.2f\"|format(timings.test_generation)}}<span class="unit">sec</span></div>
                    </div>
                    {% endif %}
                    <div class="timing-card">
                        <label>TEST EXECUTION</label>
                        <div class="time">{{\"%.2f\"|format(timings.test_execution)}}<span class="unit">sec</span></div>
                    </div>
                    {% if timings.report_generation %}
                    <div class="timing-card">
                        <label>REPORT GENERATION</label>
                        <div class="time">{{\"%.2f\"|format(timings.report_generation)}}<span class="unit">sec</span></div>
                    </div>
                    {% endif %}
                    <div class="timing-card" style="background: rgba(255,255,255,0.25);">
                        <label>TOTAL TIME</label>
                        <div class="time">{{\"%.2f\"|format(timings.total_execution)}}<span class="unit">sec</span></div>
                    </div>
                </div>
            </div>
            {% endif %}
            
            <div class="execution-info">
                <h3>Execution Details</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Test Generation Method</label>
                        <value>{{generation_method}}</value>
                    </div>
                    {% if llm_model %}
                    <div class="info-item">
                        <label>LLM Model Used</label>
                        <value>{{llm_model}}</value>
                    </div>
                    {% endif %}
                    <div class="info-item">
                        <label>Base URL</label>
                        <value>{{base_url}}</value>
                    </div>
                    <div class="info-item">
                        <label>Tests Generated</label>
                        <value>{{total_tests_generated}}</value>
                    </div>
                </div>
            </div>
            
            <h2>Test Results Summary</h2>
            <div class="summary">
                <div class="stat-card endpoints">
                    <h3>ENDPOINTS TESTED</h3>
                    <div class="number">{{total_endpoints}}</div>
                </div>
                <div class="stat-card">
                    <h3>TOTAL TEST CASES</h3>
                    <div class="number">{{total_tests}}</div>
                </div>
                <div class="stat-card success">
                    <h3>PASSED</h3>
                    <div class="number">{{total_passed}}</div>
                </div>
                <div class="stat-card failed">
                    <h3>FAILED</h3>
                    <div class="number">{{total_failed}}</div>
                </div>
            </div>

            <h2 style="margin-top: 40px; color: #333;">📊 Endpoint-wise Results</h2>
            
            {% for endpoint, stats in endpoint_stats.items() %}
            <div class="endpoint-section">
                <div class="endpoint-header">
                    <div class="endpoint-title">{{endpoint}}</div>
                    <div class="endpoint-stats">
                        <span class="total">{{stats.total}} tests</span>
                        <span class="pass">✓ {{stats.passed}} passed</span>
                        <span class="fail">✗ {{stats.failed}} failed</span>
                    </div>
                </div>
                <table>
                    <tr>
                        <th>Test ID</th>
                        <th>Test Name</th>
                        <th>Method</th>
                        <th>Expected</th>
                        <th>Actual</th>
                        <th>Status</th>
                        <th>Error</th>
                    </tr>
                    {% for test in stats.tests %}
                    <tr>
                        <td><span class="test-id">{{test.id}}</span></td>
                        <td>{{test.name}}</td>
                        <td><strong>{{test.url.split('/')[-1].split('?')[0] if '/' in test.url else 'N/A'}}</strong></td>
                        <td>{{test.expected if test.expected is defined else "-"}}</td>
                        <td>{{test.actual if test.actual is defined else "-"}}</td>
                        <td class="{% if test.passed %}passed-true{% else %}passed-false{% endif %}">
                            {% if test.passed %}✅ PASS{% else %}❌ FAIL{% endif %}
                        </td>
                        <td class="error-cell">{{test.error if test.error is defined else ""}}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(tpl.render(
            results=results, 
            run_id=run_id,
            total_endpoints=total_endpoints,
            total_tests=total_tests,
            total_passed=total_passed,
            total_failed=total_failed,
            endpoint_stats=endpoint_stats,
            timings=timings,
            generation_method=generation_method,
            llm_model=llm_model,
            base_url=base_url,
            total_tests_generated=total_tests_generated
        ))

def generate_junit(results, path):
    """Generate JUnit XML report at the specified path"""
    # Ensure directory exists
    dir_path = os.path.dirname(path)
    if dir_path:  # Only create if there's a directory component
        os.makedirs(dir_path, exist_ok=True)
    
    # Extract run_id from path for display
    run_id = os.path.basename(path).replace('junit_', '').replace('.xml', '')
    
    cases = []
    for r in results:
        tc = TestCase(r["name"])
        if not r.get("passed", False):
            tc.add_failure_info(
                message=f"Expected {r.get('expected')} got {r.get('actual')}",
                output=r.get("error", "")
            )
        cases.append(tc)
    suite = TestSuite(f"API-AI-Tester-{run_id}", cases)
    with open(path, "w", encoding="utf-8") as f:
        TestSuite.to_file(f, [suite])
