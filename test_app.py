#!/usr/bin/env python3
"""
Test script for LinkedIn Sales Automation Tool
"""

import sqlite3
import os
import sys

def test_database_creation():
    """Test database creation and schema"""
    print("🧪 Testing database creation...")

    try:
        # Import the init_db function from app.py
        sys.path.append('.')
        from app import init_db

        # Remove existing database for clean test
        if os.path.exists('linkedin_automation.db'):
            os.remove('linkedin_automation.db')

        # Initialize database
        init_db()

        # Check if database was created
        if os.path.exists('linkedin_automation.db'):
            print("✅ Database created successfully")

            # Check tables
            conn = sqlite3.connect('linkedin_automation.db')
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = ['campaigns', 'prospects', 'messages']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Table '{table}' created successfully")
                else:
                    print(f"❌ Table '{table}' not found")
                    return False

            conn.close()
            return True
        else:
            print("❌ Database not created")
            return False

    except ImportError as e:
        print(f"❌ Could not import from app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_gemini_api():
    """Test Gemini API connection"""
    print("\n🧪 Testing Gemini API connection...")

    try:
        import google.generativeai as genai

        # Configure API
        api_key = "AIzaSyCQOE7NN3n2oL_oR_ZjKjD7taTphphBYy4"
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Simple test
        response = model.generate_content("Hello, this is a test message. Please respond with 'API connection successful'.")

        if response and response.text:
            print("✅ Gemini API connection successful")
            print(f"📝 Response: {response.text[:100]}...")
            return True
        else:
            print("❌ No response from Gemini API")
            return False

    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def test_imports():
    """Test all required imports"""
    print("\n🧪 Testing imports...")

    required_modules = [
        'streamlit',
        'google.generativeai',
        'pandas',
        'sqlite3',
        'json',
        'datetime',
        're',
        'dataclasses',
        'typing'
    ]

    failed_imports = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError:
            print(f"❌ Failed to import {module}")
            failed_imports.append(module)

    return len(failed_imports) == 0

def main():
    """Run all tests"""
    print("🚀 LinkedIn Sales Automation Tool - Test Suite")
    print("=" * 60)

    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database_creation),
        ("Gemini API Test", test_gemini_api)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🏃 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Total: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 All tests passed! Your app is ready to run.")
        print("\n🚀 To start the app, run: streamlit run app.py")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
