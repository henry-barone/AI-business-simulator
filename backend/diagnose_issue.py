#!/usr/bin/env python3
"""
Comprehensive diagnostic script to identify and fix the company creation issue.
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_app_startup():
    """Test if the Flask app can start properly."""
    print("1. Testing Flask app startup...")
    try:
        from app import create_app
        app = create_app('development')
        print(f"   ✓ App created successfully")
        print(f"   ✓ CORS origins: {app.config.get('CORS_ORIGINS', 'Not set')}")
        print(f"   ✓ Debug mode: {app.config.get('DEBUG', False)}")
        return app
    except Exception as e:
        print(f"   ✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_database_connection(app):
    """Test database connection."""
    print("\n2. Testing database connection...")
    try:
        with app.app_context():
            from models import db
            from models.company import Company
            
            # Test database connection (SQLAlchemy 2.0 syntax)
            with db.engine.connect() as connection:
                connection.execute(db.text("SELECT 1"))
            print("   ✓ Database connection successful")
            
            # Test Company model
            company_count = Company.query.count()
            print(f"   ✓ Company model accessible, {company_count} companies in database")
            return True
    except Exception as e:
        print(f"   ⚠ Database connection issue: {e}")
        print("   Note: This might be expected if database is not set up")
        return False

def test_routes_registration(app):
    """Test if routes are registered properly."""
    print("\n3. Testing route registration...")
    try:
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(f"{rule.methods} {rule.rule}")
            
            print(f"   ✓ Total routes registered: {len(routes)}")
            
            # Check for specific routes
            company_routes = [r for r in routes if '/companies' in r]
            print(f"   ✓ Company routes found: {len(company_routes)}")
            for route in company_routes[:3]:  # Show first 3
                print(f"      - {route}")
            
            health_routes = [r for r in routes if '/health' in r]
            print(f"   ✓ Health routes found: {len(health_routes)}")
            
            return True
    except Exception as e:
        print(f"   ✗ Route registration test failed: {e}")
        return False

def test_companies_route_import():
    """Test if companies route imports correctly."""
    print("\n4. Testing companies route import...")
    try:
        from routes.companies import companies_bp, ENHANCED_FEATURES
        print("   ✓ Companies blueprint imports successfully")
        print(f"   ✓ Enhanced features available: {ENHANCED_FEATURES}")
        
        # Test create_company function
        from routes.companies import create_company
        print("   ✓ create_company function accessible")
        return True
    except Exception as e:
        print(f"   ✗ Companies route import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_request_simulation(app):
    """Simulate a manual request to the companies endpoint."""
    print("\n5. Testing manual request simulation...")
    try:
        with app.test_client() as client:
            # Test health endpoint first
            health_response = client.get('/health')
            print(f"   Health endpoint: {health_response.status_code}")
            if health_response.status_code == 200:
                print(f"   Health response: {health_response.get_json()}")
            
            # Test company creation
            company_data = {
                "name": "Test Company",
                "industry": "Manufacturing"
            }
            
            response = client.post('/api/companies',
                                 data=json.dumps(company_data),
                                 content_type='application/json')
            
            print(f"   Company creation status: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"   ✓ Company creation successful: {response.get_json()}")
                return True
            else:
                print(f"   ✗ Company creation failed: {response.get_data(as_text=True)}")
                return False
                
    except Exception as e:
        print(f"   ✗ Manual request simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_external_request():
    """Test external HTTP request to the running server."""
    print("\n6. Testing external HTTP request...")
    try:
        # Test health endpoint
        health_url = "http://localhost:5000/health"
        response = requests.get(health_url, timeout=5)
        print(f"   Health check: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✓ Health response: {response.json()}")
            
            # Test company creation
            company_url = "http://localhost:5000/api/companies"
            company_data = {
                "name": "External Test Company",
                "industry": "Manufacturing"
            }
            
            response = requests.post(company_url,
                                   json=company_data,
                                   headers={"Content-Type": "application/json"},
                                   timeout=5)
            
            print(f"   Company creation: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"   ✓ External request successful: {response.json()}")
                return True
            else:
                print(f"   ✗ External request failed: {response.text}")
                print(f"   Response headers: {dict(response.headers)}")
                return False
        else:
            print(f"   ✗ Health check failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ⚠ Server not running on localhost:5000")
        print("   Start the server with: python app.py")
        return False
    except Exception as e:
        print(f"   ✗ External request failed: {e}")
        return False

def diagnose_common_issues():
    """Diagnose common configuration issues."""
    print("\n7. Diagnosing common issues...")
    
    # Check environment variables
    print("   Environment variables:")
    important_vars = ['FLASK_ENV', 'DATABASE_URL', 'SECRET_KEY', 'CORS_ORIGINS']
    for var in important_vars:
        value = os.environ.get(var, 'Not set')
        if var == 'SECRET_KEY' and value != 'Not set':
            value = '***hidden***'
        print(f"      {var}: {value}")
    
    # Check if .env file exists
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"   ✓ .env file exists")
    else:
        print(f"   ⚠ .env file not found (this might be OK)")
    
    # Check uploads directory
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        print(f"   ✓ uploads directory exists")
    else:
        print(f"   ⚠ uploads directory missing - creating it")
        os.makedirs(uploads_dir, exist_ok=True)

def main():
    """Run comprehensive diagnostics."""
    print("Backend Issue Diagnostic Tool")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Run all tests
    app = test_app_startup()
    if not app:
        print("\n❌ Cannot proceed - Flask app creation failed")
        return
    
    db_ok = test_database_connection(app)
    routes_ok = test_routes_registration(app)
    import_ok = test_companies_route_import()
    manual_ok = test_manual_request_simulation(app)
    external_ok = test_external_request()
    
    diagnose_common_issues()
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY:")
    print("=" * 50)
    
    tests = [
        ("Flask app startup", app is not None),
        ("Database connection", db_ok),
        ("Route registration", routes_ok),
        ("Companies route import", import_ok),
        ("Manual request test", manual_ok),
        ("External request test", external_ok)
    ]
    
    for test_name, result in tests:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<25}: {status}")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    if not external_ok and manual_ok:
        print("- Server configuration issue. Check CORS settings and port binding.")
        print("- Make sure server is running with: python app.py")
    elif not manual_ok:
        print("- Backend logic issue. Check route handlers and database setup.")
    elif not import_ok:
        print("- Route import issue. Check for syntax errors in routes/companies.py")
    elif all(result for _, result in tests):
        print("- All tests passed! The issue might be frontend-related.")
        print("- Check browser console for CORS or network errors.")
        print("- Verify frontend is making requests to correct URL (localhost:5000)")
    
    print("\nTo test manually:")
    print("curl -X POST http://localhost:5000/api/companies \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"name\": \"Test Company\", \"industry\": \"Manufacturing\"}'")

if __name__ == "__main__":
    main()