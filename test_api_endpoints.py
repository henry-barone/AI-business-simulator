#!/usr/bin/env python3
"""
Test Enhanced Simulation API Endpoints
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import requests
import json
from flask import Flask
from backend.app import create_app

def test_enhanced_simulation_api():
    """Test the enhanced simulation API endpoints."""
    
    print("🧪 Testing Enhanced Simulation API Endpoints")
    print("=" * 50)
    
    try:
        # Create test app
        app = create_app('development')
        
        with app.test_client() as client:
            # Test data
            test_company_data = {
                "name": "Test Manufacturing Co",
                "industry": "Manufacturing"
            }
            
            print("\n📝 Step 1: Creating test company...")
            company_response = client.post('/api/companies', 
                                         json=test_company_data,
                                         content_type='application/json')
            
            if company_response.status_code == 201:
                company_data = company_response.get_json()
                company_id = company_data['company']['id']
                print(f"✅ Company created with ID: {company_id}")
            else:
                print(f"❌ Failed to create company: {company_response.status_code}")
                return False
            
            # Create test P&L data
            test_pl_data = {
                "revenue": 5000000,
                "cogs": 3000000,
                "labor_costs": 1200000,
                "overhead_costs": 500000,
                "net_income": 300000
            }
            
            print("\n📊 Step 2: Creating test P&L data...")
            pl_response = client.post(f'/api/companies/{company_id}/pl-statement',
                                    json=test_pl_data,
                                    content_type='application/json')
            
            if pl_response.status_code == 201:
                print("✅ P&L data created successfully")
            else:
                print(f"❌ Failed to create P&L data: {pl_response.status_code}")
                return False
            
            # Test enhanced simulation creation
            simulation_data = {
                "automation_levels": {
                    "labor": 0.5,
                    "quality": 0.6,
                    "inventory": 0.4,
                    "service": 0.3
                },
                "projection_months": 12,
                "production_volume": "1000-10000 units/day",
                "employee_count": "51-200",
                "automation_level": "Some automated tools"
            }
            
            print("\n🏭 Step 3: Testing enhanced simulation creation...")
            sim_response = client.post(f'/api/companies/{company_id}/enhanced-simulation',
                                     json=simulation_data,
                                     content_type='application/json')
            
            if sim_response.status_code == 201:
                sim_data = sim_response.get_json()
                simulation_id = sim_data['simulation_id']
                print(f"✅ Enhanced simulation created with ID: {simulation_id}")
                
                # Check response structure
                if 'data' in sim_data:
                    data = sim_data['data']
                    print(f"📈 Total Annual Savings: ${data['summary']['total_annual_savings']:,.2f}")
                    print(f"💰 Total Implementation Cost: ${data['summary']['total_implementation_cost']:,.2f}")
                    print(f"📊 Number of Projections: {len(data['projections'])}")
                    
                    # Test getting the simulation
                    print("\n🔍 Step 4: Testing simulation retrieval...")
                    get_response = client.get(f'/api/companies/{company_id}/enhanced-simulation')
                    
                    if get_response.status_code == 200:
                        print("✅ Simulation retrieved successfully")
                    else:
                        print(f"❌ Failed to retrieve simulation: {get_response.status_code}")
                        return False
                    
                    # Test real-time adjustments
                    print("\n⚡ Step 5: Testing real-time adjustments...")
                    adjustment_data = {
                        "labor_automation": 60,
                        "quality_automation": 70,
                        "inventory_automation": 50,
                        "service_automation": 40
                    }
                    
                    adjust_response = client.post(f'/api/enhanced-simulations/{simulation_id}/adjust',
                                                json=adjustment_data,
                                                content_type='application/json')
                    
                    if adjust_response.status_code == 200:
                        adjust_data = adjust_response.get_json()
                        print("✅ Real-time adjustments working")
                        if 'results' in adjust_data:
                            results = adjust_data['results']
                            print(f"📊 Total Annual Savings: ${results['summary']['total_annual_savings']:,.2f}")
                            print(f"💰 Break-even Month: {results['summary']['break_even_month']}")
                    else:
                        print(f"❌ Failed to adjust simulation: {adjust_response.status_code}")
                        return False
                    
                else:
                    print("❌ Missing data in simulation response")
                    return False
                    
            else:
                print(f"❌ Failed to create enhanced simulation: {sim_response.status_code}")
                print(f"Response: {sim_response.get_json()}")
                return False
            
            print("\n" + "=" * 50)
            print("✅ All Enhanced Simulation API Tests Passed!")
            return True
            
    except Exception as e:
        print(f"\n❌ API Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_simulation_api()
    if success:
        print("\n🎉 Enhanced Simulation API is ready for integration!")
    else:
        print("\n💥 API tests failed - check configuration")