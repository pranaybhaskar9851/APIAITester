# API AI Tester V7 - Architecture Documentation

## Overview

API AI Tester V7 is an intelligent API testing framework that automatically generates and executes comprehensive test cases for REST APIs based on OpenAPI/Swagger specifications. It supports both traditional rule-based test generation and AI-powered test generation using local LLM models (Ollama).

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Interface (FastAPI)                  │
│                            app.py                                │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ├─────────┐         ┌──────────┐        ┌─────────┐
                │         │         │          │        │         │
                ▼         ▼         ▼          ▼        ▼         │
        ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
        │ Swagger  │ │Generator │ │   LLM    │ │ Executor │     │
        │  Loader  │ │  Engine  │ │Generator │ │  Engine  │     │
        └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
                                                      │            │
                                                      ▼            │
                                              ┌──────────┐        │
                                              │  Report  │        │
                                              │ Generator│        │
                                              └──────────┘        │
                                                      │            │
                                                      ▼            │
                                    ┌────────────────────────┐    │
                                    │  Artifacts & Reports   │◄───┘
                                    │  - JSON Files          │
                                    │  - HTML Reports        │
                                    │  - JUnit XML           │
                                    └────────────────────────┘
```

---

## Core Components

### 1. **Web Interface (`app.py`)**

**Purpose**: Provides the user interface and orchestrates the entire testing workflow.

**Key Features**:
- FastAPI-based web interface
- Form-based input for configuration
- Supports multiple test generation modes:
  - Traditional Swagger-based generation
  - AI-powered generation using Ollama
  - Reuse of previously generated tests
- Session management for login-based authentication

**Endpoints**:
- `GET /` - Home page with configuration form
- `POST /run` - Executes test generation and execution workflow

**Configuration Parameters**:
- Base URL
- Swagger/OpenAPI specification URL
- Login credentials (volume, username, password)
- API token (alternative to login)
- Test generation method (Swagger vs LLM)
- Test reuse option

---

### 2. **Swagger Loader (`engine/swagger.py`)**

**Purpose**: Fetches and parses OpenAPI/Swagger specifications.

**Functionality**:
```python
def load_swagger(swagger_input: str) -> dict
```
- Downloads Swagger JSON from provided URL
- Parses and validates the specification
- Returns structured dictionary for test generation

---

### 3. **Test Generators**

#### 3.1 **Traditional Generator (`engine/generator.py`)**

**Purpose**: Rule-based test case generation from Swagger spec.

**Key Features**:
- Iterates through all API endpoints and HTTP methods
- Generates two test cases per endpoint:
  - **Positive test**: Valid authentication, expects 200
  - **Unauthorized test**: Invalid authentication, expects 401
- Extracts and processes:
  - Path parameters (replaces with default values like "1")
  - Query parameters (uses defaults or type-appropriate values)
  - Required headers (`accept`, `Content-Type`, `Locale`)
- Excludes login endpoints from test generation

**Test Case Structure**:
```json
{
  "id": "uuid",
  "test_name": "GET /endpoint Description",
  "method": "GET|POST|PUT|DELETE|PATCH",
  "endpoint": "/path/to/endpoint?param=value",
  "expected_status": 200,
  "auth": "valid|invalid",
  "headers": {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Locale": "en_US"
  }
}
```

#### 3.2 **LLM Generator (`engine/llm_generator.py`)**

**Purpose**: AI-powered intelligent test generation using local Ollama models.

**Key Features**:
- Uses local LLM (Llama, Mistral, CodeLlama, etc.)
- Analyzes Swagger spec contextually
- Generates more intelligent and comprehensive tests
- Automatic fallback to traditional generation on failure

**Workflow**:
1. Prepares Swagger spec for LLM context (limits size if needed)
2. Constructs detailed prompt with instructions
3. Calls Ollama API with specified model
4. Parses and validates LLM-generated JSON
5. Falls back to traditional generator if parsing fails

**Advantages**:
- Better understanding of API semantics
- More realistic test data
- Can identify edge cases
- Adapts to API patterns

---

### 4. **Test Executor (`engine/executor.py`)**

**Purpose**: Executes test cases against the target API and collects results.

**Execution Flow**:

```
1. Initialize session and create artifact directory
2. If login configured:
   ├─ Execute login request (POST with form data)
   ├─ Extract authToken from response
   ├─ Save login request/response for debugging
   └─ Wait 0.5s for token activation
3. For each test case:
   ├─ Prepare headers (add AuthToken, Locale, accept)
   ├─ Execute HTTP request
   ├─ Capture response (status, headers, body)
   ├─ Save request/response to JSON files
   ├─ Compare actual vs expected status
   └─ Record test result (pass/fail)
4. Return aggregated results
```

**Authentication Handling**:
- Supports form-based login with custom headers:
  - `Content-Type: application/x-www-form-urlencoded`
  - `TargetVolume: <volume_name>`
  - `Locale: en_US`
- Extracts authToken from multiple response formats
- Applies token to all subsequent requests
- Handles both valid and invalid authentication scenarios

**Smart URL Construction**:
- Prevents duplicate path segments
- Handles various login endpoint formats
- Normalizes base URLs and endpoints

---

### 5. **Report Generator (`engine/report.py`)**

**Purpose**: Generates human-readable and machine-readable test reports.

**Output Formats**:

#### 5.1 **HTML Report**
- Visual test results table
- Shows test name, expected/actual status, pass/fail
- Includes URL and error information
- Saved as `reports/report_<timestamp>.html`

#### 5.2 **JUnit XML Report**
- Standard JUnit format for CI/CD integration
- Compatible with Jenkins, GitLab CI, etc.
- Includes test execution time and status
- Saved as `reports/junit_<timestamp>.xml`

---

## Data Flow

### Test Generation and Execution Flow

```
User Input (Web Form)
    ↓
[Load Swagger Spec]
    ↓
Decision: Reuse Tests?
    ├─ Yes → [Load test_cases.json]
    │
    └─ No → Decision: Use LLM?
             ├─ Yes → [LLM Generator] → [Validate & Save]
             └─ No  → [Swagger Generator] → [Save]
                ↓
        [Execute Login] (if configured)
                ↓
        [Extract AuthToken]
                ↓
        [Execute Test Cases]
                ↓
        [Save Artifacts]
          ├─ Request/Response JSON pairs
          └─ Login request/response
                ↓
        [Generate Reports]
          ├─ HTML Report
          └─ JUnit XML
                ↓
        [Display Results]
```

---

## File Structure

```
api-ai-tester-v7/
│
├── app.py                      # Main FastAPI application
├── requirements.txt            # Python dependencies
├── test_cases.json            # Saved test cases (auto-generated)
│
├── engine/                    # Core logic modules
│   ├── swagger.py            # Swagger spec loader
│   ├── generator.py          # Traditional test generator
│   ├── llm_generator.py      # AI-powered test generator
│   ├── executor.py           # Test execution engine
│   └── report.py             # Report generation
│
├── artifacts/                # Test execution artifacts
│   └── <timestamp>/         # Per-execution directory
│       ├── login_request.json
│       ├── login_response.json
│       ├── <uuid>_request.json
│       └── <uuid>_response.json
│
└── reports/                  # Generated reports
    ├── report_<timestamp>.html
    └── junit_<timestamp>.xml
```

---

## Key Features

### 1. **Dual Test Generation Modes**

| Feature | Swagger-Based | LLM-Based |
|---------|--------------|-----------|
| Speed | Fast | Slower (LLM inference) |
| Intelligence | Rule-based | Context-aware |
| Accuracy | High for standard APIs | High for complex APIs |
| Offline | Yes | Yes (local LLM) |
| Customization | Limited | Extensive |

### 2. **Authentication Workflows**

**Login-Based Authentication**:
```
1. Execute login endpoint with credentials
2. Extract authToken from response
3. Apply token to all test requests
4. Save login artifacts for debugging
```

**Token-Based Authentication**:
```
1. User provides pre-generated token
2. Token applied directly to all requests
3. No login execution needed
```

### 3. **Test Reusability**

- Test cases saved to `test_cases.json`
- Can rerun tests without regenerating
- Useful for:
  - Regression testing
  - Performance testing
  - Consistent test execution
  - Offline testing

### 4. **Comprehensive Artifacts**

Each test execution creates:
- Timestamped directory
- Request/response pairs (JSON)
- Login transaction details
- Complete traceability

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Web Framework | FastAPI |
| HTTP Client | Requests |
| Templating | Jinja2 |
| LLM Integration | Ollama (local) |
| Reports | HTML, JUnit XML |
| Authentication | Form-based, Token-based |

---

## Configuration

### Environment Requirements

**Required**:
- Python 3.8+
- FastAPI
- Requests library

**Optional**:
- Ollama (for LLM-based generation)
- Supported models: llama3.2, mistral, codellama, etc.

### API Requirements

The target API should:
- Provide OpenAPI/Swagger specification
- Support standard HTTP methods
- Use consistent authentication (AuthToken header)
- Return JSON responses

---

## Security Considerations

1. **Credentials**: Passwords are not logged or saved to artifacts
2. **Tokens**: AuthTokens are saved to artifacts for debugging (secure storage recommended)
3. **Network**: All communication over HTTP/HTTPS as configured
4. **Local Execution**: LLM models run locally (no data sent externally)

---

## Extensibility

### Adding New Test Generators

Create a new generator module:
```python
def custom_generate_tests(swagger: dict, **kwargs) -> list:
    # Your custom logic
    return test_cases
```

### Custom Headers

Modify `executor.py` to add API-specific headers:
```python
headers["CustomHeader"] = "CustomValue"
```

### Report Formats

Add new report generators in `engine/report.py`:
```python
def generate_custom_report(results, run_id):
    # Generate custom format
    pass
```

---

## Performance Considerations

1. **Test Execution**: Sequential (can be parallelized)
2. **LLM Generation**: Depends on model size and hardware
3. **Artifact Storage**: Grows with test count
4. **Network Latency**: Depends on target API

**Optimization Tips**:
- Use smaller LLM models for faster generation
- Implement parallel test execution
- Archive old artifacts periodically
- Use test reuse for repeated runs

---

## Future Enhancements

1. **Parallel Execution**: Run tests concurrently
2. **Data-Driven Tests**: Support test data files
3. **Mock Support**: Integrate API mocking
4. **Advanced Assertions**: Custom validation rules
5. **CI/CD Integration**: GitHub Actions, Jenkins plugins
6. **Database Testing**: Support for database-backed APIs
7. **Performance Testing**: Load testing capabilities
8. **API Versioning**: Multi-version testing

---

## Troubleshooting

### Common Issues

**1. Authentication Failures**
- Verify login credentials
- Check AuthToken format in response
- Ensure token extraction logic matches API response structure

**2. LLM Generation Fails**
- Ensure Ollama is running: `ollama list`
- Check model is pulled: `ollama pull llama3.2`
- System falls back to traditional generation automatically

**3. Missing Dependencies**
- Run: `pip install -r requirements.txt`
- For Ollama: `pip install ollama`

**4. Path Issues**
- Add Ollama to PATH (Windows):
  ```powershell
  [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\<user>\AppData\Local\Programs\Ollama", [EnvironmentVariableTarget]::User)
  ```

---

## Conclusion

API AI Tester V7 provides a comprehensive, intelligent, and extensible framework for automated API testing. By combining traditional rule-based generation with AI-powered intelligence, it offers flexibility for testing APIs of varying complexity while maintaining reliability and performance.
