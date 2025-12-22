# API AI Tester V7

🚀 **Intelligent API Testing Framework with AI-Powered Test Generation**

Automatically generate and execute comprehensive API tests from OpenAPI/Swagger specifications using AI or rule-based methods.

---

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation Guide](#installation-guide)
- [Running the Application](#running-the-application)
- [Using the Application](#using-the-application)
- [Supported LLM Models](#supported-llm-models)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

---

## ✨ Features

- ✅ **Automatic Test Generation** from OpenAPI/Swagger specifications
- 🤖 **AI-Powered Test Cases** using multiple LLM models (Llama, Qwen, Phi)
- ⚡ **Parallel Test Execution** with up to 10 concurrent workers (5-10x faster)
- 📊 **Comprehensive HTML Reports** with endpoint-wise statistics
- 📄 **JUnit XML Reports** for CI/CD integration
- 🔐 **API Key Authentication** support
- 🎯 **Petstore API Compatible** out of the box
- 🔢 **Sequential Test IDs** (test001, test002...) for better readability
- 🔄 **Test Case Reuse** for faster subsequent runs

---

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

### 1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, **check "Add Python to PATH"**

### 2. **Git** (optional, for cloning)
   - Download from: https://git-scm.com/downloads

### 3. **Ollama** (optional, for AI-powered test generation)
   - Download from: https://ollama.com/download
   - Required only if you want to use LLM models

---

## 📥 Installation Guide

### Step 1: Clone or Download the Repository

**Option A: Using Git**
```bash
git clone https://github.com/pranaybhaskar9851/APIAITester.git
cd APIAITester
```

**Option B: Download ZIP**
1. Click the green "Code" button on GitHub
2. Select "Download ZIP"
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

---

### Step 2: Create a Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

---

### Step 3: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

**Required packages include:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `requests` - HTTP client
- `jinja2` - Template engine
- `junit-xml` - JUnit report generation
- `ollama` - LLM integration (for AI features)

---

### Step 4: Install Ollama and LLM Models (Optional - For AI Features)

#### **Windows:**

1. **Download Ollama:**
   - Go to https://ollama.com/download
   - Download the Windows installer
   - Run the installer

2. **Verify Installation:**
   ```powershell
   # Add Ollama to PATH (if needed)
   $env:Path += ";C:\Users\<YourUsername>\AppData\Local\Programs\Ollama"
   
   # Test Ollama
   ollama --version
   ```

3. **Pull LLM Models:**
   ```powershell
   # Default model (recommended - 2GB)
   ollama pull llama3.2
   
   # Optional: Faster, smaller models
   ollama pull llama3.2:1b      # 1.3GB - Fastest
   ollama pull qwen2.5:0.5b     # 400MB - Ultra-light
   ollama pull phi3:mini        # 2.3GB - Efficient
   ```

#### **macOS/Linux:**

1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull Models:**
   ```bash
   ollama pull llama3.2
   ollama pull llama3.2:1b
   ollama pull qwen2.5:0.5b
   ollama pull phi3:mini
   ```

---

## 🚀 Running the Application

### Step 1: Start the Server

**Navigate to project directory (if not already there):**
```bash
cd path/to/api-ai-tester-v001
```

**Activate virtual environment (if you created one):**
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

**Start the FastAPI server:**
```bash
uvicorn app:app --reload --port 8000
```

**Alternative (if uvicorn command not found):**
```bash
python -m uvicorn app:app --reload --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 2: Access the Web Interface

Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

or

```
http://localhost:8000
```

You should see the API AI Tester interface! 🎉

---

## 🎯 Using the Application

### 1. **Configure API Settings**
   - **Base URL**: Enter the API base URL
     - Default: `https://petstore3.swagger.io/api/v3`
   - **Swagger/OpenAPI Spec URL**: Enter the OpenAPI specification URL
     - Default: `https://petstore3.swagger.io/api/v3/openapi.json`

### 2. **Authentication**
   - **API Key**: Enter your API key
     - Default: `test-api-key-123` (works with Petstore API)
     - Leave empty for public endpoints

### 3. **Test Generation Options**

   **Option A: Rule-Based Generation (No AI required)**
   - Leave "Use AI (Ollama)" unchecked
   - Generates tests based on OpenAPI specification
   - Fast and reliable
   - No Ollama installation needed

   **Option B: AI-Powered Generation (Requires Ollama)**
   - Check "Use AI (Ollama) for intelligent test generation"
   - Select LLM model from dropdown:
     - **Llama 3.2 1B** - Fastest (1.3GB)
     - **Llama 3.2 3B** - Balanced (2GB) - Recommended
     - **Qwen 2.5 0.5B** - Ultra-light (400MB)
     - **Phi 3 Mini** - Efficient (2.3GB)

### 4. **Run Tests**
   - Click **"▶ Run Tests"** button
   - Watch the progress overlay showing:
     - Loading API specification
     - Generating test cases
     - Executing test suite
     - Generating reports

### 5. **View Results**
   - After execution completes, you'll see:
     - **Execution ID** (timestamp)
     - Test statistics
     - Links to:
       - **📊 HTML Report** - Detailed endpoint-wise results
       - **📄 JUnit Report** - XML format for CI/CD

### 6. **Reuse Tests (Optional)**
   - Check "♻️ Reuse existing test cases"
   - Skips test generation step
   - Uses previously generated `test_cases.json`
   - Much faster for repeated executions

---

## 🤖 Supported LLM Models

| Model | Size | Speed | Best For | Install Command |
|-------|------|-------|----------|-----------------|
| **Llama 3.2 1B** | 1.3GB | ⚡⚡⚡ | Quick iterations, limited resources | `ollama pull llama3.2:1b` |
| **Llama 3.2 3B** | 2GB | ⚡⚡ | Balanced quality & speed (Default) | `ollama pull llama3.2` |
| **Qwen 2.5 0.5B** | 400MB | ⚡⚡⚡ | Minimal resources, ultra-fast | `ollama pull qwen2.5:0.5b` |
| **Phi 3 Mini** | 2.3GB | ⚡⚡ | Code understanding, efficiency | `ollama pull phi3:mini` |

**Note:** Smaller models are faster but may generate fewer test variations.

---

## 📁 Project Structure

```
api-ai-tester-v001/
│
├── app.py                      # FastAPI main application (Web UI & API endpoints)
├── requirements.txt            # Python package dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
│
├── engine/                     # Core testing engine
│   ├── swagger.py             # OpenAPI/Swagger specification loader
│   ├── generator.py           # Rule-based test case generator
│   ├── llm_generator.py       # AI-powered test case generator (LLM)
│   ├── executor.py            # Parallel test executor (ThreadPool)
│   └── report.py              # HTML & JUnit report generator
│
├── artifacts/                  # Test execution artifacts (requests/responses)
│   └── YYYYMMDD_HHMMSS/       # Timestamped execution folders
│       ├── test001_request.json
│       ├── test001_response.json
│       └── ...
│
├── reports/                    # Generated test reports
│   ├── report_YYYYMMDD_HHMMSS.html    # HTML report
│   └── junit_YYYYMMDD_HHMMSS.xml      # JUnit XML report
│
└── test_cases.json             # Generated test cases (cached for reuse)
```

---

## 🐛 Troubleshooting

### **Issue: Port 8000 already in use**

**Solution:**
```bash
# Use a different port
uvicorn app:app --reload --port 8080

# Then access: http://127.0.0.1:8080
```

---

### **Issue: `uvicorn: command not found`**

**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall
pip install uvicorn

# Or run directly with Python
python -m uvicorn app:app --reload --port 8000
```

---

### **Issue: `ollama: command not found` (Windows)**

**Solution:**
```powershell
# Add Ollama to PATH temporarily
$env:Path += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama"

# Or add permanently via System Environment Variables
# System Properties → Environment Variables → Path → Add:
# C:\Users\<YourUsername>\AppData\Local\Programs\Ollama
```

---

### **Issue: LLM generates fewer tests than expected**

**Solution:**
- The system automatically falls back to rule-based generation if LLM generates <80% of expected tests
- Use rule-based generation (uncheck AI option) for guaranteed complete coverage
- Try a different LLM model (Llama 3.2 3B is most reliable)

---

### **Issue: Module not found errors**

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

### **Issue: Tests fail with connection errors**

**Solution:**
- Check if the target API is accessible
- Verify Base URL and OpenAPI Spec URL are correct
- Check firewall/network settings
- For Petstore API, ensure internet connection is active

---

## ⚙️ Advanced Configuration

### **Changing Default Configuration**

Edit [app.py](app.py) to change default values:

```python
# Around line 528-535
value="https://petstore3.swagger.io/api/v3"           # Change Base URL
value="https://petstore3.swagger.io/api/v3/openapi.json"  # Change OpenAPI URL
value="test-api-key-123"                              # Change default API key
```

### **Adjusting Parallel Execution Workers**

Edit [executor.py](engine/executor.py):

```python
# Around line 84, change max_workers parameter
def execute_tests(tests, api_key, base_url, run_id, max_workers=10):
# Change 10 to your desired number (e.g., 5 for slower systems, 20 for faster)
```

### **Customizing Report Templates**

Edit [report.py](engine/report.py) to modify HTML report layout and styling.

---

## 📊 Reports Explained

### **HTML Report Features:**
- **Summary Cards**: Total endpoints, test cases, passed, failed
- **Endpoint Groups**: Tests organized by API endpoint
- **Per-Endpoint Stats**: Test count, pass/fail for each endpoint
- **Detailed Table**: Test ID, name, method, expected/actual status, errors
- **Visual Indicators**: ✅ PASS / ❌ FAIL with color coding

### **JUnit XML Report:**
- Compatible with CI/CD tools (Jenkins, GitHub Actions, etc.)
- Contains test suite results in standard XML format
- Can be integrated into automated pipelines

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

---

## 📝 License

MIT License

---

## 👤 Author

**Pranay Bhaskar**
- GitHub: [@pranaybhaskar9851](https://github.com/pranaybhaskar9851)

---

## 🎉 Quick Start Cheat Sheet

```bash
# 1. Clone repository
git clone https://github.com/pranaybhaskar9851/APIAITester.git
cd APIAITester

# 2. Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Install Ollama & models
ollama pull llama3.2

# 5. Run application
uvicorn app:app --reload --port 8000

# 6. Open browser
# http://127.0.0.1:8000
```

---

**Happy Testing! 🚀**
