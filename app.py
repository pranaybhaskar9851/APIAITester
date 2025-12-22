
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

app = FastAPI(title="API AI Tester V7")

@app.get("/", response_class=HTMLResponse)
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>API AI Tester V7</title>
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
            
            input[type="checkbox"] {
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
                <h1>🚀 API AI Tester V7</h1>
                <p>Intelligent API Testing Framework with AI-Powered Test Generation</p>
            </div>
            
            <div class="form-container">
                <form method="post" action="/run" onsubmit="handleSubmit(event)">
                    
                    <!-- API Configuration Section -->
                    <div class="section">
                        <div class="section-title">API Configuration</div>
                        <div class="form-group">
                            <label>Base URL</label>
                            <input type="text" name="base_url" value="https://petstore3.swagger.io/api/v3" placeholder="https://petstore3.swagger.io/api/v3"/>
                        </div>
                        <div class="form-group">
                            <label>Swagger/OpenAPI Spec URL</label>
                            <input type="text" name="swagger" value="https://petstore3.swagger.io/api/v3/openapi.json" placeholder="https://petstore3.swagger.io/api/v3/openapi.json"/>
                        </div>
                    </div>
                    
                    <!-- Authentication Section -->
                    <div class="section">
                        <div class="section-title">Authentication</div>
                        
                        <div class="info-box">
                            💡 <strong>Note:</strong> Enter your API key below. For Petstore API, you can use "test-api-key-123" as a test value.
                        </div>
                        
                        <div class="form-group">
                            <label>API Key <span class="label-help">(optional - leave empty for public endpoints)</span></label>
                            <input type="text" name="api_key" placeholder="Enter your API key" value="test-api-key-123"/>
                        </div>
                    </div>
                    
                    <!-- Test Generation Options Section -->
                    <div class="section">
                        <div class="section-title">Test Generation Options</div>
                        
                        <div class="checkbox-group">
                            <input type="checkbox" name="use_llm" value="true" id="use_llm"/>
                            <label for="use_llm" class="checkbox-label">
                                🤖 Use AI (Ollama) for intelligent test generation
                            </label>
                        </div>
                        
                        <div class="form-group">
                            <label>LLM Model <span class="label-help">(select a lightweight model)</span></label>
                            <select name="llm_model" style="width: 100%; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; transition: all 0.3s; background: white; cursor: pointer;">
                                <option value="llama3.2:1b">🦙 Llama 3.2 1B (Fastest - 1.3GB)</option>
                                <option value="llama3.2" selected>🦙 Llama 3.2 3B (Balanced - 2GB)</option>
                                <option value="qwen2.5:0.5b">🐉 Qwen 2.5 0.5B (Ultra-light - 400MB)</option>
                                <option value="phi3:mini">🔬 Phi 3 Mini (Efficient - 2.3GB)</option>
                            </select>
                        </div>
                        
                        <div class="info-box" style="background: #fff3e0; border-left-color: #ff9800; color: #e65100;">
                            💡 <strong>Model Info:</strong> Smaller models are faster but may generate fewer variations. Install with: <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">ollama pull [model]</code>
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
    use_llm: str = Form(""),
    llm_model: str = Form("llama3.2")
):
    import os
    import json
    
    tests_file = "test_cases.json"
    
    # Check if user wants to reuse existing tests
    if reuse_tests == "true" and os.path.exists(tests_file):
        print(f"Reusing existing test cases from {tests_file}")
        with open(tests_file, "r") as f:
            tests = json.load(f)
    else:
        # Generate new tests from Swagger
        spec = load_swagger(swagger)
        
        # Choose generation method based on user preference
        if use_llm == "true":
            print(f"Using LLM-based test generation with model: {llm_model}")
            tests = generate_tests_with_llm(spec, None, llm_model)
        else:
            print("Using Swagger-based test generation")
            tests = generate_tests(spec, None)
        
        # Save generated tests for future reuse
        with open(tests_file, "w") as f:
            json.dump(tests, f, indent=2)
        print(f"Generated {len(tests)} test cases and saved to {tests_file}")

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Execute tests with API key
    results = execute_tests(tests, api_key, base_url, run_id)

    generate_html_report(results, run_id)
    generate_junit(results, run_id)

    return {
        "status": "success",
        "execution_id": run_id,
        "html_report": f"/reports/report_{run_id}.html",
        "junit_report": f"/reports/junit_{run_id}.xml",
        "total_tests": len(results),
        "passed": sum(1 for r in results if r.get("status") == "PASS"),
        "failed": sum(1 for r in results if r.get("status") == "FAIL")
    }

@app.get("/reports/{filename}")
async def get_report(filename: str):
    file_path = os.path.join("reports", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Report not found"}
