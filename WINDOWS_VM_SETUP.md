# Windows VM Setup Guide for Jenkins Agent

This guide provides step-by-step instructions to set up your Windows VM with Python, Ollama, LLMs, and Jenkins Agent for the API AI Tester project.

---

## 📋 Overview

Your Windows VM will serve as a dedicated Jenkins agent that:
- ✅ Has Python pre-installed
- ✅ Has Ollama pre-installed with LLM models
- ✅ Runs Jenkins agent to execute pipelines
- ✅ Is labeled as `api-tester-vm` in Jenkins

---

## 🖥️ Part 1: Windows VM Initial Setup

### System Requirements
- **OS**: Windows 10/11 or Windows Server 2019+
- **RAM**: 16 GB minimum (recommended for LLM models)
- **Disk**: 50 GB free space minimum
- **Network**: Internet access for downloading dependencies

---

## 🐍 Part 2: Install Python on Windows VM

### Step 1: Download Python
1. Open browser and go to: https://www.python.org/downloads/
2. Download **Python 3.11** or **Python 3.12** (recommended)

### Step 2: Install Python
1. Run the installer
2. ⚠️ **IMPORTANT**: Check ✅ **"Add Python to PATH"**
3. Click **"Install Now"**
4. Wait for installation to complete

### Step 3: Verify Python Installation
Open PowerShell and run:
```powershell
python --version
# Should show: Python 3.11.x or 3.12.x

pip --version
# Should show: pip 24.x.x
```

### Step 4: Upgrade pip
```powershell
python -m pip install --upgrade pip
```

---

## 🤖 Part 3: Install Ollama on Windows VM

### Step 1: Download Ollama
1. Open browser and go to: https://ollama.com/download
2. Click **"Download for Windows"**
3. Download the `.exe` installer

### Step 2: Install Ollama
1. Run the downloaded installer
2. Follow the installation wizard
3. Ollama will start automatically as a Windows service

### Step 3: Verify Ollama Installation
Open PowerShell and run:
```powershell
ollama --version
# Should show: ollama version is 0.x.x
```

### Step 4: Pull Required LLM Models
This may take 30-60 minutes depending on your internet speed:

```powershell
# Pull all models used in the pipeline
ollama pull llama3.2:3b
ollama pull llama3.2:1b
ollama pull qwen2.5:3b
ollama pull qwen2.5:1.5b
ollama pull phi3:mini
ollama pull phi4:latest

# Verify models are downloaded
ollama list
```

Expected output:
```
NAME                    ID              SIZE    MODIFIED
llama3.2:3b            a80c4f17acd5    2.0 GB  2 hours ago
llama3.2:1b            baf6a787fdff    1.3 GB  2 hours ago
qwen2.5:3b             f6daf2b25194    1.9 GB  2 hours ago
qwen2.5:1.5b           6b9ac0bb6b91    1.0 GB  2 hours ago
phi3:mini              64c1188f2485    2.3 GB  2 hours ago
phi4:latest            0fe66f6a2e25    4.7 GB  2 hours ago
```

### Step 5: Test Ollama
```powershell
# Quick test
ollama run llama3.2:3b "Hello, are you working?"
```

If you get a response, Ollama is working correctly!

---

## 🔧 Part 4: Install Git on Windows VM (Optional but Recommended)

### Step 1: Download Git
1. Go to: https://git-scm.com/download/win
2. Download the 64-bit installer

### Step 2: Install Git
1. Run the installer
2. Use default settings
3. Complete installation

### Step 3: Verify Git
```powershell
git --version
# Should show: git version 2.x.x
```

---

## 🤵 Part 5: Set Up Jenkins Agent on Windows VM

### Method A: Jenkins Agent via Java (Recommended)

#### Step 1: Install Java JDK
1. Download from: https://adoptium.net/
2. Download **Eclipse Temurin JDK 17** (LTS)
3. Install with default settings
4. Verify:
```powershell
java -version
# Should show: openjdk version "17.x.x"
```

#### Step 2: Create Jenkins Agent in Jenkins Master

1. **On Jenkins Master**, go to:
   - **Manage Jenkins** → **Nodes** → **New Node**

2. **Configure Node**:
   - **Node name**: `api-tester-vm` (important!)
   - **Type**: ✅ Permanent Agent
   - Click **Create**

3. **Node Configuration**:
   - **Name**: `api-tester-vm`
   - **Description**: `Windows VM with Python, Ollama, and LLMs for API testing`
   - **Number of executors**: `2` (or more based on VM CPU)
   - **Remote root directory**: `C:\Jenkins`
   - **Labels**: `api-tester-vm windows python ollama ai-ready`
   - **Usage**: "Use this node as much as possible"
   - **Launch method**: 
     - Select **"Launch agent by connecting it to the controller"**
     - OR **"Launch agent via execution of command on the controller"**
   - **Availability**: "Keep this agent online as much as possible"

4. Click **Save**

#### Step 3: Download Agent JAR on Windows VM

1. After saving the node, you'll see agent connection instructions
2. Copy the agent secret shown
3. On Windows VM, create directory:
```powershell
New-Item -ItemType Directory -Path "C:\Jenkins" -Force
cd C:\Jenkins
```

4. Download agent.jar (URL will be shown in Jenkins):
```powershell
# Replace <JENKINS_URL> with your Jenkins server URL
Invoke-WebRequest -Uri "http://<JENKINS_URL>/jnlpJars/agent.jar" -OutFile "agent.jar"
```

#### Step 4: Create Agent Startup Script

Create file: `C:\Jenkins\start-agent.ps1`
```powershell
# start-agent.ps1
# Replace these values with your actual Jenkins URL and secret
$jenkinsUrl = "http://your-jenkins-server:8080"
$agentName = "api-tester-vm"
$agentSecret = "your-agent-secret-here"

# Start the Jenkins agent
java -jar C:\Jenkins\agent.jar `
    -url $jenkinsUrl `
    -name $agentName `
    -secret $agentSecret `
    -workDir "C:\Jenkins"
```

#### Step 5: Run Agent Manually (Test)
```powershell
cd C:\Jenkins
powershell -File start-agent.ps1
```

You should see: "INFO: Connected"

#### Step 6: Set Up Agent as Windows Service (Auto-start)

1. Download NSSM (Non-Sucking Service Manager):
   - https://nssm.cc/download
   - Extract to `C:\Jenkins\nssm`

2. Install as service:
```powershell
# Run PowerShell as Administrator
cd C:\Jenkins\nssm\win64

.\nssm.exe install JenkinsAgent
```

3. In NSSM GUI:
   - **Path**: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
   - **Startup directory**: `C:\Jenkins`
   - **Arguments**: `-ExecutionPolicy Bypass -File C:\Jenkins\start-agent.ps1`
   - Click **Install service**

4. Start the service:
```powershell
Start-Service JenkinsAgent
```

5. Verify service is running:
```powershell
Get-Service JenkinsAgent
# Status should be: Running
```

6. Set service to start automatically:
```powershell
Set-Service -Name JenkinsAgent -StartupType Automatic
```

### Method B: Jenkins Agent via SSH (Alternative)

If you prefer SSH connection:
1. Install OpenSSH Server on Windows VM
2. Configure SSH agent in Jenkins
3. Add SSH credentials in Jenkins

---

## ✅ Part 6: Verify Complete Setup

### Step 1: Check Agent Connection in Jenkins
1. Go to **Jenkins** → **Nodes**
2. You should see `api-tester-vm` with a green checkmark ✅
3. Click on the node
4. Check **Log** - should show "Agent successfully connected"

### Step 2: Test Environment on Agent

In Jenkins, create a test pipeline:

```groovy
pipeline {
    agent { label 'api-tester-vm' }
    
    stages {
        stage('Test Environment') {
            steps {
                bat '''
                    echo "=== Testing Python ==="
                    python --version
                    pip --version
                    
                    echo "=== Testing Ollama ==="
                    ollama --version
                    ollama list
                    
                    echo "=== Testing Git ==="
                    git --version
                    
                    echo "=== Testing Java ==="
                    java -version
                    
                    echo "=== System Info ==="
                    systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
                '''
            }
        }
    }
}
```

Run this pipeline - all commands should execute successfully!

---

## 🎯 Part 7: Run Your API AI Tester Pipeline

### Step 1: Verify Node Label
The Jenkinsfile is configured to use: `agent { label 'api-tester-vm' }`

Ensure your agent has this label:
- Go to **Jenkins** → **Nodes** → **api-tester-vm** → **Configure**
- Check **Labels** field contains: `api-tester-vm`
- Save if you made changes

### Step 2: Run the Pipeline
1. Go to your pipeline job: **API-AI-Tester-Pipeline**
2. Click **Build with Parameters**
3. Fill in parameters
4. Click **Build**

The pipeline will now execute on your Windows VM! 🎉

---

## 🔍 Troubleshooting

### Issue: Agent not connecting
**Solution**:
```powershell
# Check if Jenkins service is running
Get-Service JenkinsAgent

# Restart service
Restart-Service JenkinsAgent

# Check logs
Get-Content C:\Jenkins\agent.log -Tail 50
```

### Issue: "Python not found" in pipeline
**Solution**:
```powershell
# Verify PATH includes Python
$env:Path -split ';' | Select-String Python

# If not found, add Python to system PATH:
# System Properties → Environment Variables → System Variables → Path → Edit
# Add: C:\Users\<username>\AppData\Local\Programs\Python\Python311\
# Add: C:\Users\<username>\AppData\Local\Programs\Python\Python311\Scripts\
```

### Issue: "Ollama not found" in pipeline
**Solution**:
```powershell
# Check if Ollama service is running
Get-Service Ollama

# If not running, start it
Start-Service Ollama

# Or restart Ollama
Restart-Service Ollama
```

### Issue: Pipeline stuck/hanging
**Solution**:
- Check VM resources (CPU, RAM, Disk)
- LLM models require significant RAM (8GB+ for larger models)
- Consider using smaller models if VM has limited resources

### Issue: "Permission denied" errors
**Solution**:
```powershell
# Run PowerShell as Administrator
# Give Jenkins agent user full control of C:\Jenkins
icacls "C:\Jenkins" /grant "SYSTEM:(OI)(CI)F" /T
```

---

## 📊 Monitoring & Maintenance

### Check Agent Status
```powershell
# Service status
Get-Service JenkinsAgent

# View logs
Get-Content C:\Jenkins\agent.log -Tail 100

# Check Ollama
ollama ps

# Check running processes
Get-Process | Where-Object {$_.ProcessName -like "*java*" -or $_.ProcessName -like "*ollama*"}
```

### Update LLM Models
```powershell
# Pull latest versions
ollama pull llama3.2:3b
ollama pull qwen2.5:3b
ollama pull phi4:latest

# Remove old unused models
ollama rm <model-name>
```

### Disk Space Management
```powershell
# Check disk space
Get-PSDrive C

# Ollama models location: C:\Users\<username>\.ollama\models
# Jenkins workspace: C:\Jenkins\workspace
# Clean old workspaces if needed
```

---

## 🔒 Security Best Practices

1. **Firewall**: Ensure only Jenkins master can connect to the agent
2. **User Account**: Run Jenkins agent with a dedicated service account
3. **Updates**: Keep Python, Ollama, and Java updated
4. **Antivirus**: Exclude `C:\Jenkins` and Ollama directories from real-time scanning
5. **Network**: Use VPN or private network between Jenkins master and agent

---

## 📞 Quick Reference

### Important Paths
- **Jenkins Agent**: `C:\Jenkins`
- **Agent JAR**: `C:\Jenkins\agent.jar`
- **Agent Logs**: `C:\Jenkins\agent.log`
- **Ollama Models**: `C:\Users\<username>\.ollama\models`
- **Python**: `C:\Users\<username>\AppData\Local\Programs\Python\Python311`

### Important Commands
```powershell
# Restart Jenkins Agent
Restart-Service JenkinsAgent

# Restart Ollama
Restart-Service Ollama

# Test Python
python --version

# Test Ollama
ollama list

# View Agent Status
Get-Service JenkinsAgent
```

---

## ✅ Setup Checklist

- [ ] Windows VM created with adequate resources
- [ ] Python 3.11+ installed with PATH configured
- [ ] pip upgraded to latest version
- [ ] Ollama installed and running
- [ ] All 6 LLM models downloaded
- [ ] Git installed (optional)
- [ ] Java JDK 17 installed
- [ ] Jenkins node created with label `api-tester-vm`
- [ ] Jenkins agent downloaded and configured
- [ ] Jenkins agent running as Windows service
- [ ] Agent shows as online in Jenkins
- [ ] Test pipeline executed successfully
- [ ] API AI Tester pipeline runs on the VM

---

**🎉 Your Windows VM is now fully configured as a Jenkins agent for API AI Tester!**

The pipeline will automatically execute on this VM whenever you trigger a build.
