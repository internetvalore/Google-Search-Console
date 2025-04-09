#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for final report generation.
"""

import os
import sys
import pandas as pd
import numpy as np
from docx import Document
from datetime import datetime

# Import the necessary modules
from seo_report import ReportGenerator
from test_seo_report import (
    MockMetaDescriptionAnalyzer,
    MockImageAnalyzer,
    MockLinksAnalyzer,
    MockReachabilityAnalyzer,
    MockMainTopicAnalyzer
)

class MockSearchConsoleAnalyzer:
    def __init__(self):
        self.clusters_data = [
            {
                "top_queries": ["seo", "seo tool", "seo analysis"],
                "queries": 10,
                "impressions": 1000,
                "clicks": 100,
                "avg_position": 5.5
            },
            {
                "top_queries": ["web development", "web dev", "website"],
                "queries": 5,
                "impressions": 500,
                "clicks": 50,
                "avg_position": 7.2
            }
        ]
        
        self.topics_data = {
            "https://example.com": ["SEO", "Analysis", "Tool"],
            "https://example.com/page1": ["Web Development", "Coding"]
        }
        
        self.suggestions_data = [
            {
                "source": "https://example.com",
                "target": "https://example.com/page1",
                "topic": "Web Development"
            },
            {
                "source": "https://example.com/page1",
                "target": "https://example.com",
                "topic": "SEO"
            }
        ]
    
    def get_clusters(self):
        return self.clusters_data
    
    def get_topics(self):
        return self.topics_data
    
    def suggest_internal_links(self):
        return self.suggestions_data

class MockSEMrushAnalyzer:
    def __init__(self):
        self.clusters_data = [
            {
                "top_keywords": ["seo", "seo tool", "seo analysis"],
                "keywords": 10,
                "traffic": 100,
                "avg_position": 5.5,
                "search_volume": 1000
            },
            {
                "top_keywords": ["web development", "web dev", "website"],
                "keywords": 5,
                "traffic": 50,
                "avg_position": 7.2,
                "search_volume": 500
            }
        ]
        
        self.topics_data = {
            "https://example.com": ["SEO", "Analysis", "Tool"],
            "https://example.com/page1": ["Web Development", "Coding"]
        }
        
        self.visibility_data = {
            "SEO": 0.8,
            "Web Development": 0.6
        }
        
        self.traffic_data = {
            "SEO": 100,
            "Web Development": 50
        }
        
        self.suggestions_data = [
            {
                "source": "https://example.com",
                "target": "https://example.com/page1",
                "topic": "Web Development"
            },
            {
                "source": "https://example.com/page1",
                "target": "https://example.com",
                "topic": "SEO"
            }
        ]
    
    def get_clusters(self):
        return self.clusters_data
    
    def get_topics(self):
        return self.topics_data
    
    def get_visibility(self):
        return self.visibility_data
    
    def get_traffic(self):
        return self.traffic_data
    
    def suggest_internal_links(self):
        return self.suggestions_data

def test_final_report_generation():
    print("Testing final report generation...")
    
    # Create mock analyzers
    meta_analyzer = MockMetaDescriptionAnalyzer()
    image_analyzer = MockImageAnalyzer()
    links_analyzer = MockLinksAnalyzer()
    reachability_analyzer = MockReachabilityAnalyzer()
    topic_analyzer = MockMainTopicAnalyzer()
    search_console_analyzer = MockSearchConsoleAnalyzer()
    semrush_analyzer = MockSEMrushAnalyzer()
    
    # Create a report generator
    report_generator = ReportGenerator()
    
    # Generate the report
    report_path = report_generator.generate_final_report(
        "https://example.com",
        meta_analyzer,
        image_analyzer,
        links_analyzer,
        reachability_analyzer,
        topic_analyzer,
        search_console_analyzer,
        semrush_analyzer
    )
    
    # Check if the report was generated
    if os.path.exists(report_path):
        print(f"Final report generated successfully: {report_path}")
        print("Test passed!")
    else:
        print(f"Error: Report file not found at {report_path}")
        print("Test failed!")

if __name__ == "__main__":
    test_final_report_generation()
