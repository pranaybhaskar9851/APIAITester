
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from engine.swagger import load_swagger
from engine.generator import generate_tests
from engine.llm_generator import generate_tests_with_llm
from engine.executor import execute_tests
from engine.report import generate_html_report, generate_junit
from datetime import datetime
import json
import os

app = FastAPI(title="API AI Tester")

@app.get("/fakestoreapi_swagger.json")
def get_fakestore_swagger():
    """Serve the FakeStoreAPI swagger file"""
    return FileResponse("fakestoreapi_swagger.json", media_type="application/json")

@app.get("/docs-data.json")
def get_docs_data():
    """Serve the docs-data.json OpenAPI specification file"""
    return FileResponse("docs-data.json", media_type="application/json")

@app.get("/", response_class=HTMLResponse)
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>API AI Tester</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 32px;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 14px;
                opacity: 0.9;
            }
            
            .form-container {
                padding: 40px;
            }
            
            .section {
                margin-bottom: 35px;
                border-left: 4px solid #667eea;
                padding-left: 20px;
            }
            
            .section-title {
                font-size: 18px;
                font-weight: 600;
                color: #333;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
            }
            
            .section-title::before {
                content: "";
                width: 8px;
                height: 8px;
                background: #667eea;
                border-radius: 50%;
                margin-right: 10px;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                font-size: 14px;
                font-weight: 500;
                color: #555;
                margin-bottom: 8px;
            }
            
            .label-help {
                font-weight: 400;
                color: #999;
                font-size: 12px;
                margin-left: 5px;
            }
            
            input[type="text"],
            input[type="password"],
            select {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                transition: all 0.3s;
            }
            
            input[type="text"]:focus,
            input[type="password"]:focus,
            select:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            select {
                background: white;
                cursor: pointer;
            }
            
            select option {
                padding: 10px;
            }
            
            .checkbox-group {
                display: flex;
                align-items: center;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 6px;
                margin-bottom: 15px;
            }
            
            input[type="checkbox"],
            input[type="radio"] {
                width: 20px;
                height: 20px;
                margin-right: 10px;
                cursor: pointer;
            }
            
            .checkbox-label {
                font-size: 14px;
                color: #333;
                cursor: pointer;
                user-select: none;
            }
            
            .submit-btn {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            
            .submit-btn:active {
                transform: translateY(0);
            }
            
            .info-box {
                background: #e3f2fd;
                border-left: 4px solid #2196f3;
                padding: 12px 15px;
                border-radius: 4px;
                font-size: 13px;
                color: #1976d2;
                margin-top: 10px;
            }
            
            .row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            
            @media (max-width: 768px) {
                .row {
                    grid-template-columns: 1fr;
                }
            }
            
            /* Loading Overlay */
            .loading-overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                z-index: 9999;
                justify-content: center;
                align-items: center;
            }
            
            .loading-overlay.active {
                display: flex;
            }
            
            .loading-content {
                background: white;
                padding: 40px 60px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }
            
            .spinner {
                width: 60px;
                height: 60px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .loading-title {
                font-size: 20px;
                font-weight: 600;
                color: #333;
                margin-bottom: 10px;
            }
            
            .loading-message {
                font-size: 14px;
                color: #666;
                margin-bottom: 5px;
            }
            
            .loading-steps {
                margin-top: 20px;
                text-align: left;
                font-size: 13px;
                color: #777;
                max-width: 400px;
            }
            
            .loading-step {
                padding: 8px 0;
                display: flex;
                align-items: center;
                transition: all 0.3s;
            }
            
            .loading-step::before {
                content: "⏳";
                margin-right: 10px;
                font-size: 16px;
            }
            
            .loading-step.completed::before {
                content: "✅";
            }
            
            .loading-step.in-progress {
                color: #667eea;
                font-weight: 600;
            }
            
            .loading-step.in-progress::before {
                content: "⚡";
                animation: pulse 1s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .step-detail {
                font-size: 11px;
                color: #999;
                margin-left: 26px;
                margin-top: -5px;
            }
            
            .success-content {
                display: none;
            }
            
            .success-content.active {
                display: block;
            }
            
            .success-icon {
                font-size: 60px;
                margin-bottom: 20px;
            }
            
            .success-title {
                font-size: 24px;
                font-weight: 600;
                color: #4caf50;
                margin-bottom: 10px;
            }
            
            .success-message {
                font-size: 14px;
                color: #666;
                margin-bottom: 25px;
            }
            
            .execution-id {
                background: #f5f5f5;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                color: #333;
                margin-bottom: 25px;
            }
            
            .report-links {
                display: flex;
                gap: 15px;
                justify-content: center;
            }
            
            .report-btn {
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.3s;
                display: inline-block;
            }
            
            .report-btn.primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .report-btn.primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .report-btn.secondary {
                background: #f5f5f5;
                color: #333;
                border: 2px solid #ddd;
            }
            
            .report-btn.secondary:hover {
                background: #e0e0e0;
            }
            
            .close-btn {
                position: absolute;
                top: 15px;
                right: 15px;
                width: 35px;
                height: 35px;
                border: none;
                background: #f5f5f5;
                border-radius: 50%;
                font-size: 20px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s;
                color: #666;
            }
            
            .close-btn:hover {
                background: #e0e0e0;
                transform: rotate(90deg);
            }
            
            .run-again-btn {
                margin-top: 20px;
                padding: 12px 24px;
                background: white;
                color: #667eea;
                border: 2px solid #667eea;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .run-again-btn:hover {
                background: #667eea;
                color: white;
            }
        </style>
        <script>
            function closePopup() {
                const overlay = document.getElementById('loadingOverlay');
                overlay.classList.remove('active');
                
                // Reset for next run
                const loadingContent = document.getElementById('loadingContent');
                const successContent = document.getElementById('successContent');
                loadingContent.style.display = 'block';
                successContent.classList.remove('active');
                
                // Reset step indicators
                document.querySelectorAll('.loading-step').forEach(step => {
                    step.classList.remove('completed');
                });
            }
            
            async function handleSubmit(event) {
                event.preventDefault();
                
                const overlay = document.getElementById('loadingOverlay');
                const loadingContent = document.getElementById('loadingContent');
                const successContent = document.getElementById('successContent');
                
                // Show loading overlay
                overlay.classList.add('active');
                loadingContent.classList.remove('hidden');
                successContent.classList.remove('active');
                
                // Simulate progress steps
                const steps = [
                    { id: 'step1', delay: 500 },
                    { id: 'step2', delay: 1500 }
                ];
                
                steps.forEach(step => {
                    setTimeout(() => {
                        const element = document.getElementById(step.id);
                        if (element) {
                            element.classList.add('completed');
                        }
                    }, step.delay);
                });
                
                // Submit form via fetch
                const form = event.target;
                const formData = new FormData(form);
                
                try {
                    const response = await fetch('/run', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    // Hide loading, show success
                    loadingContent.style.display = 'none';
                    successContent.classList.add('active');
                    
                    // Update success content
                    document.getElementById('executionId').textContent = data.execution_id;
                    document.getElementById('htmlReportLink').href = data.html_report;
                    document.getElementById('junitReportLink').href = data.junit_report;
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred during test execution. Please check the console for details.');
                    overlay.classList.remove('active');
                }
            }
            
            // Enable/disable LLM options based on test mode selection
            document.addEventListener('DOMContentLoaded', function() {
                const ruleMode = document.getElementById('rule_mode');
                const aiMode = document.getElementById('ai_mode');
                const llmOptions = document.getElementById('llm_options');
                const llmModel = document.getElementById('llm_model');
                
                function updateLLMOptions() {
                    if (aiMode && aiMode.checked) {
                        // Enable AI mode
                        llmOptions.style.opacity = '1';
                        llmOptions.style.pointerEvents = 'auto';
                        llmModel.disabled = false;
                        llmModel.style.background = 'white';
                        llmModel.style.cursor = 'pointer';
                    } else {
                        // Disable AI mode (Rule-based selected)
                        llmOptions.style.opacity = '0.5';
                        llmOptions.style.pointerEvents = 'none';
                        llmModel.disabled = true;
                        llmModel.style.background = '#f5f5f5';
                        llmModel.style.cursor = 'not-allowed';
                    }
                }
                
                // Listen for changes
                if (ruleMode) ruleMode.addEventListener('change', updateLLMOptions);
                if (aiMode) aiMode.addEventListener('change', updateLLMOptions);
                
                // Initialize on page load
                updateLLMOptions();
            });
        </script>
    </head>
    <body>
        <!-- Loading Overlay -->
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-content" id="loadingContent">
                <div class="spinner"></div>
                <div class="loading-title">Test Execution In Progress</div>
                <div class="loading-message">Processing your API tests with professional-grade validation...</div>
                <div class="loading-steps">
                    <div class="loading-step" id="step1">Loading API specification</div>
                    <div class="loading-step" id="step2">Generating test cases</div>
                    <div class="loading-step" id="step3">Executing test suite</div>
                    <div class="loading-step" id="step4">Generating reports</div>
                </div>
            </div>
            
            <!-- Success Content -->
            <div class="loading-content success-content" id="successContent">
                <button class="close-btn" onclick="closePopup()" title="Close">✕</button>
                <div class="success-icon">✅</div>
                <div id="testStats" style="margin: 15px 0; font-size: 14px; color: #666;"></div>
                <div class="success-title">Execution Completed Successfully!</div>
                <div class="success-message">Your API tests have been generated and executed.</div>
                <div class="execution-id">
                    Execution ID: <span id="executionId"></span>
                </div>
                <div class="report-links">
                    <a id="htmlReportLink" class="report-btn primary" target="_blank">📊 View HTML Report</a>
                    <a id="junitReportLink" class="report-btn secondary" target="_blank">📄 View JUnit Report</a>
                </div>
                <button class="run-again-btn" onclick="closePopup()">🔄 Run Tests Again</button>
            </div>
        </div>
        
        <div class="container">
            <div class="header">
                <h1>🚀 API AI Tester</h1>
                <p>Intelligent API Testing Framework with AI-Powered Test Generation</p>
            </div>
            
            <div class="form-container">
                <form method="post" action="/run" onsubmit="handleSubmit(event)">
                    
                    <!-- API Configuration Section -->
                    <div class="section">
                        <div class="section-title">API Configuration</div>
                        <div class="form-group">
                            <label>Base URL</label>
                            <input type="text" name="base_url" value="https://fakestoreapi.com" placeholder="https://fakestoreapi.com"/>
                        </div>
                        <div class="form-group">
                            <label>Swagger/OpenAPI Spec URL</label>
                            <input type="text" name="swagger" value="http://127.0.0.1:8000/fakestoreapi_swagger.json" placeholder="http://127.0.0.1:8000/fakestoreapi_swagger.json"/>
                        </div>
                    </div>
                    
                    <!-- Authentication Section -->
                    <div class="section">
                        <div class="section-title">Authentication</div>
                        
                        <div class="info-box">
                            💡 <strong>Note:</strong> Enter your API key below. For FakeStoreAPI, you can use "test-api-key-123" as a test value.
                        </div>
                        
                        <div class="form-group">
                            <label>API Key <span class="label-help">(optional - leave empty for public endpoints)</span></label>
                            <input type="text" name="api_key" placeholder="Enter your API key" value="test-api-key-123"/>
                        </div>
                    </div>
                    
                    <!-- Test Generation Options Section -->
                    <div class="section">
                        <div class="section-title">Test Generation Options</div>
                        
                        <!-- Strategy Info Box -->
                        <div class="info-box" style="background: #e8f5e9; border-left-color: #4caf50; color: #2e7d32; margin-bottom: 20px;">
                            <strong>📋 Choose Your Test Generation Strategy:</strong><br>
                            • <strong>Rule-Based:</strong> Fast, deterministic testing for standard CRUD APIs. Best for simple REST APIs with predictable patterns.<br>
                            • <strong>AI-Powered:</strong> Intelligent, context-aware test generation for complex APIs. Generates smarter scenarios, realistic data, and edge cases.
                        </div>
                        
                        <!-- Radio Button Selection -->
                        <div style="margin-bottom: 20px;">
                            <div class="checkbox-group" style="margin-bottom: 10px;">
                                <input type="radio" name="test_mode" value="rule" id="rule_mode" checked/>
                                <label for="rule_mode" class="checkbox-label">
                                    ⚙️ <strong>Rule-Based Generation</strong> <span style="color: #999; font-size: 12px;">(Fast, deterministic, no dependencies)</span>
                                </label>
                            </div>
                            
                            <div class="checkbox-group">
                                <input type="radio" name="test_mode" value="ai" id="ai_mode"/>
                                <label for="ai_mode" class="checkbox-label">
                                    🤖 <strong>AI-Powered Generation</strong> <span style="color: #999; font-size: 12px;">(Intelligent, context-aware, requires Ollama)</span>
                                </label>
                            </div>
                        </div>
                        
                        <!-- LLM Model Selection (disabled by default) -->
                        <div class="form-group" id="llm_options" style="opacity: 0.5; pointer-events: none; transition: all 0.3s;">
                            <label>LLM Model <span class="label-help">(select a lightweight model)</span></label>
                            <select name="llm_model" id="llm_model" disabled style="width: 100%; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; transition: all 0.3s; background: #f5f5f5; cursor: not-allowed;">
                                <option value="qwen2.5:0.5b">🐉 Qwen 2.5 0.5B (Ultra-light - 400MB)</option>
                                <option value="tinyllama:latest">🦙 TinyLlama Latest (Ultra-light - 637MB)</option>
                                <option value="llama3.2:1b" selected>🦙 Llama 3.2 1B (Fastest - 1.3GB)</option>
                                <option value="gemma3:1b">💎 Gemma 3 1B (Compact - 1GB)</option>
                                <option value="llama3:8b">🦙 Llama 3 8B (Powerful - 4.7GB)</option>
                                <option value="phi3:mini">🔬 Phi 3 Mini (Efficient - 2.3GB)</option>
                            </select>
                            
                            <div class="info-box" style="background: #fff3e0; border-left-color: #ff9800; color: #e65100; margin-top: 10px;">
                                💡 <strong>Setup Required:</strong> Install Ollama and pull a model: <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">ollama pull llama3.2:1b</code>
                            </div>
                        </div>
                        
                        <div class="checkbox-group">
                            <input type="checkbox" name="reuse_tests" value="true" id="reuse_tests"/>
                            <label for="reuse_tests" class="checkbox-label">
                                ♻️ Reuse existing test cases (skip generation)
                            </label>
                        </div>
                        
                        <div class="info-box">
                            ⚡ <strong>Tip:</strong> First run generates and saves tests. Next runs can reuse them for faster execution.
                        </div>
                    </div>
                    
                    <button type="submit" class="submit-btn">▶ Run Tests</button>
                    
                </form>
            </div>
        </div>
    </body>
    </html>
    '''

@app.post("/run")
async def run(
    base_url: str = Form(...),
    swagger: str = Form(...),
    api_key: str = Form(""),
    reuse_tests: str = Form(""),
    test_mode: str = Form("rule"),
    llm_model: str = Form("llama3.2:1b")
):
    import os
    import json
    import time
    import sys
    
    # Track execution timing
    execution_start = time.time()
    timings = {
        'swagger_load': 0,
        'test_generation': 0,
        'test_execution': 0,
        'report_generation': 0
    }
    
    print("\n" + "="*70, flush=True)
    print("API TEST EXECUTION PIPELINE STARTED", flush=True)
    print("="*70, flush=True)
    
    # Create testcases folder if it doesn't exist
    testcases_folder = "testcases"
    os.makedirs(testcases_folder, exist_ok=True)
    
    # Check if user wants to reuse existing tests
    if reuse_tests == "true":
        # Find the latest test case file
        test_files = [f for f in os.listdir(testcases_folder) if f.startswith("test_cases_") and f.endswith(".json")]
        if test_files:
            # Sort by filename (timestamp) to get the latest
            latest_test_file = sorted(test_files)[-1]
            tests_file_path = os.path.join(testcases_folder, latest_test_file)
            print(f"\n[STEP 1/4] Reusing existing test cases from {latest_test_file}", flush=True)
            with open(tests_file_path, "r", encoding="utf-8") as f:
                tests = json.load(f)
            print(f"✓ Loaded {len(tests)} test cases from file", flush=True)
            timings['test_generation'] = 0
            timings['swagger_load'] = 0
            generation_method = "Reused Existing Tests"
        else:
            print(f"\n[STEP 1/4] No existing test cases found, will generate new tests", flush=True)
            reuse_tests = "false"  # Force generation
    
    if reuse_tests != "true":
        # Step 1: Load Swagger specification
        print(f"\n[STEP 1/4] Loading Swagger specification...", flush=True)
        print(f"  Source: {swagger}", flush=True)
        step_start = time.time()
        spec = load_swagger(swagger)
        timings['swagger_load'] = time.time() - step_start
        print(f"✓ Swagger loaded successfully ({timings['swagger_load']:.2f}s)", flush=True)
        print(f"  Found {len(spec.get('paths', {}))} endpoints", flush=True)
        
        # Step 2: Generate tests based on selected mode
        print(f"\n[STEP 2/4] Generating test cases...", flush=True)
        step_start = time.time()
        if test_mode == "ai":
            print(f"  Method: AI-Powered generation", flush=True)
            print(f"  Model: {llm_model}", flush=True)
            tests = generate_tests_with_llm(spec, None, llm_model)
            generation_method = f"AI-Powered ({llm_model})"
        else:
            print(f"  Method: Rule-based generation", flush=True)
            tests = generate_tests(spec, None)
            generation_method = "Rule-based (Swagger)"
        timings['test_generation'] = time.time() - step_start
        print(f"✓ Generated {len(tests)} test cases ({timings['test_generation']:.2f}s)", flush=True)
        
        # Save generated tests with timestamp for future reuse
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tests_file = f"test_cases_{timestamp}.json"
        tests_file_path = os.path.join(testcases_folder, tests_file)
        with open(tests_file_path, "w", encoding="utf-8") as f:
            json.dump(tests, f, indent=2)
        print(f"  Saved to: {tests_file_path}", flush=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Step 3: Execute tests
    print(f"\n[STEP 3/4] Executing {len(tests)} test cases...", flush=True)
    print(f"  Base URL: {base_url}", flush=True)
    print(f"  Run ID: {run_id}", flush=True)
    step_start = time.time()
    results = execute_tests(tests, api_key, base_url, run_id)
    timings['test_execution'] = time.time() - step_start
    
    # Step 4: Generate reports
    print(f"\n[STEP 4/4] Generating reports...", flush=True)
    step_start = time.time()
    html_path = os.path.join("reports", f"report_{run_id}.html")
    junit_path = os.path.join("reports", f"junit_{run_id}.xml")
    
    # Pass timing and metadata to report generation
    timings['total_execution'] = time.time() - execution_start
    metadata = {
        'timings': timings,
        'generation_method': generation_method,
        'llm_model': llm_model if test_mode == "ai" else None,
        'base_url': base_url,
        'total_tests': len(tests)
    }
    
    generate_html_report(results, html_path, metadata)
    generate_junit(results, junit_path)
    timings['report_generation'] = time.time() - step_start
    
    print(f"✓ Reports generated ({timings['report_generation']:.2f}s)", flush=True)
    print(f"  HTML Report: {html_path}", flush=True)
    print(f"  JUnit Report: {junit_path}", flush=True)
    
    print(f"\n{'='*70}", flush=True)
    print(f"PIPELINE COMPLETED SUCCESSFULLY", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"Total Execution Time: {timings['total_execution']:.2f}s", flush=True)
    print(f"  • Swagger Load: {timings.get('swagger_load', 0):.2f}s", flush=True)
    print(f"  • Test Generation: {timings.get('test_generation', 0):.2f}s", flush=True)
    print(f"  • Test Execution: {timings.get('test_execution', 0):.2f}s", flush=True)
    print(f"  • Report Generation: {timings.get('report_generation', 0):.2f}s", flush=True)
    print(f"{'='*70}\n", flush=True)

    return {
        "status": "success",
        "execution_id": run_id,
        "html_report": f"/reports/report_{run_id}.html",
        "junit_report": f"/reports/junit_{run_id}.xml",
        "total_tests": len(results),
        "passed": sum(1 for r in results if r.get("passed") == True),
        "failed": sum(1 for r in results if r.get("passed") == False)
    }

@app.get("/benchmarks")
async def get_benchmarks_page():
    """Serve the benchmarks dashboard page"""
    # Get all benchmark result files from benchmarks folder
    benchmark_files = []
    benchmarks_dir = "benchmarks"
    if os.path.exists(benchmarks_dir):
        benchmark_files = sorted([f for f in os.listdir(benchmarks_dir) if f.startswith("benchmark_results_") and f.endswith(".json")], reverse=True)
    
    # Load the latest benchmark results
    latest_results = []
    if benchmark_files:
        try:
            with open(os.path.join(benchmarks_dir, benchmark_files[0]), 'r', encoding='utf-8') as f:
                latest_results = json.load(f)
        except:
            pass
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>LLM Benchmarks - API AI Tester</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #666;
            font-size: 16px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .results-table {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e0e0e0;
        }}
        td {{
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status-success {{
            background: #d4edda;
            color: #155724;
        }}
        .status-failed {{
            background: #f8d7da;
            color: #721c24;
        }}
        .status-timeout {{
            background: #fff3cd;
            color: #856404;
        }}
        .status-error {{
            background: #f8d7da;
            color: #721c24;
        }}
        .action-buttons {{
            margin-top: 20px;
            display: flex;
            gap: 10px;
        }}
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        .btn-primary:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        .btn-secondary {{
            background: #f8f9fa;
            color: #333;
        }}
        .btn-secondary:hover {{
            background: #e9ecef;
        }}
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .bar {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .bar-label {{
            width: 150px;
            font-size: 14px;
            font-weight: 500;
        }}
        .bar-visual {{
            flex: 1;
            height: 30px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 5px;
            position: relative;
            margin-right: 10px;
        }}
        .bar-value {{
            font-size: 14px;
            font-weight: 600;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 LLM Benchmarks Dashboard</h1>
            <p class="subtitle">Performance comparison of different LLM models for API test generation</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{len(latest_results)}</div>
                <div class="stat-label">Models Tested</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len([r for r in latest_results if r.get('status') == 'SUCCESS'])}</div>
                <div class="stat-label">Successful Runs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len([r for r in latest_results if r.get('status') != 'SUCCESS'])}</div>
                <div class="stat-label">Failed Runs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(r.get('tests_generated', 0) for r in latest_results if r.get('tests_generated'))}</div>
                <div class="stat-label">Total Tests Generated</div>
            </div>
        </div>
        
        {'<div class="chart-container"><h2 style="margin-bottom: 20px;">⏱️ Execution Time Comparison</h2>' + ''.join([f'<div class="bar"><div class="bar-label">{r["model"]}</div><div class="bar-visual" style="width: {min(100, (r["total_time"]/max([x.get("total_time", 1) for x in latest_results]))*100)}%"></div><div class="bar-value">{r["total_time"]:.1f}s</div></div>' for r in sorted([r for r in latest_results if r.get("status") == "SUCCESS"], key=lambda x: x.get("total_time", 9999))]) + '</div>' if latest_results and any(r.get("status") == "SUCCESS" for r in latest_results) else ''}
        
        <div class="results-table">
            <h2 style="margin-bottom: 20px;">📊 Detailed Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Status</th>
                        <th>Time (seconds)</th>
                        <th>Time (minutes)</th>
                        <th>Tests Generated</th>
                        <th>Tests Passed</th>
                        <th>Tests Failed</th>
                        <th>Pass Rate</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td><strong>{r["model"]}</strong></td>
                        <td><span class="status-badge status-{r["status"].lower()}">{r["status"]}</span></td>
                        <td>{r["total_time"]:.1f}s</td>
                        <td>{r["total_time"]/60:.1f}m</td>
                        <td>{r.get("tests_generated", "N/A")}</td>
                        <td>{r.get("tests_passed", "N/A")}</td>
                        <td>{r.get("tests_failed", "N/A")}</td>
                        <td>{f'{(r.get("tests_passed", 0) / r.get("tests_generated", 1) * 100):.1f}%' if r.get("tests_generated") else "N/A"}</td>
                    </tr>
                    ''' for r in latest_results]) if latest_results else '<tr><td colspan="8" style="text-align: center; padding: 40px; color: #999;">No benchmark results available. Run benchmark_llms.py to generate results.</td></tr>'}
                </tbody>
            </table>
            
            <div class="action-buttons">
                <a href="/" class="btn btn-secondary">← Back to Home</a>
                <button class="btn btn-primary" onclick="location.reload()">🔄 Refresh Results</button>
            </div>
        </div>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html)

@app.get("/reports/{filename}")
async def get_report(filename: str):
    file_path = os.path.join("reports", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Report not found"}
