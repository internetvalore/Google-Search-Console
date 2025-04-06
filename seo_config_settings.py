#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration settings for the SEO Analysis Tool.
Contains constants and configuration parameters.
"""

# Meta description settings
META_DESC_MIN_LENGTH = 50  # Minimum length for a good meta description
META_DESC_MAX_LENGTH = 160  # Maximum length for a good meta description

# Image settings
IMAGE_MAX_SIZE = 100000  # Maximum size for an image in bytes (100 KB)

# Link settings
LINK_CHECK_TIMEOUT = 10  # Timeout for checking if a link is broken (in seconds)

# Crawler settings
CRAWLER_MAX_PAGES = 100  # Maximum number of pages to crawl
CRAWLER_MAX_DEPTH = 5  # Maximum depth to crawl
CRAWLER_TIMEOUT = 30  # Timeout for crawling a page (in seconds)
CRAWLER_USER_AGENT = "SEO Analysis Tool Crawler"  # User agent for the crawler

# Content loader settings
CONTENT_LOADER_MAX_CONCURRENT = 10  # Maximum number of concurrent requests
CONTENT_LOADER_TIMEOUT = 30  # Timeout for loading content (in seconds)

# Topic analyzer settings
TOPIC_ANALYZER_MAX_KEYWORDS = 10  # Maximum number of keywords to extract per page
TOPIC_ANALYZER_MAX_TOPICS = 5  # Maximum number of topics to extract per page

# Search Console settings
SEARCH_CONSOLE_CLUSTERS = 10  # Number of clusters for Search Console data

# SEMrush settings
SEMRUSH_CLUSTERS = 10  # Number of clusters for SEMrush data

# LM Studio settings
LMSTUDIO_API_URL = "http://localhost:1234/v1"  # URL for the LM Studio API
LMSTUDIO_MAX_TOKENS = 500  # Maximum number of tokens to generate
LMSTUDIO_TEMPERATURE = 0.7  # Temperature for sampling
LMSTUDIO_TOP_P = 0.95  # Top-p value for nucleus sampling

# UI settings
WINDOW_TITLE = "SEO Analysis Tool"
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
PADDING_X = 10
PADDING_Y = 10
TITLE_FONT = ("Helvetica", 16, "bold")
NORMAL_FONT = ("Helvetica", 10)
BUTTON_COLOR = "#4CAF50"  # Green
BUTTON_TEXT_COLOR = "white"
ERROR_COLOR = "red"
SUCCESS_COLOR = "green"
WARNING_COLOR = "orange"
INFO_COLOR = "blue"

# Directory settings
DATA_DIR = "data"
REPORTS_DIR = "reports"
SESSIONS_DIR = "sessions"
LOGS_DIR = "logs"

# Report settings
REPORT_OUTPUT_DIR = "reports"  # Output directory for reports
