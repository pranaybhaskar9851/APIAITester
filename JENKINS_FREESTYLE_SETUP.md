# Jenkins Freestyle Project Setup Guide for API AI Tester

This guide provides step-by-step instructions to set up a Jenkins **Freestyle Project** for the API AI Tester with user-configurable parameters.

---

## 📋 Prerequisites

Before starting, ensure:
- ✅ Jenkins server is running
- ✅ Windows VM is set up with Python, Ollama, and LLMs (see [WINDOWS_VM_SETUP.md](WINDOWS_VM_SETUP.md))
- ✅ Jenkins agent is configured on Windows VM with label `api-tester-vm`
- ✅ Required Jenkins plugins installed:
  - **Git Plugin**
  - **HTML Publisher Plugin**
  - **JUnit Plugin**

---

## 🚀 Step-by-Step Freestyle Project Setup

### Step 1: Create New Freestyle Project

1. Go to **Jenkins Dashboard**
2. Click **New Item**
3. Enter item name: `API-AI-Tester-Freestyle`
4. Select **Freestyle project**
5. Click **OK**

---

### Step 2: Configure General Settings

In the **General** section:

1. **Description**: 
   ```
   Automated API testing framework with AI-powered test generation.
   Tests are executed on Windows VM with Python, Ollama, and LLM models.
   ```

2. Check ✅ **Discard old builds**
   - **Days to keep builds**: `30`
   - **Max # of builds to keep**: `50`

3. Check ✅ **This project is parameterized**

---

### Step 3: Add Build Parameters

Click **Add Parameter** for each of the following:

#### Parameter 1: BASE_URL
- **Type**: String Parameter
- **Name**: `BASE_URL`
- **Default Value**: `https://petstore3.swagger.io/api/v3`
- **Description**: `The base URL of the API to test (e.g., https://petstore3.swagger.io/api/v3)`

#### Parameter 2: SWAGGER_URL
- **Type**: String Parameter
- **Name**: `SWAGGER_URL`
- **Default Value**: `https://petstore3.swagger.io/api/v3/openapi.json`
- **Description**: `Full URL to the OpenAPI/Swagger specification JSON file`

#### Parameter 3: API_KEY
- **Type**: Password Parameter
- **Name**: `API_KEY`
- **Default Value**: `test-api-key-123`
- **Description**: `API Key for authentication (optional - leave as default for public endpoints)`

#### Parameter 4: USE_AI
- **Type**: Boolean Parameter
- **Name**: `USE_AI`
- **Default Value**: ☐ Unchecked (false)
- **Description**: `Enable AI (Ollama) for intelligent test generation. Requires Ollama to be installed on the Windows VM.`

#### Parameter 5: LLM_MODEL
- **Type**: Choice Parameter
- **Name**: `LLM_MODEL`
- **Choices** (enter one per line):
  ```
  llama3.2:3b
  llama3.2:1b
  qwen2.5:3b
  qwen2.5:1.5b
  phi3:mini
  phi4:latest
  ```
- **Description**: `Select the LLM model to use (only applicable if USE_AI is enabled)`

#### Parameter 6: REUSE_TESTS
- **Type**: Boolean Parameter
- **Name**: `REUSE_TESTS`
- **Default Value**: ☐ Unchecked (false)
- **Description**: `Skip test generation and reuse existing test cases from test_cases.json (faster execution)`

#### Parameter 7: PYTHON_CMD
- **Type**: Choice Parameter
- **Name**: `PYTHON_CMD`
- **Choices** (enter one per line):
  ```
  python
  python3
  py
  ```
- **Description**: `Python command to use on the Windows VM (usually 'python' on Windows)`

---

### Step 4: Restrict Where Project Can Run

In the **General** section:

1. Check ✅ **Restrict where this project can be run**
2. **Label Expression**: `api-tester-vm`
3. You should see: "Label is serviced by 1 node(s)" (your Windows VM)

This ensures the job **ONLY runs on your Windows VM** with all the tools pre-installed!

---

### Step 5: Configure Source Code Management

In the **Source Code Management** section:

1. Select ⚫ **Git**
2. **Repository URL**: `https://github.com/pranaybhaskar9851/APIAITester.git`
3. **Credentials**: 
   - Select existing credentials if you have private repo
   - For public repo: Select `- none -`
4. **Branch Specifier**: `*/main`

**Advanced Options** (expand if needed):
- **Repository browser**: (auto)

---

### Step 6: Configure Build Triggers (Optional)

Choose when the job should run:

#### Option A: Manual Only (Default)
- Leave all unchecked - job runs only when triggered manually

#### Option B: Scheduled Builds
- Check ✅ **Build periodically**
- **Schedule** (cron syntax):
  ```
  H 2 * * *        # Daily at 2 AM
  H */4 * * *      # Every 4 hours
  H H * * 1-5      # Once per day on weekdays
  ```

#### Option C: GitHub Webhook (when code changes)
- Check ✅ **GitHub hook trigger for GITScm polling**
- Requires webhook configuration in GitHub (see Advanced section)

#### Option D: Poll SCM (check for changes)
- Check ✅ **Poll SCM**
- **Schedule**: `H/15 * * * *` (check every 15 minutes)

---

### Step 7: Configure Build Environment

1. Check ✅ **Delete workspace before build starts** (optional - for clean builds)
2. Check ✅ **Add timestamps to the Console Output** (recommended)

---

### Step 8: Add Build Step

In the **Build** section:

1. Click **Add build step**
2. Select **Execute Windows batch command**
3. **Command**:
   ```batch
   @echo off
   echo ============================================================================
   echo Running API AI Tester with parameters
   echo ============================================================================
   
   REM Execute the Jenkins batch script
   call jenkins_run.bat
   ```

---

### Step 9: Configure Post-build Actions

Click **Add post-build action** for each:

#### Action 1: Publish JUnit Test Results
1. Select **Publish JUnit test result report**
2. **Test report XMLs**: `reports/junit_*.xml`
3. Check ✅ **Retain long standard output/error**
4. **Health report amplification factor**: `1.0`

#### Action 2: Publish HTML Reports
1. Select **Publish HTML reports**
2. Click **Add** to add report
3. Configure:
   - **HTML directory to archive**: `reports`
   - **Index page[s]**: `report_*.html`
   - **Report title**: `API Test Report`
   - Check ✅ **Keep past HTML reports**

#### Action 3: Archive Artifacts
1. Select **Archive the artifacts**
2. **Files to archive**: 
   ```
   reports/**/*
   artifacts/**/*
   test_cases.json
   ```
3. Check ✅ **Archive artifacts only if build is successful** (optional)

#### Action 4: Email Notifications (Optional)
1. Select **E-mail Notification**
2. **Recipients**: `your-email@example.com`
3. Check ✅ **Send e-mail for every unstable build**
4. Check ✅ **Send separate e-mails to individuals who broke the build**

---

### Step 10: Save Configuration

Click **Save** at the bottom of the page.

---

## ▶️ Running the Freestyle Project

### First Time Execution

1. Go to project page: `API-AI-Tester-Freestyle`
2. Click **Build with Parameters** (on left sidebar)
3. Fill in the parameters:
   
   **Example Configuration:**
   ```
   BASE_URL: https://petstore3.swagger.io/api/v3
   SWAGGER_URL: https://petstore3.swagger.io/api/v3/openapi.json
   API_KEY: test-api-key-123
   USE_AI: ☐ Unchecked (start without AI first)
   LLM_MODEL: llama3.2:3b
   REUSE_TESTS: ☐ Unchecked
   PYTHON_CMD: python
   ```

4. Click **Build**

### Monitoring Execution

1. Watch the build appear in **Build History**
2. Click on the build number (e.g., `#1`)
3. Click **Console Output** to see live logs
4. Wait for completion (typically 2-10 minutes)

---

## 📊 Viewing Results

After build completes:

### Test Results
1. On build page, click **Test Result**
2. View passed/failed tests
3. Click individual tests for details

### HTML Report
1. On build page, click **API Test Report**
2. Interactive HTML report with:
   - Endpoint-wise statistics
   - Request/response details
   - Timing information

### Artifacts
1. On build page, click **Build Artifacts**
2. Download:
   - `reports/` - HTML and JUnit reports
   - `artifacts/` - Request/response data
   - `test_cases.json` - Generated test cases

### Console Output
1. Click **Console Output**
2. See full execution log
3. Useful for debugging

---

## 🔄 Running with Different Configurations

### Configuration 1: Quick Test (No AI)
```
USE_AI: ☐ Unchecked
REUSE_TESTS: ☐ Unchecked
```
**Duration**: ~2-3 minutes
**Use Case**: Quick validation, rule-based tests

### Configuration 2: AI-Powered Tests
```
USE_AI: ☑ Checked
LLM_MODEL: llama3.2:3b
REUSE_TESTS: ☐ Unchecked
```
**Duration**: ~5-10 minutes
**Use Case**: Comprehensive testing, first run

### Configuration 3: Fast Execution (Reuse)
```
REUSE_TESTS: ☑ Checked
```
**Duration**: ~1-2 minutes
**Use Case**: Re-run existing tests quickly

### Configuration 4: Your Custom API
```
BASE_URL: https://your-api.com/v1
SWAGGER_URL: https://your-api.com/v1/openapi.json
API_KEY: your-real-api-key-here
USE_AI: ☑ Checked
```
**Use Case**: Testing your own API

---

## 🎯 Verifying Node Selection

To confirm the job runs on correct Windows VM:

1. Start a build
2. Check **Console Output**
3. First few lines should show:
   ```
   Running on api-tester-vm in C:\Jenkins\workspace\API-AI-Tester-Freestyle
   ```

If it says "Running on master" or different node, check:
- Node label is `api-tester-vm`
- Node is online in Jenkins
- "Restrict where this project can be run" is checked

---

## 🔧 Advanced Configuration

### Add GitHub Webhook

To trigger builds automatically on code push:

1. **In Jenkins** (if not done):
   - Job configuration → Build Triggers
   - Check ✅ **GitHub hook trigger for GITScm polling**
   - Save

2. **In GitHub Repository**:
   - Go to **Settings** → **Webhooks** → **Add webhook**
   - **Payload URL**: `http://your-jenkins-url:8080/github-webhook/`
   - **Content type**: `application/json`
   - **Which events**: Select "Just the push event"
   - Check ✅ Active
   - Click **Add webhook**

### Email Notifications with Templates

For detailed email notifications:

1. Install **Email Extension Plugin**
2. In post-build actions, add **Editable Email Notification**
3. Configure:
   - **Project Recipient List**: `team@example.com`
   - **Triggers**: Success, Failure, Unstable
   - **Content**: Use default template or customize

### Parameterized Scheduling

To run different configurations at different times:

1. Install **Parameterized Scheduler Plugin**
2. In Build Triggers, use **Parameterized Scheduler**
3. Example:
   ```
   # Quick test every 2 hours
   H */2 * * * % REUSE_TESTS=true
   
   # Full AI test daily at 2 AM
   H 2 * * * % USE_AI=true;REUSE_TESTS=false
   ```

---

## 🐛 Troubleshooting

### Issue: "Build waiting for available executor"
**Cause**: Windows VM node is offline or busy  
**Solution**:
- Check node status in Jenkins → Manage Jenkins → Nodes
- Ensure `api-tester-vm` is online and has free executors
- Check Windows VM Jenkins agent service is running

### Issue: "Python not found"
**Cause**: Python not in PATH on Windows VM  
**Solution**:
- On Windows VM, verify: `python --version`
- Add Python to System PATH
- Restart Jenkins agent service

### Issue: "Ollama not found" when USE_AI=true
**Cause**: Ollama not installed or not in PATH  
**Solution**:
- On Windows VM, verify: `ollama --version`
- Install Ollama following [WINDOWS_VM_SETUP.md](WINDOWS_VM_SETUP.md)
- Restart Jenkins agent service

### Issue: Tests fail with 404 errors
**Cause**: Incorrect BASE_URL or SWAGGER_URL  
**Solution**:
- Verify URLs are accessible from Windows VM
- Test in browser: can you access the Swagger URL?
- Check firewall/network settings

### Issue: "No test results found"
**Cause**: Tests didn't run or reports not generated  
**Solution**:
- Check Console Output for errors
- Verify `reports/` directory exists in workspace
- Check JUnit pattern matches: `reports/junit_*.xml`

---

## 📋 Quick Reference

### Key Files in Repository
- `jenkins_run.bat` - Main execution script (called by Jenkins)
- `run_pipeline.py` - Python pipeline runner
- `requirements.txt` - Python dependencies
- `test_cases.json` - Generated/saved test cases

### Important Paths on Windows VM
- **Workspace**: `C:\Jenkins\workspace\API-AI-Tester-Freestyle`
- **Reports**: `C:\Jenkins\workspace\API-AI-Tester-Freestyle\reports`
- **Artifacts**: `C:\Jenkins\workspace\API-AI-Tester-Freestyle\artifacts`

### Console Output Indicators
- ✅ `SUCCESS: Virtual environment ready` - Dependencies installed
- ✅ `SUCCESS: Ollama and model verified` - AI ready (if enabled)
- ✅ `STATUS: SUCCESS - All tests passed` - All tests passed
- ❌ `STATUS: FAILED - Some tests failed` - Check reports

---

## ✅ Configuration Checklist

- [ ] Freestyle project created
- [ ] All 7 parameters configured
- [ ] Node restriction set to `api-tester-vm`
- [ ] Git repository configured (main branch)
- [ ] Build step added (Execute Windows batch command)
- [ ] JUnit test results publisher configured
- [ ] HTML report publisher configured
- [ ] Artifacts archiving configured
- [ ] Windows VM is online in Jenkins
- [ ] Test build executed successfully
- [ ] Reports accessible after build
- [ ] (Optional) Email notifications configured
- [ ] (Optional) Build triggers configured
- [ ] (Optional) GitHub webhook configured

---

## 🎉 You're All Set!

Your Jenkins Freestyle project is now configured to:
- ✅ Run exclusively on your Windows VM
- ✅ Accept user parameters for flexible testing
- ✅ Generate comprehensive reports
- ✅ Archive all artifacts
- ✅ Support both AI-powered and rule-based testing

Just click **Build with Parameters** and start testing! 🚀
