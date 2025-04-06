#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration settings for the SEO Analysis Tool.
"""

# Window settings
WINDOW_TITLE = "SEO Analysis Tool"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# UI settings
PADDING_X = 20
PADDING_Y = 20
TITLE_FONT = ("Arial", 16, "bold")
NORMAL_FONT = ("Arial", 12)
SMALL_FONT = ("Arial", 10)
BUTTON_COLOR = "#4CAF50"
BUTTON_TEXT_COLOR = "white"
ERROR_COLOR = "red"
SUCCESS_COLOR = "green"
WARNING_COLOR = "orange"
INFO_COLOR = "blue"
WRAP_LENGTH = 450

# URL validation settings
DEFAULT_URL_PREFIX = "https://"
REQUEST_TIMEOUT = 10
VALID_SCHEMES = ['http', 'https']

# Crawling settings
MAX_PAGES = 500
CRAWL_DELAY = 0.5
USER_AGENT = "SEO Analysis Tool/1.0"
RESPECT_ROBOTS_TXT = True
MAX_DEPTH = 5

# Content loading settings
ASYNC_CONCURRENCY = 10
ASYNC_TIMEOUT = 30

# NLP settings
SPACY_MODEL = "en_core_web_sm"
MIN_KEYWORD_FREQ = 3
MAX_KEYWORDS = 20
STOPWORDS_LANG = "english"

# Report settings
REPORT_TEMPLATE = "templates/report_template.docx"
REPORT_FILENAME = "SEO_Analysis_Report.docx"
CHART_DPI = 300
CHART_WIDTH = 10
CHART_HEIGHT = 6

# LM Studio settings
LMSTUDIO_API_URL = "http://localhost:1234/v1"
LMSTUDIO_MODEL = "default"
LMSTUDIO_MAX_TOKENS = 500
LMSTUDIO_TEMPERATURE = 0.7

# File paths
DATA_DIR = "data"
REPORTS_DIR = "reports"
SESSIONS_DIR = "sessions"
LOGS_DIR = "logs"

# CSV column names
# Search Console CSV columns
SC_QUERY_COL = "Query"
SC_LANDING_PAGE_COL = "Landing Page"
SC_IMPRESSIONS_COL = "Impressions"
SC_CLICKS_COL = "Url Clicks"
SC_POSITION_COL = "Average Position"
SC_TOPIC_COL = "Topic"

# SEMrush CSV columns
SR_KEYWORD_COL = "Keyword"
SR_POSITION_COL = "Position"
SR_PREV_POSITION_COL = "Previous position"
SR_SEARCH_VOLUME_COL = "Search Volume"
SR_KEYWORD_DIFFICULTY_COL = "Keyword Difficulty"
SR_CPC_COL = "CPC"
SR_URL_COL = "URL"
SR_TRAFFIC_COL = "Traffic"
SR_TRAFFIC_PERCENT_COL = "Traffic (%)"
SR_TRAFFIC_COST_COL = "Traffic Cost"
SR_COMPETITION_COL = "Competition"
SR_RESULTS_COL = "Number of Results"
SR_TRENDS_COL = "Trends"
SR_TIMESTAMP_COL = "Timestamp"
SR_SERP_FEATURES_COL = "SERP Features by Keyword"
SR_KEYWORD_INTENTS_COL = "Keyword Intents"
SR_POSITION_TYPE_COL = "Position Type"
