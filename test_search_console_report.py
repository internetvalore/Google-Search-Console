#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Search Console report generation.
"""

import os
import sys
import pandas as pd
import numpy as np
from docx import Document
from datetime import datetime

# Import the necessary modules
from seo_report import ReportGenerator
from test_final_report import MockSearchConsoleAnalyzer

def test_search_console_report_generation():
    print("Testing Search Console report generation...")
    
    # Create mock analyzer
    search_console_analyzer = MockSearchConsoleAnalyzer()
    
    # Create a report generator
    report_generator = ReportGenerator()
    
    # Generate the report
    report_path = report_generator.generate_search_console_report(search_console_analyzer)
    
    # Check if the report was generated
    if os.path.exists(report_path):
        print(f"Search Console report generated successfully: {report_path}")
        print("Test passed!")
    else:
        print(f"Error: Report file not found at {report_path}")
        print("Test failed!")

if __name__ == "__main__":
    test_search_console_report_generation()
