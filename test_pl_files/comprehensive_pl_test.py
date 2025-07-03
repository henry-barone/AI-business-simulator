#!/usr/bin/env python3
"""
Comprehensive test script for PLAnalyzer class.
Tests parsing functionality, edge cases, and validation.
"""

import sys
import os
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.pl_analyzer import PLAnalyzer

class PLAnalyzerTester:
    def __init__(self):
        self.analyzer = PLAnalyzer()
        self.test_results = []
        self.test_files_dir = Path(__file__).parent
        
    def create_test_csv_files(self):
        """Create various test CSV files for comprehensive testing."""
        
        # Test 1: Simple P&L with standard keywords
        simple_pl = pd.DataFrame({
            'Item': ['Revenue', 'Cost of Goods Sold', 'Labor Costs', 'Overhead Expenses'],
            'Amount': [100000, 60000, 25000, 10000]
        })
        simple_pl.to_csv(self.test_files_dir / 'test_simple_pl.csv', index=False)
        
        # Test 2: P&L with alternative keywords
        alt_keywords_pl = pd.DataFrame({
            'Description': ['Sales Revenue', 'COGS', 'Payroll', 'Administrative Expenses'],
            'Value': [150000, 75000, 30000, 15000]
        })
        alt_keywords_pl.to_csv(self.test_files_dir / 'test_alt_keywords.csv', index=False)
        
        # Test 3: P&L with different number formats
        number_formats_pl = pd.DataFrame({
            'Line Item': ['Total Revenue', 'Cost of Sales', 'Wages', 'Rent'],
            'Amount': ['$250,000.00', '(125,000)', '$45,000.50', '8000']
        })
        number_formats_pl.to_csv(self.test_files_dir / 'test_number_formats.csv', index=False)
        
        # Test 4: P&L with multiple revenue sources
        multi_revenue_pl = pd.DataFrame({
            'Account': ['Product Sales', 'Service Revenue', 'COGS - Products', 'COGS - Services', 'Salaries', 'Utilities'],
            'Amount': [80000, 70000, 45000, 35000, 40000, 5000]
        })
        multi_revenue_pl.to_csv(self.test_files_dir / 'test_multi_revenue.csv', index=False)
        
        # Test 5: P&L with mixed case and spaces
        mixed_case_pl = pd.DataFrame({
            'DESCRIPTION': ['GROSS RECEIPTS', 'cost of goods sold', 'Employee Compensation', 'General & Administrative'],
            'TOTAL': [200000, 120000, 50000, 20000]
        })
        mixed_case_pl.to_csv(self.test_files_dir / 'test_mixed_case.csv', index=False)
        
        # Test 6: Empty file
        empty_df = pd.DataFrame()
        empty_df.to_csv(self.test_files_dir / 'test_empty.csv', index=False)
        
        # Test 7: File with no financial data
        non_financial_df = pd.DataFrame({
            'Name': ['John', 'Jane', 'Bob'],
            'Age': [25, 30, 35],
            'City': ['NYC', 'LA', 'Chicago']
        })
        non_financial_df.to_csv(self.test_files_dir / 'test_non_financial.csv', index=False)
        
        # Test 8: P&L with negative numbers and parentheses
        negative_numbers_pl = pd.DataFrame({
            'Item': ['Income', 'Direct Costs', 'Labor', 'Operating Expenses'],
            'Q1': [500000, -300000, -100000, -50000],
            'Q2': ['600,000', '(350,000)', '(110,000)', '(55,000)']
        })
        negative_numbers_pl.to_csv(self.test_files_dir / 'test_negative_numbers.csv', index=False)
        
        # Test 9: P&L with costs exceeding revenue (validation test)
        high_costs_pl = pd.DataFrame({
            'Item': ['Revenue', 'Cost of Goods Sold', 'Labor Costs', 'Overhead'],
            'Amount': [50000, 60000, 40000, 30000]
        })
        high_costs_pl.to_csv(self.test_files_dir / 'test_high_costs.csv', index=False)
        
        # Test 10: P&L with zero revenue (validation test)
        zero_revenue_pl = pd.DataFrame({
            'Item': ['Sales', 'Cost of Goods Sold', 'Labor Costs'],
            'Amount': [0, 10000, 5000]
        })
        zero_revenue_pl.to_csv(self.test_files_dir / 'test_zero_revenue.csv', index=False)
        
        print("✓ Created 10 test CSV files")
        
    def test_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Test parsing of a single file and return detailed results."""
        print(f"\n--- Testing: {file_path.name} ---")
        
        try:
            # Parse the file
            parsed_data = self.analyzer.parse_file(str(file_path))
            
            # Validate the data
            validation_result = self.analyzer.validate_data(parsed_data)
            
            # Extract matched items for detailed analysis
            matched_items = parsed_data.get('raw_data', {}).get('matched_items', [])
            
            test_result = {
                'file_name': file_path.name,
                'success': True,
                'parsed_data': parsed_data,
                'validation': validation_result,
                'matched_items': matched_items,
                'error': None
            }
            
            # Display results
            print(f"Revenue: ${parsed_data.get('revenue', 0):,.2f}")
            print(f"COGS: ${parsed_data.get('cogs', 0):,.2f}")
            print(f"Labor Costs: ${parsed_data.get('labor_costs', 0):,.2f}")
            print(f"Overhead Costs: ${parsed_data.get('overhead_costs', 0):,.2f}")
            print(f"Confidence Score: {parsed_data.get('confidence_score', 0):.2f}")
            
            if matched_items:
                print(f"\nMatched Items ({len(matched_items)}):")
                for item in matched_items:
                    print(f"  • {item['category']}: ${item['value']:,.2f} from '{item['text']}'")
            else:
                print("No items were matched and categorized")
            
            print(f"\nValidation:")
            print(f"  Valid: {validation_result['is_valid']}")
            if validation_result['errors']:
                print(f"  Errors: {', '.join(validation_result['errors'])}")
            if validation_result['warnings']:
                print(f"  Warnings: {', '.join(validation_result['warnings'])}")
                
        except Exception as e:
            test_result = {
                'file_name': file_path.name,
                'success': False,
                'parsed_data': None,
                'validation': None,
                'matched_items': [],
                'error': str(e)
            }
            print(f"ERROR: {str(e)}")
        
        return test_result
    
    def test_keyword_recognition(self):
        """Test that the parser correctly identifies different revenue keywords."""
        print("\n=== Testing Keyword Recognition ===")
        
        keywords_test = {
            'revenue': ['revenue', 'sales', 'income', 'turnover', 'gross receipts'],
            'cogs': ['cost of goods sold', 'cogs', 'cost of sales', 'direct costs'],
            'labor_costs': ['labor', 'wages', 'salaries', 'payroll', 'compensation'],
            'overhead_costs': ['overhead', 'administrative expenses', 'sg&a', 'rent', 'utilities']
        }
        
        for category, keywords in keywords_test.items():
            print(f"\n{category.replace('_', ' ').title()} Keywords:")
            for keyword in keywords:
                result = self.analyzer._categorize_line_item(keyword.lower())
                status = "✓" if result == category else "✗"
                print(f"  {status} '{keyword}' -> {result}")
    
    def test_number_extraction(self):
        """Test different number formats."""
        print("\n=== Testing Number Extraction ===")
        
        test_values = [
            ('1000', 1000.0),
            ('$1,000.00', 1000.0),
            ('(500)', 500.0),
            ('-750.50', -750.5),
            ('2,500,000', 2500000.0),
            ('$1.2M', None),  # Should fail - not supported
            ('N/A', None),
            ('', None),
            (1500, 1500.0),
        ]
        
        for test_val, expected in test_values:
            result = self.analyzer._extract_numeric_value(test_val)
            status = "✓" if result == expected else "✗"
            print(f"  {status} '{test_val}' -> {result} (expected: {expected})")
    
    def run_all_tests(self):
        """Run comprehensive tests on all CSV files."""
        print("=== PLAnalyzer Comprehensive Test Suite ===")
        
        # Create test files
        self.create_test_csv_files()
        
        # Test keyword recognition
        self.test_keyword_recognition()
        
        # Test number extraction
        self.test_number_extraction()
        
        # Test all CSV files
        print("\n=== Testing All CSV Files ===")
        csv_files = list(self.test_files_dir.glob('*.csv'))
        
        for csv_file in sorted(csv_files):
            test_result = self.test_single_file(csv_file)
            self.test_results.append(test_result)
        
        # Generate summary report
        self.generate_summary_report()
        
        # Generate recommendations
        self.generate_recommendations()
    
    def generate_summary_report(self):
        """Generate a summary report of all test results."""
        print("\n" + "="*60)
        print("SUMMARY REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
        
        print(f"\nPASS/FAIL Status:")
        for result in self.test_results:
            status = "PASS" if result['success'] else "FAIL"
            confidence = ""
            if result['success'] and result['parsed_data']:
                conf_score = result['parsed_data'].get('confidence_score', 0)
                confidence = f" (confidence: {conf_score:.2f})"
            print(f"  {status}: {result['file_name']}{confidence}")
        
        print(f"\nValidation Issues:")
        for result in self.test_results:
            if result['success'] and result['validation']:
                val = result['validation']
                if val['errors'] or val['warnings']:
                    print(f"  {result['file_name']}:")
                    for error in val['errors']:
                        print(f"    ERROR: {error}")
                    for warning in val['warnings']:
                        print(f"    WARNING: {warning}")
        
        print(f"\nConfidence Score Analysis:")
        confidence_scores = []
        for result in self.test_results:
            if result['success'] and result['parsed_data']:
                score = result['parsed_data'].get('confidence_score', 0)
                confidence_scores.append(score)
                
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            print(f"  Average Confidence: {avg_confidence:.2f}")
            print(f"  High Confidence (>0.7): {sum(1 for s in confidence_scores if s > 0.7)}")
            print(f"  Medium Confidence (0.3-0.7): {sum(1 for s in confidence_scores if 0.3 <= s <= 0.7)}")
            print(f"  Low Confidence (<0.3): {sum(1 for s in confidence_scores if s < 0.3)}")
    
    def generate_recommendations(self):
        """Generate recommendations based on test results."""
        print(f"\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)
        
        recommendations = []
        
        # Analyze failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            recommendations.append(f"• Fix parsing failures in {len(failed_tests)} files")
            for test in failed_tests:
                recommendations.append(f"  - {test['file_name']}: {test['error']}")
        
        # Analyze confidence scores
        low_confidence_tests = [r for r in self.test_results 
                               if r['success'] and r['parsed_data'] 
                               and r['parsed_data'].get('confidence_score', 0) < 0.3]
        if low_confidence_tests:
            recommendations.append(f"• Improve keyword matching for {len(low_confidence_tests)} files with low confidence")
        
        # Analyze matched items
        no_matches_tests = [r for r in self.test_results 
                           if r['success'] and not r['matched_items']]
        if no_matches_tests:
            recommendations.append(f"• Investigate why {len(no_matches_tests)} files had no matched items")
        
        # Check for missing categories
        categories_found = set()
        for result in self.test_results:
            if result['success']:
                for item in result['matched_items']:
                    categories_found.add(item['category'])
        
        expected_categories = {'revenue', 'cogs', 'labor_costs', 'overhead_costs'}
        missing_categories = expected_categories - categories_found
        if missing_categories:
            recommendations.append(f"• Add keywords for missing categories: {', '.join(missing_categories)}")
        
        # Number format recommendations
        recommendations.append("• Consider adding support for 'M' and 'K' suffixes in number parsing")
        recommendations.append("• Add validation for unusual number formats")
        
        # Validation recommendations
        recommendations.append("• Consider adjusting confidence score thresholds based on test results")
        recommendations.append("• Add more specific validation rules for different P&L structures")
        
        if not recommendations:
            recommendations.append("• Parser is working well! Consider edge case testing with real-world files")
        
        for rec in recommendations:
            print(rec)

def main():
    """Run the comprehensive test suite."""
    tester = PLAnalyzerTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()