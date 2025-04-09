#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for comparison report generation.
"""

import os
import sys
import pandas as pd
import numpy as np
from docx import Document
from datetime import datetime

# Import the necessary modules
from seo_report import ReportGenerator

class MockSearchConsoleComparison:
    def __init__(self):
        self.query_comparison_data = {
            "seo": {
                "impressions_before": 1000,
                "impressions_after": 1200,
                "clicks_before": 100,
                "clicks_after": 120,
                "position_before": 5.5,
                "position_after": 4.8,
                "ctr_before": 0.1,
                "ctr_after": 0.1
            },
            "web development": {
                "impressions_before": 500,
                "impressions_after": 600,
                "clicks_before": 50,
                "clicks_after": 60,
                "position_before": 7.2,
                "position_after": 6.5,
                "ctr_before": 0.1,
                "ctr_after": 0.1
            }
        }
        
        self.landing_page_comparison_data = {
            "https://example.com": {
                "impressions_before": 1000,
                "impressions_after": 1200,
                "clicks_before": 100,
                "clicks_after": 120,
                "position_before": 5.5,
                "position_after": 4.8,
                "ctr_before": 0.1,
                "ctr_after": 0.1
            },
            "https://example.com/page1": {
                "impressions_before": 500,
                "impressions_after": 600,
                "clicks_before": 50,
                "clicks_after": 60,
                "position_before": 7.2,
                "position_after": 6.5,
                "ctr_before": 0.1,
                "ctr_after": 0.1
            }
        }
        
        self.improved_queries_data = [
            {
                "query": "seo",
                "impressions_before": 1000,
                "impressions_after": 1200,
                "clicks_before": 100,
                "clicks_after": 120,
                "position_before": 5.5,
                "position_after": 4.8,
                "ctr_before": 0.1,
                "ctr_after": 0.1
            }
        ]
        
        self.declined_queries_data = [
            {
                "query": "web design",
                "impressions_before": 300,
                "impressions_after": 200,
                "clicks_before": 30,
                "clicks_after": 20,
                "position_before": 6.0,
                "position_after": 7.0,
                "ctr_before": 0.1,
                "ctr_after": 0.1
            }
        ]
        
        self.improved_landing_pages_data = [
            {
                "landing_page": "https://example.com",
                "impressions_before": 1000,
                "impressions_after": 1200,
                "clicks_before": 100,
                "clicks_after": 120,
                "position_before": 5.5,
                "position_after": 4.8,
                "ctr_before": 0.1,
                "ctr_after": 0.1
            }
        ]
        
        self.declined_landing_pages_data = [
            {
                "landing_page": "https://example.com/old-page",
                "impressions_before": 300,
                "impressions_after": 200,
                "clicks_before": 30,
                "clicks_after": 20,
                "position_before": 6.0,
                "position_after": 7.0,
                "ctr_before": 0.1,
                "ctr_after": 0.1
            }
        ]
    
    def get_query_comparison(self):
        return self.query_comparison_data
    
    def get_landing_page_comparison(self):
        return self.landing_page_comparison_data
    
    def get_improved_queries(self):
        return self.improved_queries_data
    
    def get_declined_queries(self):
        return self.declined_queries_data
    
    def get_improved_landing_pages(self):
        return self.improved_landing_pages_data
    
    def get_declined_landing_pages(self):
        return self.declined_landing_pages_data

def test_comparison_report_generation():
    print("Testing comparison report generation...")
    
    # Create mock comparison
    search_console_comparison = MockSearchConsoleComparison()
    
    # Create a report generator
    report_generator = ReportGenerator()
    
    # Generate the report
    report_path = report_generator.generate_comparison_report(search_console_comparison)
    
    # Check if the report was generated
    if os.path.exists(report_path):
        print(f"Comparison report generated successfully: {report_path}")
        print("Test passed!")
    else:
        print(f"Error: Report file not found at {report_path}")
        print("Test failed!")

if __name__ == "__main__":
    test_comparison_report_generation()
