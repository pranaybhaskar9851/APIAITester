# Jenkins CI/CD Pipeline Setup Guide for API AI Tester

## 📋 Overview

This guide provides step-by-step instructions to set up a Jenkins CI/CD pipeline for the API AI Tester project with user-configurable parameters.

---

## 🎯 Prerequisites

### 1. Jenkins Server Setup
- Jenkins 2.387+ installed and running
- Required Jenkins Plugins:
  - **Git Plugin** (for GitHub integration)
  - **Pipeline Plugin** (for Jenkinsfile support)
  - **HTML Publisher Plugin** (for publishing HTML reports)
  - **JUnit Plugin** (for test results)
  - **Parameter Plugin** (built-in)
  - **Credentials Plugin** (built-in)

### 2. Jenkins Server Requirements
- Python 3.8+ installed on Jenkins agent/server
- pip package manager
- Internet access for downloading dependencies

### 3. Optional (for AI-powered tests)
- Ollama installed on Jenkins agent/server
- Required LLM models pulled (e.g., `ollama pull llama3.2:3b`)

---

## 📝 Step-by-Step Jenkins Pipeline Setup

### Step 1: Install Required Jenkins Plugins

1. Navigate to **Jenkins Dashboard** → **Manage Jenkins** → **Plugins**
2. Go to **Available Plugins** tab
3. Search and install these plugins:
   - HTML Publisher Plugin
   - JUnit Plugin
   - Git Plugin
   - Pipeline Plugin
4. Restart Jenkins if required

---

### Step 2: Create GitHub Credentials (Optional but Recommended)

1. Go to **Jenkins Dashboard** → **Manage Jenkins** → **Credentials**
2. Click on **(global)** domain
3. Click **Add Credentials**
4. Configure:
   - **Kind**: Username with password
   - **Username**: Your GitHub username
   - **Password**: Your GitHub Personal Access Token
   - **ID**: `github-credentials` (or any meaningful ID)
   - **Description**: GitHub Access Token
5. Click **Create**

---

### Step 3: Create New Jenkins Pipeline Job

1. Go to **Jenkins Dashboard**
2. Click **New Item**
3. Enter job name: `API-AI-Tester-Pipeline`
4. Select **Pipeline** project type
5. Click **OK**

---

### Step 4: Configure Pipeline Parameters

In the job configuration page:

1. Check **"This project is parameterized"**
2. Add the following parameters:

#### Parameter 1: Base URL
- Click **Add Parameter** → **String Parameter**
- **Name**: `BASE_URL`
- **Default Value**: `https://petstore3.swagger.io/api/v3`
- **Description**: `The base URL of the API to test (e.g., https://petstore3.swagger.io/api/v3)`

#### Parameter 2: Swagger/OpenAPI Spec URL
- Click **Add Parameter** → **String Parameter**
- **Name**: `SWAGGER_URL`
- **Default Value**: `https://petstore3.swagger.io/api/v3/openapi.json`
- **Description**: `Full URL to the OpenAPI/Swagger specification JSON file`

#### Parameter 3: API Key
- Click **Add Parameter** → **Password Parameter**
- **Name**: `API_KEY`
- **Default Value**: `test-api-key-123`
- **Description**: `API Key for authentication (optional - leave empty for public endpoints)`

#### Parameter 4: Use AI for Test Generation
- Click **Add Parameter** → **Boolean Parameter**
- **Name**: `USE_AI`
- **Default Value**: `false`
- **Description**: `Enable AI (Ollama) for intelligent test generation. Requires Ollama to be installed.`

#### Parameter 5: LLM Model Selection
- Click **Add Parameter** → **Choice Parameter**
- **Name**: `LLM_MODEL`
- **Choices** (one per line):
  ```
  llama3.2:3b
  llama3.2:1b
  qwen2.5:3b
  qwen2.5:1.5b
  phi3:mini
  phi4:latest
  ```
- **Description**: `Select the LLM model to use (only applicable if USE_AI is enabled)`

#### Parameter 6: Reuse Existing Test Cases
- Click **Add Parameter** → **Boolean Parameter**
- **Name**: `REUSE_TESTS`
- **Default Value**: `false`
- **Description**: `Skip test generation and reuse existing test cases from test_cases.json (faster execution)`

#### Parameter 7: Python Command
- Click **Add Parameter** → **Choice Parameter**
- **Name**: `PYTHON_CMD`
- **Choices** (one per line):
  ```
  python
  python3
  py
  ```
- **Description**: `Python command to use (depends on your Jenkins agent OS)`

---

### Step 5: Configure Pipeline Script

Scroll down to the **Pipeline** section and select:
- **Definition**: Pipeline script from SCM

Configure SCM:
- **SCM**: Git
- **Repository URL**: `https://github.com/pranaybhaskar9851/APIAITester.git`
- **Credentials**: Select the GitHub credentials created earlier (or leave as "none" for public repo)
- **Branch Specifier**: `*/main`
- **Script Path**: `Jenkinsfile`

---

### Step 6: Create Jenkinsfile in Repository

Create a file named `Jenkinsfile` in the root of your repository with the following content:

```groovy
pipeline {
    agent any
    
    parameters {
        string(
            name: 'BASE_URL',
            defaultValue: 'https://petstore3.swagger.io/api/v3',
            description: 'The base URL of the API to test'
        )
        string(
            name: 'SWAGGER_URL',
            defaultValue: 'https://petstore3.swagger.io/api/v3/openapi.json',
            description: 'Full URL to the OpenAPI/Swagger specification'
        )
        password(
            name: 'API_KEY',
            defaultValue: 'test-api-key-123',
            description: 'API Key for authentication (optional)'
        )
        booleanParam(
            name: 'USE_AI',
            defaultValue: false,
            description: 'Enable AI (Ollama) for intelligent test generation'
        )
        choice(
            name: 'LLM_MODEL',
            choices: ['llama3.2:3b', 'llama3.2:1b', 'qwen2.5:3b', 'qwen2.5:1.5b', 'phi3:mini', 'phi4:latest'],
            description: 'Select the LLM model to use (if USE_AI is enabled)'
        )
        booleanParam(
            name: 'REUSE_TESTS',
            defaultValue: false,
            description: 'Skip generation and reuse existing test cases'
        )
        choice(
            name: 'PYTHON_CMD',
            choices: ['python', 'python3', 'py'],
            description: 'Python command to use'
        )
    }
    
    environment {
        VENV_DIR = 'venv'
        TIMESTAMP = sh(returnStdout: true, script: "date +%Y%m%d_%H%M%S").trim()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "📦 Checking out code from GitHub..."
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo "🐍 Setting up Python virtual environment..."
                script {
                    if (isUnix()) {
                        sh """
                            ${params.PYTHON_CMD} -m venv ${VENV_DIR}
                            . ${VENV_DIR}/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        """
                    } else {
                        bat """
                            ${params.PYTHON_CMD} -m venv ${VENV_DIR}
                            call ${VENV_DIR}\\Scripts\\activate.bat
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        """
                    }
                }
            }
        }
        
        stage('Verify Ollama Setup') {
            when {
                expression { params.USE_AI == true }
            }
            steps {
                echo "🤖 Verifying Ollama installation and model..."
                script {
                    if (isUnix()) {
                        sh """
                            ollama --version || echo "⚠️  Ollama not installed"
                            ollama list | grep ${params.LLM_MODEL} || echo "⚠️  Model ${params.LLM_MODEL} not found"
                        """
                    } else {
                        bat """
                            ollama --version || echo "Ollama not installed"
                            ollama list | findstr ${params.LLM_MODEL} || echo "Model ${params.LLM_MODEL} not found"
                        """
                    }
                }
            }
        }
        
        stage('Generate Test Configuration') {
            steps {
                echo "⚙️  Generating test configuration..."
                script {
                    def configJson = """
                    {
                        "base_url": "${params.BASE_URL}",
                        "swagger_url": "${params.SWAGGER_URL}",
                        "api_key": "${params.API_KEY}",
                        "use_ai": ${params.USE_AI},
                        "llm_model": "${params.LLM_MODEL}",
                        "reuse_tests": ${params.REUSE_TESTS}
                    }
                    """
                    writeFile file: 'pipeline_config.json', text: configJson
                    echo "Configuration saved to pipeline_config.json"
                }
            }
        }
        
        stage('Run API Tests') {
            steps {
                echo "🧪 Running API tests..."
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV_DIR}/bin/activate
                            ${params.PYTHON_CMD} -u run_pipeline.py \
                                --base-url "${params.BASE_URL}" \
                                --swagger-url "${params.SWAGGER_URL}" \
                                --api-key "${params.API_KEY}" \
                                ${params.USE_AI ? '--use-ai' : ''} \
                                --llm-model "${params.LLM_MODEL}" \
                                ${params.REUSE_TESTS ? '--reuse-tests' : ''}
                        """
                    } else {
                        bat """
                            call ${VENV_DIR}\\Scripts\\activate.bat
                            ${params.PYTHON_CMD} -u run_pipeline.py ^
                                --base-url "${params.BASE_URL}" ^
                                --swagger-url "${params.SWAGGER_URL}" ^
                                --api-key "${params.API_KEY}" ^
                                ${params.USE_AI ? '--use-ai' : ''} ^
                                --llm-model "${params.LLM_MODEL}" ^
                                ${params.REUSE_TESTS ? '--reuse-tests' : ''}
                        """
                    }
                }
            }
        }
        
        stage('Publish Reports') {
            steps {
                echo "📊 Publishing test reports..."
                
                // Publish JUnit test results
                junit allowEmptyResults: true, testResults: 'reports/junit_*.xml'
                
                // Publish HTML report
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report_*.html',
                    reportName: 'API Test Report',
                    reportTitles: 'API AI Tester Results'
                ])
                
                // Archive artifacts
                archiveArtifacts artifacts: 'reports/**,artifacts/**,test_cases.json,pipeline_config.json', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo "🧹 Cleaning up workspace..."
            cleanWs(
                deleteDirs: true,
                patterns: [
                    [pattern: 'venv/**', type: 'INCLUDE'],
                    [pattern: '__pycache__/**', type: 'INCLUDE']
                ]
            )
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
    }
}
```

---

### Step 7: Create Pipeline Runner Script

Create a file named `run_pipeline.py` in the root of your repository:

```python
#!/usr/bin/env python3
"""
Jenkins Pipeline Runner Script for API AI Tester
This script is called by Jenkins with command-line parameters
"""

import argparse
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.swagger import load_swagger
from engine.generator import generate_tests
from engine.llm_generator import generate_tests_with_llm
from engine.executor import execute_tests
from engine.report import generate_html_report, generate_junit


def main():
    parser = argparse.ArgumentParser(description='API AI Tester Pipeline Runner')
    parser.add_argument('--base-url', required=True, help='Base URL of the API')
    parser.add_argument('--swagger-url', required=True, help='Swagger/OpenAPI spec URL')
    parser.add_argument('--api-key', default='', help='API Key for authentication')
    parser.add_argument('--use-ai', action='store_true', help='Use AI for test generation')
    parser.add_argument('--llm-model', default='llama3.2:3b', help='LLM model to use')
    parser.add_argument('--reuse-tests', action='store_true', help='Reuse existing test cases')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🚀 API AI Tester Pipeline Started")
    print("=" * 80)
    print(f"📍 Base URL: {args.base_url}")
    print(f"📄 Swagger URL: {args.swagger_url}")
    print(f"🔑 API Key: {'***' if args.api_key else 'None'}")
    print(f"🤖 Use AI: {args.use_ai}")
    print(f"🧠 LLM Model: {args.llm_model}")
    print(f"♻️  Reuse Tests: {args.reuse_tests}")
    print("=" * 80)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Step 1: Load Swagger/OpenAPI specification
        print("\n📥 Step 1: Loading API specification...")
        swagger_doc = load_swagger(args.swagger_url)
        print(f"✅ Loaded specification with {len(swagger_doc.get('paths', {}))} endpoints")
        
        # Step 2: Generate or load test cases
        if args.reuse_tests and os.path.exists('test_cases.json'):
            print("\n♻️  Step 2: Loading existing test cases...")
            with open('test_cases.json', 'r') as f:
                test_cases = json.load(f)
            print(f"✅ Loaded {len(test_cases)} existing test cases")
        else:
            if args.use_ai:
                print(f"\n🤖 Step 2: Generating tests with AI (Model: {args.llm_model})...")
                test_cases = generate_tests_with_llm(swagger_doc, args.base_url, args.llm_model)
            else:
                print("\n📝 Step 2: Generating tests with rule-based generator...")
                test_cases = generate_tests(swagger_doc, args.base_url)
            
            print(f"✅ Generated {len(test_cases)} test cases")
            
            # Save test cases
            with open('test_cases.json', 'w') as f:
                json.dump(test_cases, f, indent=2)
            print("💾 Test cases saved to test_cases.json")
        
        # Step 3: Execute tests
        print("\n🧪 Step 3: Executing API tests...")
        results = execute_tests(test_cases, args.api_key, timestamp)
        print(f"✅ Executed {len(results)} tests")
        
        # Step 4: Generate reports
        print("\n📊 Step 4: Generating reports...")
        
        # HTML Report
        html_report_path = f"reports/report_{timestamp}.html"
        generate_html_report(results, html_report_path)
        print(f"✅ HTML report: {html_report_path}")
        
        # JUnit XML Report
        junit_report_path = f"reports/junit_{timestamp}.xml"
        generate_junit(results, junit_report_path)
        print(f"✅ JUnit report: {junit_report_path}")
        
        # Step 5: Print summary
        print("\n" + "=" * 80)
        print("📈 Test Execution Summary")
        print("=" * 80)
        
        passed = sum(1 for r in results if r.get('status') == 'PASS')
        failed = sum(1 for r in results if r.get('status') == 'FAIL')
        skipped = sum(1 for r in results if r.get('status') == 'SKIP')
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"📊 Total: {len(results)}")
        print(f"📈 Success Rate: {(passed/len(results)*100):.1f}%")
        print("=" * 80)
        
        # Exit with appropriate code
        if failed > 0:
            print("\n⚠️  Some tests failed. Check reports for details.")
            sys.exit(1)
        else:
            print("\n✅ All tests passed!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

### Step 8: Commit and Push to GitHub

```bash
# Add the new files
git add Jenkinsfile run_pipeline.py JENKINS_CICD_SETUP.md

# Commit
git commit -m "Add Jenkins CI/CD pipeline configuration"

# Push to main branch
git push origin main
```

---

### Step 9: Run the Pipeline

1. Go to your Jenkins job: `API-AI-Tester-Pipeline`
2. Click **Build with Parameters**
3. Fill in the parameters:
   - **BASE_URL**: e.g., `https://petstore3.swagger.io/api/v3`
   - **SWAGGER_URL**: e.g., `https://petstore3.swagger.io/api/v3/openapi.json`
   - **API_KEY**: Your API key or leave as default
   - **USE_AI**: Check if you want AI-powered tests (requires Ollama)
   - **LLM_MODEL**: Select model if USE_AI is checked
   - **REUSE_TESTS**: Check to skip generation and reuse existing tests
   - **PYTHON_CMD**: Select appropriate Python command
4. Click **Build**

---

## 📊 Viewing Results

### Test Results
- Navigate to your build
- Click **Test Result** to see JUnit test results
- Click **API Test Report** to see detailed HTML report

### Artifacts
- Click **Build Artifacts** to download:
  - Test cases JSON
  - HTML reports
  - JUnit XML reports
  - Execution artifacts

---

## 🔧 Advanced Configuration

### Configure Email Notifications

Add to the `post` section of Jenkinsfile:

```groovy
post {
    failure {
        emailext(
            subject: "❌ API Tests Failed - Build #${BUILD_NUMBER}",
            body: """
                Build Failed: ${BUILD_URL}
                
                Check the build logs and test reports for details.
            """,
            to: 'your-email@example.com'
        )
    }
    success {
        emailext(
            subject: "✅ API Tests Passed - Build #${BUILD_NUMBER}",
            body: """
                All tests passed! 
                
                View reports: ${BUILD_URL}api-test-report/
            """,
            to: 'your-email@example.com'
        )
    }
}
```

### Schedule Automatic Builds

In Jenkins job configuration:
1. Check **Build Triggers** → **Build periodically**
2. Add cron expression, e.g.:
   - `H 2 * * *` - Daily at 2 AM
   - `H */4 * * *` - Every 4 hours
   - `H H * * 1-5` - Once per day on weekdays

### Webhook Trigger from GitHub

1. In Jenkins job, check **GitHub hook trigger for GITScm polling**
2. In GitHub repository:
   - Go to **Settings** → **Webhooks** → **Add webhook**
   - Payload URL: `http://your-jenkins-url/github-webhook/`
   - Content type: `application/json`
   - Select events: **Just the push event**
   - Click **Add webhook**

---

## 🐛 Troubleshooting

### Issue: Python not found
**Solution**: Ensure Python is installed on Jenkins agent and path is correct

### Issue: Ollama not available
**Solution**: 
- Install Ollama on Jenkins agent
- Pull required models: `ollama pull llama3.2:3b`
- Or disable USE_AI parameter

### Issue: Permission denied on venv
**Solution**: Ensure Jenkins user has write permissions in workspace

### Issue: Reports not published
**Solution**: Check HTML Publisher Plugin is installed and reports directory exists

---

## 📞 Support

For issues or questions:
- Create an issue on GitHub
- Check Jenkins logs: `http://your-jenkins-url/job/API-AI-Tester-Pipeline/lastBuild/console`
- Review application logs in build artifacts

---

## ✅ Checklist

- [ ] Jenkins plugins installed
- [ ] GitHub credentials configured
- [ ] Pipeline job created with parameters
- [ ] Jenkinsfile added to repository
- [ ] run_pipeline.py script added
- [ ] Code pushed to GitHub main branch
- [ ] First build executed successfully
- [ ] Reports accessible
- [ ] (Optional) Email notifications configured
- [ ] (Optional) Scheduled builds configured
- [ ] (Optional) GitHub webhooks configured

---

**🎉 Your Jenkins CI/CD pipeline is now ready!**
