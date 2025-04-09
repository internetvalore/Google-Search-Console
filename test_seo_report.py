#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for SEO report generation.
"""

import os
import sys
import pandas as pd
import numpy as np
from docx import Document
from datetime import datetime

# Import the necessary modules
from seo_report import ReportGenerator
from seo_meta_description import MetaDescriptionAnalyzer
from seo_images import ImageAnalyzer
from seo_links import LinksAnalyzer
from seo_reachability import ReachabilityAnalyzer
from seo_main_topic import MainTopicAnalyzer

class MockMetaDescriptionAnalyzer:
    def __init__(self):
        self.data = {
            "URL": ["https://example.com", "https://example.com/page1"],
            "Has Meta Description": [True, False],
            "Meta Description": ["This is a meta description", ""],
            "Meta Description Length": [25, 0],
            "Meta Description Quality": ["good", "too_short"]
        }
    
    def to_dataframe(self):
        return pd.DataFrame(self.data)

class MockImageAnalyzer:
    def __init__(self):
        self.data = {
            "URL": ["https://example.com", "https://example.com/page1"],
            "Image Source": ["image1.jpg", "image2.jpg"],
            "Has Alt Text": [True, False],
            "Alt Text": ["Alt text for image 1", ""],
            "Image Size": [50000, 150000]
        }
    
    def to_dataframe(self):
        return pd.DataFrame(self.data)

class MockLinksAnalyzer:
    def __init__(self):
        self.data = {
            "URL": ["https://example.com", "https://example.com/page1"],
            "Link": ["https://example.com/page1", "https://external.com"],
            "Link Text": ["Page 1", "External Link"],
            "Is Internal": [True, False],
            "Is External": [False, True],
            "Is Broken": [False, False],
            "Is Nofollow": [False, True]
        }
    
    def to_dataframe(self):
        return pd.DataFrame(self.data)

class MockReachabilityAnalyzer:
    def __init__(self):
        self.data = {
            "URL": ["https://example.com", "https://example.com/page1", "https://example.com/orphan"],
            "Is Reachable": [True, True, False],
            "Is Orphan Page": [False, False, True],
            "Clicks from Home": [0, 1, -1]
        }
    
    def to_dataframe(self):
        return pd.DataFrame(self.data)

class MockMainTopicAnalyzer:
    def __init__(self):
        self.data = {
            "URL": ["https://example.com", "https://example.com/page1"],
            "Main Topics": ["SEO, Analysis", "Web Development"],
            "Keywords": ["SEO, tool, analysis", "web, development, coding"]
        }
    
    def to_dataframe(self):
        return pd.DataFrame(self.data)

def test_seo_report_generation():
    print("Testing SEO report generation...")
    
    # Create mock analyzers
    meta_analyzer = MockMetaDescriptionAnalyzer()
    image_analyzer = MockImageAnalyzer()
    links_analyzer = MockLinksAnalyzer()
    reachability_analyzer = MockReachabilityAnalyzer()
    topic_analyzer = MockMainTopicAnalyzer()
    
    # Create a report generator
    report_generator = ReportGenerator()
    
    # Generate the report
    report_path = report_generator.generate_seo_report(
        "https://example.com",
        meta_analyzer,
        image_analyzer,
        links_analyzer,
        reachability_analyzer,
        topic_analyzer
    )
    
    # Check if the report was generated
    if os.path.exists(report_path):
        print(f"SEO report generated successfully: {report_path}")
        print("Test passed!")
    else:
        print(f"Error: Report file not found at {report_path}")
        print("Test failed!")

if __name__ == "__main__":
    test_seo_report_generation()
