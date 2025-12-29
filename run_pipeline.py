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
