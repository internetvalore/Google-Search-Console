#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry point for the SEO Analysis Tool.
Contains the main application class and GUI implementation.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pickle
import threading
import time
from datetime import datetime

# Import configuration
from seo_config import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, PADDING_X, PADDING_Y,
    TITLE_FONT, NORMAL_FONT, BUTTON_COLOR, BUTTON_TEXT_COLOR,
    ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR, INFO_COLOR,
    DATA_DIR, REPORTS_DIR, SESSIONS_DIR, LOGS_DIR
)

# Import modules
from seo_url_validator import SEOURLValidator
from seo_crawler import SEOCrawler
from seo_content_loader import ContentLoader
from seo_meta_description import MetaDescriptionAnalyzer
from seo_images import ImageAnalyzer
from seo_links import LinksAnalyzer
from seo_reachability import ReachabilityAnalyzer
from seo_main_topic import MainTopicAnalyzer
from seo_search_console import SearchConsoleData, SearchConsoleAnalyzer, SearchConsoleComparison
from seo_semrush import SEMrushData, SEMrushAnalyzer
from seo_lmstudio import LMStudioClient, MetaDescriptionGenerator
from seo_report import SEOReportGenerator


class SEOAnalysisTool:
    """Main application class for the SEO Analysis Tool."""
    
    def __init__(self, root):
        """
        Initialize the SEO Analysis Tool.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.setup_window()
        
        # Create directories if they don't exist
        for directory in [DATA_DIR, REPORTS_DIR, SESSIONS_DIR, LOGS_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Configure logging
        logging.basicConfig(
            filename=os.path.join(LOGS_DIR, f"seo_tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize data structures
        self.url = ""
        self.crawler_results = None
        self.content_loader = None
        self.meta_description_analyzer = None
        self.image_analyzer = None
        self.links_analyzer = None
        self.reachability_analyzer = None
        self.main_topic_analyzer = None
        self.search_console_data = None
        self.search_console_analyzer = None
        self.search_console_data_old = None
        self.search_console_comparison = None
        self.semrush_data = None
        self.semrush_analyzer = None
        self.lm_client = None
        self.meta_description_generator = None
        self.report_generator = None
        
        # Create widgets
        self.create_widgets()
        
        # Initialize button states
        self.update_button_states()
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(True, True)
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=(PADDING_X, PADDING_Y))
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
    
    def create_widgets(self):
        """Create and configure the UI widgets."""
        self.create_title_label()
        self.create_notebook()
        self.create_status_bar()
    
    def create_title_label(self):
        """Create the title label."""
        title_frame = ttk.Frame(self.main_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame,
            text=WINDOW_TITLE,
            font=TITLE_FONT
        )
        title_label.pack(pady=10)
    
    def create_notebook(self):
        """Create the notebook with tabs."""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # Create tabs
        self.create_crawling_tab()
        self.create_analysis_tab()
        self.create_search_console_tab()
        self.create_semrush_tab()
        self.create_reports_tab()
        self.create_session_tab()
    
    def create_crawling_tab(self):
        """Create the crawling tab."""
        crawling_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(crawling_frame, text="Crawling")
        
        # Configure grid
        crawling_frame.grid_columnconfigure(1, weight=1)
        
        # URL input
        ttk.Label(crawling_frame, text="Website URL:", font=NORMAL_FONT).grid(row=0, column=0, sticky="w", pady=5)
        
        url_frame = ttk.Frame(crawling_frame)
        url_frame.grid(row=0, column=1, sticky="ew", pady=5)
        url_frame.grid_columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, font=NORMAL_FONT)
        self.url_entry.grid(row=0, column=0, sticky="ew")
        
        validate_button = ttk.Button(
            url_frame,
            text="Validate",
            command=self.validate_url
        )
        validate_button.grid(row=0, column=1, padx=(5, 0))
        
        # Crawling options
        options_frame = ttk.LabelFrame(crawling_frame, text="Crawling Options", padding=10)
        options_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Use sitemap option
        self.use_sitemap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Use Sitemap",
            variable=self.use_sitemap_var
        ).grid(row=0, column=0, sticky="w")
        
        # Use crawling option
        self.use_crawling_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Use Crawling",
            variable=self.use_crawling_var
        ).grid(row=0, column=1, sticky="w")
        
        # Max pages
        ttk.Label(options_frame, text="Max Pages:").grid(row=1, column=0, sticky="w", pady=5)
        self.max_pages_var = tk.StringVar(value="500")
        ttk.Entry(options_frame, textvariable=self.max_pages_var, width=10).grid(row=1, column=1, sticky="w", pady=5)
        
        # Max depth
        ttk.Label(options_frame, text="Max Depth:").grid(row=2, column=0, sticky="w", pady=5)
        self.max_depth_var = tk.StringVar(value="5")
        ttk.Entry(options_frame, textvariable=self.max_depth_var, width=10).grid(row=2, column=1, sticky="w", pady=5)
        
        # Crawling buttons
        buttons_frame = ttk.Frame(crawling_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.crawl_button = ttk.Button(
            buttons_frame,
            text="Crawl Website",
            command=self.crawl_website
        )
        self.crawl_button.grid(row=0, column=0, padx=5)
        
        self.load_content_button = ttk.Button(
            buttons_frame,
            text="Load Content",
            command=self.load_content,
            state="disabled"
        )
        self.load_content_button.grid(row=0, column=1, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(crawling_frame, text="Results", padding=10)
        results_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Create a text widget for displaying results
        self.crawling_results_text = tk.Text(results_frame, wrap="word", height=10)
        self.crawling_results_text.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.crawling_results_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.crawling_results_text.configure(yscrollcommand=scrollbar.set)
    
    def create_analysis_tab(self):
        """Create the analysis tab."""
        analysis_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(analysis_frame, text="Analysis")
        
        # Configure grid
        analysis_frame.grid_columnconfigure(0, weight=1)
        
        # Analysis buttons
        buttons_frame = ttk.LabelFrame(analysis_frame, text="Analysis Options", padding=10)
        buttons_frame.grid(row=0, column=0, sticky="ew", pady=10)
        
        # Create a 3x3 grid of buttons
        self.meta_desc_button = ttk.Button(
            buttons_frame,
            text="Analyze Meta Descriptions",
            command=self.analyze_meta_descriptions,
            state="disabled"
        )
        self.meta_desc_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.images_button = ttk.Button(
            buttons_frame,
            text="Analyze Images",
            command=self.analyze_images,
            state="disabled"
        )
        self.images_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.links_button = ttk.Button(
            buttons_frame,
            text="Analyze Links",
            command=self.analyze_links,
            state="disabled"
        )
        self.links_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.reachability_button = ttk.Button(
            buttons_frame,
            text="Analyze Reachability",
            command=self.analyze_reachability,
            state="disabled"
        )
        self.reachability_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.main_topic_button = ttk.Button(
            buttons_frame,
            text="Analyze Main Topics",
            command=self.analyze_main_topics,
            state="disabled"
        )
        self.main_topic_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.generate_meta_desc_button = ttk.Button(
            buttons_frame,
            text="Generate Meta Descriptions",
            command=self.generate_meta_descriptions,
            state="disabled"
        )
        self.generate_meta_desc_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        
        # Results frame
        results_frame = ttk.LabelFrame(analysis_frame, text="Results", padding=10)
        results_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Create a text widget for displaying results
        self.analysis_results_text = tk.Text(results_frame, wrap="word", height=15)
        self.analysis_results_text.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.analysis_results_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.analysis_results_text.configure(yscrollcommand=scrollbar.set)
    
    def create_search_console_tab(self):
        """Create the Search Console tab."""
        sc_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(sc_frame, text="Search Console")
        
        # Configure grid
        sc_frame.grid_columnconfigure(1, weight=1)
        
        # Load Search Console data
        ttk.Label(sc_frame, text="Search Console CSV:", font=NORMAL_FONT).grid(row=0, column=0, sticky="w", pady=5)
        
        sc_file_frame = ttk.Frame(sc_frame)
        sc_file_frame.grid(row=0, column=1, sticky="ew", pady=5)
        sc_file_frame.grid_columnconfigure(0, weight=1)
        
        self.sc_file_entry = ttk.Entry(sc_file_frame, font=NORMAL_FONT)
        self.sc_file_entry.grid(row=0, column=0, sticky="ew")
        
        browse_sc_button = ttk.Button(
            sc_file_frame,
            text="Browse",
            command=lambda: self.browse_file(self.sc_file_entry)
        )
        browse_sc_button.grid(row=0, column=1, padx=(5, 0))
        
        load_sc_button = ttk.Button(
            sc_file_frame,
            text="Load",
            command=self.load_search_console_data
        )
        load_sc_button.grid(row=0, column=2, padx=(5, 0))
        
        # Load old Search Console data for comparison
        ttk.Label(sc_frame, text="Old Search Console CSV:", font=NORMAL_FONT).grid(row=1, column=0, sticky="w", pady=5)
        
        sc_old_file_frame = ttk.Frame(sc_frame)
        sc_old_file_frame.grid(row=1, column=1, sticky="ew", pady=5)
        sc_old_file_frame.grid_columnconfigure(0, weight=1)
        
        self.sc_old_file_entry = ttk.Entry(sc_old_file_frame, font=NORMAL_FONT)
        self.sc_old_file_entry.grid(row=0, column=0, sticky="ew")
        
        browse_sc_old_button = ttk.Button(
            sc_old_file_frame,
            text="Browse",
            command=lambda: self.browse_file(self.sc_old_file_entry)
        )
        browse_sc_old_button.grid(row=0, column=1, padx=(5, 0))
        
        load_sc_old_button = ttk.Button(
            sc_old_file_frame,
            text="Load",
            command=self.load_old_search_console_data
        )
        load_sc_old_button.grid(row=0, column=2, padx=(5, 0))
        
        # Analysis buttons
        buttons_frame = ttk.LabelFrame(sc_frame, text="Analysis Options", padding=10)
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.sc_cluster_button = ttk.Button(
            buttons_frame,
            text="Cluster Queries",
            command=self.cluster_search_console_queries,
            state="disabled"
        )
        self.sc_cluster_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.sc_topics_button = ttk.Button(
            buttons_frame,
            text="Identify Topics",
            command=self.identify_search_console_topics,
            state="disabled"
        )
        self.sc_topics_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.sc_compare_button = ttk.Button(
            buttons_frame,
            text="Compare Datasets",
            command=self.compare_search_console_data,
            state="disabled"
        )
        self.sc_compare_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.sc_suggest_button = ttk.Button(
            buttons_frame,
            text="Suggest Internal Links",
            command=self.suggest_search_console_links,
            state="disabled"
        )
        self.sc_suggest_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(sc_frame, text="Results", padding=10)
        results_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Create a text widget for displaying results
        self.sc_results_text = tk.Text(results_frame, wrap="word", height=15)
        self.sc_results_text.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.sc_results_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.sc_results_text.configure(yscrollcommand=scrollbar.set)
    
    def create_semrush_tab(self):
        """Create the SEMrush tab."""
        sr_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(sr_frame, text="SEMrush")
        
        # Configure grid
        sr_frame.grid_columnconfigure(1, weight=1)
        
        # Load SEMrush data
        ttk.Label(sr_frame, text="SEMrush CSV:", font=NORMAL_FONT).grid(row=0, column=0, sticky="w", pady=5)
        
        sr_file_frame = ttk.Frame(sr_frame)
        sr_file_frame.grid(row=0, column=1, sticky="ew", pady=5)
        sr_file_frame.grid_columnconfigure(0, weight=1)
        
        self.sr_file_entry = ttk.Entry(sr_file_frame, font=NORMAL_FONT)
        self.sr_file_entry.grid(row=0, column=0, sticky="ew")
        
        browse_sr_button = ttk.Button(
            sr_file_frame,
            text="Browse",
            command=lambda: self.browse_file(self.sr_file_entry)
        )
        browse_sr_button.grid(row=0, column=1, padx=(5, 0))
        
        load_sr_button = ttk.Button(
            sr_file_frame,
            text="Load",
            command=self.load_semrush_data
        )
        load_sr_button.grid(row=0, column=2, padx=(5, 0))
        
        # Analysis buttons
        buttons_frame = ttk.LabelFrame(sr_frame, text="Analysis Options", padding=10)
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.sr_cluster_button = ttk.Button(
            buttons_frame,
            text="Cluster Keywords",
            command=self.cluster_semrush_keywords,
            state="disabled"
        )
        self.sr_cluster_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.sr_topics_button = ttk.Button(
            buttons_frame,
            text="Identify Topics",
            command=self.identify_semrush_topics,
            state="disabled"
        )
        self.sr_topics_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.sr_position_button = ttk.Button(
            buttons_frame,
            text="Analyze Positions",
            command=self.analyze_semrush_positions,
            state="disabled"
        )
        self.sr_position_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.sr_suggest_button = ttk.Button(
            buttons_frame,
            text="Suggest Internal Links",
            command=self.suggest_semrush_links,
            state="disabled"
        )
        self.sr_suggest_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(sr_frame, text="Results", padding=10)
        results_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Create a text widget for displaying results
        self.sr_results_text = tk.Text(results_frame, wrap="word", height=15)
        self.sr_results_text.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.sr_results_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.sr_results_text.configure(yscrollcommand=scrollbar.set)
    
    def create_reports_tab(self):
        """Create the reports tab."""
        reports_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(reports_frame, text="Reports")
        
        # Configure grid
        reports_frame.grid_columnconfigure(0, weight=1)
        
        # Report buttons
        buttons_frame = ttk.LabelFrame(reports_frame, text="Generate Reports", padding=10)
        buttons_frame.grid(row=0, column=0, sticky="ew", pady=10)
        
        # Create a grid of buttons
        self.url_stats_report_button = ttk.Button(
            buttons_frame,
            text="URL Statistics Report",
            command=self.generate_url_statistics_report,
            state="disabled"
        )
        self.url_stats_report_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.meta_desc_report_button = ttk.Button(
            buttons_frame,
            text="Meta Description Report",
            command=self.generate_meta_description_report,
            state="disabled"
        )
        self.meta_desc_report_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.images_report_button = ttk.Button(
            buttons_frame,
            text="Images Report",
            command=self.generate_images_report,
            state="disabled"
        )
        self.images_report_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.links_report_button = ttk.Button(
            buttons_frame,
            text="Links Report",
            command=self.generate_links_report,
            state="disabled"
        )
        self.links_report_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.reachability_report_button = ttk.Button(
            buttons_frame,
            text="Reachability Report",
            command=self.generate_reachability_report,
            state="disabled"
        )
        self.reachability_report_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.main_topic_report_button = ttk.Button(
            buttons_frame,
            text="Main Topic Report",
            command=self.generate_main_topic_report,
            state="disabled"
        )
        self.main_topic_report_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        
        self.sc_report_button = ttk.Button(
            buttons_frame,
            text="Search Console Report",
            command=self.generate_search_console_report,
            state="disabled"
        )
        self.sc_report_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        self.sr_report_button = ttk.Button(
            buttons_frame,
            text="SEMrush Report",
            command=self.generate_semrush_report,
            state="disabled"
        )
        self.sr_report_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.comprehensive_report_button = ttk.Button(
            buttons_frame,
            text="Comprehensive Report",
            command=self.generate_comprehensive_report,
            state="disabled"
        )
        self.comprehensive_report_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        
        # Results frame
        results_frame = ttk.LabelFrame(reports_frame, text="Results", padding=10)
        results_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Create a text widget for displaying results
        self.reports_results_text = tk.Text(results_frame, wrap="word", height=15)
        self.reports_results_text.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.reports_results_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.reports_results_text.configure(yscrollcommand=scrollbar.set)
    
    def create_session_tab(self):
        """Create the session tab."""
        session_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(session_frame, text="Session")
        
        # Configure grid
        session_frame.grid_columnconfigure(1, weight=1)
        
        # Save session
        ttk.Label(session_frame, text="Save Session:", font=NORMAL_FONT).grid(row=0, column=0, sticky="w", pady=5)
        
        save_frame = ttk.Frame(session_frame)
        save_frame.grid(row=0, column=1, sticky="ew", pady=5)
        save_frame.grid_columnconfigure(0, weight=1)
        
        self.save_session_entry = ttk.Entry(save_frame, font=NORMAL_FONT)
        self.save_session_entry.grid(row=0, column=0, sticky="ew")
        
        save_session_button = ttk.Button(
            save_frame,
            text="Save",
            command=self.save_session
        )
        save_session_button.grid(row=0, column=1, padx=(5, 0))
        
        # Load session
        ttk.Label(session_frame, text="Load Session:", font=NORMAL_FONT).grid(row=1, column=0, sticky="w", pady=5)
        
        load_frame = ttk.Frame(session_frame)
        load_frame.grid(row=1, column=1, sticky="ew", pady=5)
        load_frame.grid_columnconfigure(0, weight=1)
        
        self.load_session_entry = ttk.Entry(load_frame, font=NORMAL_FONT)
        self.load_session_entry.grid(row=0, column=0, sticky="ew")
        
        browse_session_button = ttk.Button(
            load_frame,
            text="Browse",
            command=lambda: self.browse_file(self.load_session_entry)
        )
        browse_session_button.grid(row=0, column=1, padx=(5, 0))
        
        load_session_button = ttk.Button(
            load_frame,
            text="Load",
            command=self.load_session
        )
        load_session_button.grid(row=0, column=2, padx=(5, 0))
        
        # Session info frame
        info_frame = ttk.LabelFrame(session_frame, text="Session Information", padding=10)
        info_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(0, weight=1)
        
        # Create a text widget for displaying session info
        self.session_info_text = tk.Text(info_frame, wrap="word", height=15)
        self.session_info_text.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.session_info_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.session_info_text.configure(yscrollcommand=scrollbar.set)
    
    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Label(
            self.main_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=2, column=0, sticky="
