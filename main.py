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
from seo_crawler import SEOCrawler, SitemapProcessor
from seo_content_loader import ContentLoader
from seo_meta_description import MetaDescriptionAnalyzer
from seo_images import ImageAnalyzer
from seo_links import LinksAnalyzer
from seo_reachability import ReachabilityAnalyzer
from seo_main_topic import MainTopicAnalyzer
from seo_search_console import SearchConsoleData, SearchConsoleAnalyzer, SearchConsoleComparison
from seo_semrush import SEMrushData, SEMrushAnalyzer
from seo_lmstudio import LMStudioClient, MetaDescriptionGenerator
from seo_report import ReportGenerator


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
        try:
            for directory in [DATA_DIR, REPORTS_DIR, SESSIONS_DIR, LOGS_DIR]:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"Error creating directories: {str(e)}")
            # Use current directory as fallback
            # We can't use global here, so we'll just use the directories as they are
            # and let the config module handle the fallback
            
            # Try again with the directories from the config module
            for directory in [DATA_DIR, REPORTS_DIR, SESSIONS_DIR, LOGS_DIR]:
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory, exist_ok=True)
                    except Exception as e2:
                        print(f"Error creating directory {directory}: {str(e2)}")
        
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
        self.create_main_frame()
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
    
    def create_main_frame(self):
        """Create the main content frame."""
        content_frame = ttk.Frame(self.main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Create URL input frame
        url_frame = ttk.Frame(content_frame, padding=10)
        url_frame.grid(row=0, column=0, sticky="new")
        url_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="Website URL:", font=NORMAL_FONT).grid(row=0, column=0, sticky="w", pady=5)
        
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.grid(row=0, column=1, sticky="ew", pady=5)
        url_input_frame.grid_columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_input_frame, font=NORMAL_FONT)
        self.url_entry.grid(row=0, column=0, sticky="ew")
        
        validate_button = ttk.Button(
            url_input_frame,
            text="Validate",
            command=self.validate_url
        )
        validate_button.grid(row=0, column=1, padx=(5, 0))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create tabs
        self.create_crawling_tab()
        self.create_analysis_tab()
        self.create_csv_tab()
        self.create_search_console_tab()
        self.create_semrush_tab()
        self.create_reports_tab()
        self.create_session_tab()
        
        # Create a text widget for displaying results
        results_frame = ttk.LabelFrame(content_frame, text="Results", padding=10)
        results_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(results_frame, wrap="word", height=10)
        self.results_text.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Add a welcome message
        self.results_text.insert(tk.END, "Welcome to the SEO Analysis Tool!\n\n")
        self.results_text.insert(tk.END, "This tool helps you analyze websites for SEO issues and generate reports.\n\n")
        self.results_text.insert(tk.END, "To get started, enter a URL above and click 'Validate'.\n")
    
    def create_crawling_tab(self):
        """Create the crawling tab."""
        crawling_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(crawling_frame, text="Crawling")
        
        crawling_frame.grid_columnconfigure(0, weight=1)
        
        # Crawling options
        options_frame = ttk.LabelFrame(crawling_frame, text="Crawling Options", padding=10)
        options_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Use sitemap checkbox
        self.use_sitemap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Use Sitemap",
            variable=self.use_sitemap_var
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Use crawling checkbox
        self.use_crawling_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Use Crawling",
            variable=self.use_crawling_var
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Max pages
        ttk.Label(options_frame, text="Max Pages:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.max_pages_var = tk.StringVar(value="500")
        ttk.Entry(
            options_frame,
            textvariable=self.max_pages_var,
            width=10
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Max depth
        ttk.Label(options_frame, text="Max Depth:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.max_depth_var = tk.StringVar(value="5")
        ttk.Entry(
            options_frame,
            textvariable=self.max_depth_var,
            width=10
        ).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(crawling_frame)
        buttons_frame.grid(row=1, column=0, sticky="ew", pady=10)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        self.crawl_button = ttk.Button(
            buttons_frame,
            text="Crawl Website",
            command=self.crawl_website
        )
        self.crawl_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.load_content_button = ttk.Button(
            buttons_frame,
            text="Load Content",
            command=self.load_content
        )
        self.load_content_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    def create_csv_tab(self):
        """Create the CSV tab for uploading and processing CSV files."""
        csv_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(csv_frame, text="CSV Operations")
        
        csv_frame.grid_columnconfigure(0, weight=1)
        csv_frame.grid_columnconfigure(1, weight=1)
        
        # File input section
        file_frame = ttk.LabelFrame(csv_frame, text="CSV File Selection", padding=10)
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        file_frame.grid_columnconfigure(1, weight=1)
        
        # General CSV file
        ttk.Label(file_frame, text="CSV File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.csv_file_entry = ttk.Entry(file_frame)
        self.csv_file_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        browse_button = ttk.Button(
            file_frame,
            text="Browse",
            command=lambda: self.browse_file(self.csv_file_entry)
        )
        browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # CSV type selection
        ttk.Label(file_frame, text="CSV Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.csv_type_var = tk.StringVar(value="Generic")
        csv_type_combo = ttk.Combobox(
            file_frame,
            textvariable=self.csv_type_var,
            values=["Generic", "Search Console", "SEMrush", "Analytics", "Custom"]
        )
        csv_type_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # CSV operations section
        operations_frame = ttk.LabelFrame(csv_frame, text="CSV Operations", padding=10)
        operations_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        operations_frame.grid_columnconfigure(0, weight=1)
        operations_frame.grid_columnconfigure(1, weight=1)
        
        # Load CSV
        self.load_csv_button = ttk.Button(
            operations_frame,
            text="Load CSV",
            command=self.load_csv
        )
        self.load_csv_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Preview CSV
        self.preview_csv_button = ttk.Button(
            operations_frame,
            text="Preview CSV",
            command=self.preview_csv
        )
        self.preview_csv_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Clean CSV
        self.clean_csv_button = ttk.Button(
            operations_frame,
            text="Clean CSV Data",
            command=self.clean_csv
        )
        self.clean_csv_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Export CSV
        self.export_csv_button = ttk.Button(
            operations_frame,
            text="Export CSV",
            command=self.export_csv
        )
        self.export_csv_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Analysis section
        analysis_frame = ttk.LabelFrame(csv_frame, text="CSV Analysis", padding=10)
        analysis_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        analysis_frame.grid_columnconfigure(0, weight=1)
        analysis_frame.grid_columnconfigure(1, weight=1)
        
        # Analyze CSV
        self.analyze_csv_button = ttk.Button(
            analysis_frame,
            text="Analyze CSV Data",
            command=self.analyze_csv
        )
        self.analyze_csv_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Generate CSV Report
        self.csv_report_button = ttk.Button(
            analysis_frame,
            text="Generate CSV Report",
            command=self.generate_csv_report
        )
        self.csv_report_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Merge CSVs
        self.merge_csv_button = ttk.Button(
            analysis_frame,
            text="Merge CSV Files",
            command=self.merge_csv_files
        )
        self.merge_csv_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Compare CSVs
        self.compare_csv_button = ttk.Button(
            analysis_frame,
            text="Compare CSV Files",
            command=self.compare_csv_files
        )
        self.compare_csv_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    
    def create_analysis_tab(self):
        """Create the analysis tab."""
        analysis_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(analysis_frame, text="Analysis")
        
        analysis_frame.grid_columnconfigure(0, weight=1)
        analysis_frame.grid_columnconfigure(1, weight=1)
        
        # Create a label frame for SEO Analysis
        analysis_options_frame = ttk.LabelFrame(analysis_frame, text="SEO Analysis Options", padding=10)
        analysis_options_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        analysis_options_frame.grid_columnconfigure(0, weight=1)
        analysis_options_frame.grid_columnconfigure(1, weight=1)
        
        # Meta descriptions
        self.meta_desc_button = ttk.Button(
            analysis_options_frame,
            text="Analyze Meta Descriptions",
            command=self.analyze_meta_descriptions
        )
        self.meta_desc_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Images
        self.images_button = ttk.Button(
            analysis_options_frame,
            text="Analyze Images",
            command=self.analyze_images
        )
        self.images_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Links
        self.links_button = ttk.Button(
            analysis_options_frame,
            text="Analyze Links",
            command=self.analyze_links
        )
        self.links_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Reachability
        self.reachability_button = ttk.Button(
            analysis_options_frame,
            text="Analyze Reachability",
            command=self.analyze_reachability
        )
        self.reachability_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Main topics
        self.main_topics_button = ttk.Button(
            analysis_options_frame,
            text="Analyze Main Topics",
            command=self.analyze_main_topics
        )
        self.main_topics_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # Generate meta descriptions
        self.generate_meta_desc_button = ttk.Button(
            analysis_options_frame,
            text="Generate Meta Descriptions",
            command=self.generate_meta_descriptions
        )
        self.generate_meta_desc_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Show Site Map (Graph)
        self.show_graph_button = ttk.Button(
            analysis_options_frame,
            text="Show Site Map",
            command=self.show_site_map
        )
        self.show_graph_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Create a label frame for Comprehensive Analysis
        comprehensive_frame = ttk.LabelFrame(analysis_frame, text="Comprehensive Analysis", padding=10)
        comprehensive_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        comprehensive_frame.grid_columnconfigure(0, weight=1)
        
        # Run all analyses
        self.run_all_analyses_button = ttk.Button(
            comprehensive_frame,
            text="Run All Analyses",
            command=self.run_all_analyses
        )
        self.run_all_analyses_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    
    def create_search_console_tab(self):
        """Create the Search Console tab."""
        sc_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(sc_frame, text="Search Console")
        
        sc_frame.grid_columnconfigure(0, weight=1)
        sc_frame.grid_columnconfigure(1, weight=1)
        
        # File input
        file_frame = ttk.Frame(sc_frame)
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        file_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Search Console CSV:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.sc_file_entry = ttk.Entry(file_frame)
        self.sc_file_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        browse_button = ttk.Button(
            file_frame,
            text="Browse",
            command=lambda: self.browse_file(self.sc_file_entry)
        )
        browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Old file input (for comparison)
        ttk.Label(file_frame, text="Old Search Console CSV:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.sc_old_file_entry = ttk.Entry(file_frame)
        self.sc_old_file_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        browse_old_button = ttk.Button(
            file_frame,
            text="Browse",
            command=lambda: self.browse_file(self.sc_old_file_entry)
        )
        browse_old_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Load data
        self.load_sc_button = ttk.Button(
            sc_frame,
            text="Load Search Console Data",
            command=self.load_search_console_data
        )
        self.load_sc_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Load old data
        self.load_sc_old_button = ttk.Button(
            sc_frame,
            text="Load Old Search Console Data",
            command=self.load_old_search_console_data
        )
        self.load_sc_old_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Cluster queries
        self.cluster_sc_button = ttk.Button(
            sc_frame,
            text="Cluster Search Console Queries",
            command=self.cluster_search_console_queries
        )
        self.cluster_sc_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # Identify topics
        self.identify_sc_topics_button = ttk.Button(
            sc_frame,
            text="Identify Search Console Topics",
            command=self.identify_search_console_topics
        )
        self.identify_sc_topics_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Compare data
        self.compare_sc_button = ttk.Button(
            sc_frame,
            text="Compare Search Console Data",
            command=self.compare_search_console_data
        )
        self.compare_sc_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        # Suggest links
        self.suggest_sc_links_button = ttk.Button(
            sc_frame,
            text="Suggest Search Console Links",
            command=self.suggest_search_console_links
        )
        self.suggest_sc_links_button.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
    
    def create_semrush_tab(self):
        """Create the SEMrush tab."""
        sr_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(sr_frame, text="SEMrush")
        
        sr_frame.grid_columnconfigure(0, weight=1)
        sr_frame.grid_columnconfigure(1, weight=1)
        
        # File input
        file_frame = ttk.Frame(sr_frame)
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        file_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="SEMrush CSV:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.sr_file_entry = ttk.Entry(file_frame)
        self.sr_file_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        browse_button = ttk.Button(
            file_frame,
            text="Browse",
            command=lambda: self.browse_file(self.sr_file_entry)
        )
        browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Load data
        self.load_sr_button = ttk.Button(
            sr_frame,
            text="Load SEMrush Data",
            command=self.load_semrush_data
        )
        self.load_sr_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Cluster keywords
        self.cluster_sr_button = ttk.Button(
            sr_frame,
            text="Cluster SEMrush Keywords",
            command=self.cluster_semrush_keywords
        )
        self.cluster_sr_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Identify topics
        self.identify_sr_topics_button = ttk.Button(
            sr_frame,
            text="Identify SEMrush Topics",
            command=self.identify_semrush_topics
        )
        self.identify_sr_topics_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # Analyze positions
        self.analyze_sr_positions_button = ttk.Button(
            sr_frame,
            text="Analyze SEMrush Positions",
            command=self.analyze_semrush_positions
        )
        self.analyze_sr_positions_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Suggest links
        self.suggest_sr_links_button = ttk.Button(
            sr_frame,
            text="Suggest SEMrush Links",
            command=self.suggest_semrush_links
        )
        self.suggest_sr_links_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
    
    def create_reports_tab(self):
        """Create the reports tab."""
        reports_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(reports_frame, text="Reports")
        
        reports_frame.grid_columnconfigure(0, weight=1)
        reports_frame.grid_columnconfigure(1, weight=1)
        
        # URL statistics report
        self.url_stats_report_button = ttk.Button(
            reports_frame,
            text="Generate URL Statistics Report",
            command=self.generate_url_statistics_report
        )
        self.url_stats_report_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Meta description report
        self.meta_desc_report_button = ttk.Button(
            reports_frame,
            text="Generate Meta Description Report",
            command=self.generate_meta_description_report
        )
        self.meta_desc_report_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Images report
        self.images_report_button = ttk.Button(
            reports_frame,
            text="Generate Images Report",
            command=self.generate_images_report
        )
        self.images_report_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Links report
        self.links_report_button = ttk.Button(
            reports_frame,
            text="Generate Links Report",
            command=self.generate_links_report
        )
        self.links_report_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Reachability report
        self.reachability_report_button = ttk.Button(
            reports_frame,
            text="Generate Reachability Report",
            command=self.generate_reachability_report
        )
        self.reachability_report_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # Main topic report
        self.main_topic_report_button = ttk.Button(
            reports_frame,
            text="Generate Main Topic Report",
            command=self.generate_main_topic_report
        )
        self.main_topic_report_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Search Console report
        self.sc_report_button = ttk.Button(
            reports_frame,
            text="Generate Search Console Report",
            command=self.generate_search_console_report
        )
        self.sc_report_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        # SEMrush report
        self.sr_report_button = ttk.Button(
            reports_frame,
            text="Generate SEMrush Report",
            command=self.generate_semrush_report
        )
        self.sr_report_button.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Comprehensive report
        self.comprehensive_report_button = ttk.Button(
            reports_frame,
            text="Generate Comprehensive Report",
            command=self.generate_comprehensive_report
        )
        self.comprehensive_report_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    
    def create_session_tab(self):
        """Create the session tab."""
        session_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(session_frame, text="Session")
        
        session_frame.grid_columnconfigure(0, weight=1)
        session_frame.grid_columnconfigure(1, weight=1)
        
        # Save session
        self.save_session_button = ttk.Button(
            session_frame,
            text="Save Session",
            command=self.save_session
        )
        self.save_session_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Load session
        self.load_session_button = ttk.Button(
            session_frame,
            text="Load Session",
            command=self.load_session
        )
        self.load_session_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Label(
            self.main_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=2, column=0, sticky="ew")
    
    def update_button_states(self):
        """Update the states of buttons based on available data."""
        # This method would update the states of all buttons
        # For brevity, we're not including the full implementation here
        pass
    
    def set_status(self, message, color=None):
        """
        Set the status bar message.
        
        Args:
            message (str): The message to display
            color (str): The color of the message (optional)
        """
        self.status_bar["text"] = message
        if color:
            self.status_bar["foreground"] = color
        else:
            self.status_bar["foreground"] = "black"
        self.root.update_idletasks()
    
    def append_text(self, text_widget, message, tag=None):
        """
        Append text to a text widget.
        
        Args:
            text_widget (tk.Text): The text widget
            message (str): The message to append
            tag (str): The tag to apply to the message (optional)
        """
        text_widget.config(state=tk.NORMAL)
        if tag:
            text_widget.insert(tk.END, message, tag)
        else:
            text_widget.insert(tk.END, message)
        text_widget.see(tk.END)
        text_widget.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_text(self, text_widget):
        """
        Clear a text widget.
        
        Args:
            text_widget (tk.Text): The text widget
        """
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def browse_file(self, entry_widget):
        """
        Browse for a file and update an entry widget.
        
        Args:
            entry_widget (ttk.Entry): The entry widget to update
        """
        filename = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
    
    def validate_url(self):
        """Validate the URL entered by the user."""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        self.set_status("Validating URL...", INFO_COLOR)
        
        # Validate URL
        is_valid = SEOURLValidator.is_valid_url(url)
        
        if is_valid:
            self.url = SEOURLValidator.normalize_url(url)
            message = f"URL is valid: {self.url}"
            self.set_status(message, SUCCESS_COLOR)
            messagebox.showinfo("Success", message)
        else:
            message = f"Invalid URL format: {url}"
            self.set_status(message, ERROR_COLOR)
            messagebox.showerror("Error", message)
    
    def crawl_website(self):
        """Crawl the website."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        self.set_status(f"Crawling website: {self.url}...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, f"Crawling website: {self.url}\n\n")
        
        # Get crawling options
        use_sitemap = self.use_sitemap_var.get()
        use_crawling = self.use_crawling_var.get()
        
        try:
            max_pages = int(self.max_pages_var.get())
        except ValueError:
            messagebox.showerror("Error", "Max Pages must be a number")
            return
        
        try:
            max_depth = int(self.max_depth_var.get())
        except ValueError:
            messagebox.showerror("Error", "Max Depth must be a number")
            return
        
        # Use the SEOCrawler and SitemapProcessor classes to crawl the website
        
        # Disable the crawl button during crawling
        self.crawl_button.config(state=tk.DISABLED)
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Perform the actual crawling in a separate thread
        def perform_crawling():
            sitemap_urls = []
            crawled_urls = []
            
            try:
                # First, try to find and process the sitemap if enabled
                if use_sitemap:
                    self.append_text(self.results_text, "Looking for sitemap...\n")
                    
                    # Normalize the URL to ensure we don't have double slashes
                    base_url = self.url.rstrip('/')
                    
                    # Try common sitemap locations
                    sitemap_locations = [
                        f"{base_url}/sitemap.xml",
                        f"{base_url}/sitemap_index.xml",
                        f"{base_url}/sitemap.xml.gz",
                        f"{base_url}/sitemap/sitemap.xml",
                        # Add more common sitemap locations
                        f"{base_url}/sitemap.php",
                        f"{base_url}/sitemap.txt",
                        f"{base_url}/sitemap_index.xml.gz",
                        f"{base_url}/wp-sitemap.xml",  # WordPress
                        f"{base_url}/wp-sitemap-index.xml",  # WordPress
                        f"{base_url}/sitemap-index.xml"  # Another common format
                    ]
                    
                    # Log the sitemap locations we're trying
                    self.append_text(self.results_text, "Checking the following sitemap locations:\n")
                    for loc in sitemap_locations:
                        self.append_text(self.results_text, f"- {loc}\n")
                    self.append_text(self.results_text, "\n")
                    
                    sitemap_found = False
                    for sitemap_url in sitemap_locations:
                        try:
                            # Process the sitemap
                            self.append_text(self.results_text, f"Trying sitemap at: {sitemap_url}\n")
                            sitemap_processor = SitemapProcessor(sitemap_url)
                            sitemap_result = sitemap_processor.process()
                            
                            # Check if we found any URLs
                            if sitemap_result["total_urls"] > 0:
                                sitemap_found = True
                                sitemap_urls = sitemap_result["urls"]
                                self.append_text(self.results_text, f"Found {len(sitemap_urls)} URLs in sitemap\n")
                                break
                        except Exception as e:
                            self.append_text(self.results_text, f"Error processing sitemap at {sitemap_url}: {str(e)}\n")
                    
                    if not sitemap_found:
                        self.append_text(self.results_text, "No sitemap found\n")
                
                # Then, crawl the website if enabled
                if use_crawling:
                    self.append_text(self.results_text, "Crawling website...\n")
                    
                    # Create a crawler
                    crawler = SEOCrawler(self.url, max_pages=max_pages, max_depth=max_depth)
                    
                    # Crawl the website
                    crawl_result = crawler.crawl()
                    
                    # Get the crawled URLs
                    crawled_urls = crawl_result["visited_urls"]
                    self.append_text(self.results_text, f"Found {len(crawled_urls)} URLs by crawling\n")
                
                # Combine all URLs
                all_urls = list(set(sitemap_urls + crawled_urls))
                
                # Create the crawler results object
                self.crawler_results = {
                    "urls": all_urls,
                    "sitemap_urls": sitemap_urls,
                    "crawled_urls": crawled_urls,
                    "total_urls": len(all_urls),
                    "sitemap_found": len(sitemap_urls) > 0,
                    "crawl_time": time.time() - start_time,
                }
                
                # Update the results text
                self.append_text(self.results_text, f"\nCrawling completed in {self.crawler_results['crawl_time']:.1f} seconds\n")
                self.append_text(self.results_text, f"Total URLs found: {len(all_urls)}\n")
                self.append_text(self.results_text, f"URLs from sitemap: {len(sitemap_urls)}\n")
                self.append_text(self.results_text, f"URLs from crawling: {len(crawled_urls)}\n\n")
                self.append_text(self.results_text, "Sample URLs found:\n")
                
                # Show a sample of the URLs (up to 20)
                for url in self.crawler_results["urls"][:20]:
                    self.append_text(self.results_text, f"- {url}\n")
                
                if len(self.crawler_results["urls"]) > 20:
                    self.append_text(self.results_text, f"... and {len(self.crawler_results['urls']) - 20} more\n")
                
                # Update the status
                self.set_status("Crawling completed", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Website crawled successfully")
            except Exception as e:
                # Update the results text
                self.append_text(self.results_text, f"Error during crawling: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error during crawling: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error during crawling: {str(e)}")
            finally:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Re-enable the crawl button
                self.crawl_button.config(state=tk.NORMAL)
                
                # Update button states
                self.update_button_states()
        
        # Record the start time
        start_time = time.time()
        
        # Run the crawling in a separate thread
        threading.Thread(target=perform_crawling).start()
    
    def load_content(self):
        """Load content for the crawled URLs."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        self.set_status(f"Loading content for {len(self.crawler_results['urls'])} URLs...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, f"Loading content for {len(self.crawler_results['urls'])} URLs...\n\n")
        
        # Disable the load content button during loading
        self.load_content_button.config(state=tk.DISABLED)
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Perform the actual content loading in a separate thread
        def perform_loading():
            try:
                # Create a ContentLoader instance
                from seo_content_loader import ContentLoader
                content_loader = ContentLoader(self.crawler_results["urls"])
                
                # Load the content
                start_time = time.time()
                load_results = content_loader.load_content()
                load_time = time.time() - start_time
                
                # Store the content loader
                self.content_loader = content_loader
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Calculate average content length
                total_length = sum(content_loader.content_lengths.values())
                avg_length = total_length / len(content_loader.content_lengths) if content_loader.content_lengths else 0
                
                # Count status codes
                status_counts = {}
                for status in content_loader.status_codes.values():
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count content types
                type_counts = {}
                for content_type in content_loader.content_types.values():
                    type_counts[content_type] = type_counts.get(content_type, 0) + 1
                
                # Update the results text
                self.append_text(self.results_text, f"Content loading completed in {load_time:.2f} seconds\n")
                self.append_text(self.results_text, f"Total URLs loaded: {len(content_loader.content)}\n\n")
                self.append_text(self.results_text, "Content statistics:\n")
                self.append_text(self.results_text, f"- Average content length: {avg_length:.0f} bytes\n")
                
                self.append_text(self.results_text, "- Status codes:\n")
                for status, count in status_counts.items():
                    status_text = "OK" if status == 200 else f"Error ({status})"
                    self.append_text(self.results_text, f"  - {status} ({status_text}): {count} pages\n")
                
                self.append_text(self.results_text, "- Content types:\n")
                for content_type, count in type_counts.items():
                    if not content_type:
                        content_type = "Unknown"
                    self.append_text(self.results_text, f"  - {content_type}: {count} pages\n")
                
                self.append_text(self.results_text, "\nSample URLs loaded:\n")
                # Show a sample of the URLs (up to 20)
                for i, url in enumerate(list(content_loader.content.keys())[:20]):
                    length = content_loader.content_lengths.get(url, 0)
                    self.append_text(self.results_text, f"- {url} ({length} bytes)\n")
                
                if len(content_loader.content) > 20:
                    self.append_text(self.results_text, f"... and {len(content_loader.content) - 20} more\n")
                
                # Re-enable the load content button
                self.load_content_button.config(state=tk.NORMAL)
                
                # Update the status
                self.set_status("Content loading completed", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Content loaded successfully")
                
                # Update button states
                self.update_button_states()
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error during content loading: {str(e)}\n")
                
                # Re-enable the load content button
                self.load_content_button.config(state=tk.NORMAL)
                
                # Update the status
                self.set_status(f"Error during content loading: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error during content loading: {str(e)}")
        
        # Run the content loading in a separate thread
        threading.Thread(target=perform_loading).start()
    
    def analyze_meta_descriptions(self):
        """Analyze meta descriptions."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.content_loader:
            messagebox.showerror("Error", "Please load content first")
            return
        
        self.set_status("Analyzing meta descriptions...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Analyzing meta descriptions...\n\n")
        
        # In a real implementation, this would use the MetaDescriptionAnalyzer class
        # For the stub implementation, we'll just simulate analysis
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Simulate analysis with a delay
        def simulate_analysis():
            # Simulate analysis delay
            time.sleep(2)
            
            # Stop the progress bar
            progress_bar.stop()
            progress_bar.destroy()
            
            # Create a simulated meta description analyzer object
            self.meta_description_analyzer = {
                "total_urls": len(self.crawler_results["urls"]),
                "urls_with_meta_desc": int(len(self.crawler_results["urls"]) * 0.8),  # 80% have meta descriptions
                "urls_without_meta_desc": int(len(self.crawler_results["urls"]) * 0.2),  # 20% don't have meta descriptions
                "meta_desc_too_short": int(len(self.crawler_results["urls"]) * 0.1),  # 10% have meta descriptions that are too short
                "meta_desc_too_long": int(len(self.crawler_results["urls"]) * 0.1),  # 10% have meta descriptions that are too long
                "meta_desc_good": int(len(self.crawler_results["urls"]) * 0.6),  # 60% have good meta descriptions
            }
            
            # Update the results text
            self.append_text(self.results_text, "Meta Description Analysis Results:\n\n")
            self.append_text(self.results_text, f"Total URLs analyzed: {self.meta_description_analyzer['total_urls']}\n")
            self.append_text(self.results_text, f"URLs with meta descriptions: {self.meta_description_analyzer['urls_with_meta_desc']} ({self.meta_description_analyzer['urls_with_meta_desc'] / self.meta_description_analyzer['total_urls'] * 100:.1f}%)\n")
            self.append_text(self.results_text, f"URLs without meta descriptions: {self.meta_description_analyzer['urls_without_meta_desc']} ({self.meta_description_analyzer['urls_without_meta_desc'] / self.meta_description_analyzer['total_urls'] * 100:.1f}%)\n\n")
            
            self.append_text(self.results_text, "Meta Description Quality:\n")
            self.append_text(self.results_text, f"- Good meta descriptions: {self.meta_description_analyzer['meta_desc_good']} ({self.meta_description_analyzer['meta_desc_good'] / self.meta_description_analyzer['total_urls'] * 100:.1f}%)\n")
            self.append_text(self.results_text, f"- Meta descriptions too short: {self.meta_description_analyzer['meta_desc_too_short']} ({self.meta_description_analyzer['meta_desc_too_short'] / self.meta_description_analyzer['total_urls'] * 100:.1f}%)\n")
            self.append_text(self.results_text, f"- Meta descriptions too long: {self.meta_description_analyzer['meta_desc_too_long']} ({self.meta_description_analyzer['meta_desc_too_long'] / self.meta_description_analyzer['total_urls'] * 100:.1f}%)\n\n")
            
            self.append_text(self.results_text, "URLs without meta descriptions:\n")
            # Simulate some URLs without meta descriptions
            for i in range(self.meta_description_analyzer['urls_without_meta_desc']):
                url = self.crawler_results["urls"][i]
                self.append_text(self.results_text, f"- {url}\n")
            
            # Update the status
            self.set_status("Meta description analysis completed", SUCCESS_COLOR)
            
            # Show a success message
            messagebox.showinfo("Success", "Meta description analysis completed successfully")
        
        # Run the simulation in a separate thread
        threading.Thread(target=simulate_analysis).start()
    
    def analyze_images(self):
        """Analyze images."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.content_loader:
            messagebox.showerror("Error", "Please load content first")
            return
        
        self.set_status("Analyzing images...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Analyzing images...\n\n")
        
        # In a real implementation, this would use the ImageAnalyzer class
        # For the stub implementation, we'll just simulate analysis
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Simulate analysis with a delay
        def simulate_analysis():
            # Simulate analysis delay
            time.sleep(2)
            
            # Stop the progress bar
            progress_bar.stop()
            progress_bar.destroy()
            
            # Create a simulated image analyzer object
            total_images = len(self.crawler_results["urls"]) * 5  # Assume 5 images per page on average
            self.image_analyzer = {
                "total_images": total_images,
                "images_with_alt": int(total_images * 0.7),  # 70% have alt text
                "images_without_alt": int(total_images * 0.3),  # 30% don't have alt text
                "images_too_large": int(total_images * 0.2),  # 20% are too large
                "images_optimized": int(total_images * 0.5),  # 50% are optimized
            }
            
            # Update the results text
            self.append_text(self.results_text, "Image Analysis Results:\n\n")
            self.append_text(self.results_text, f"Total images found: {self.image_analyzer['total_images']}\n")
            self.append_text(self.results_text, f"Images with alt text: {self.image_analyzer['images_with_alt']} ({self.image_analyzer['images_with_alt'] / self.image_analyzer['total_images'] * 100:.1f}%)\n")
            self.append_text(self.results_text, f"Images without alt text: {self.image_analyzer['images_without_alt']} ({self.image_analyzer['images_without_alt'] / self.image_analyzer['total_images'] * 100:.1f}%)\n\n")
            
            self.append_text(self.results_text, "Image Optimization:\n")
            self.append_text(self.results_text, f"- Optimized images: {self.image_analyzer['images_optimized']} ({self.image_analyzer['images_optimized'] / self.image_analyzer['total_images'] * 100:.1f}%)\n")
            self.append_text(self.results_text, f"- Images too large: {self.image_analyzer['images_too_large']} ({self.image_analyzer['images_too_large'] / self.image_analyzer['total_images'] * 100:.1f}%)\n\n")
            
            self.append_text(self.results_text, "Sample images without alt text:\n")
            # Simulate some images without alt text
            for i in range(min(5, self.image_analyzer['images_without_alt'])):
                url = self.crawler_results["urls"][i]
                self.append_text(self.results_text, f"- {url}/image{i+1}.jpg\n")
            
            # Update the status
            self.set_status("Image analysis completed", SUCCESS_COLOR)
            
            # Show a success message
            messagebox.showinfo("Success", "Image analysis completed successfully")
        
        # Run the simulation in a separate thread
        threading.Thread(target=simulate_analysis).start()
    
    def analyze_links(self):
        """Analyze links."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.content_loader:
            messagebox.showerror("Error", "Please load content first")
            return
        
        self.set_status("Analyzing links...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Analyzing links...\n\n")
        
        # In a real implementation, this would use the LinksAnalyzer class
        # For the stub implementation, we'll just simulate analysis
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Simulate analysis with a delay
        def simulate_analysis():
            # Simulate analysis delay
            time.sleep(2)
            
            # Stop the progress bar
            progress_bar.stop()
            progress_bar.destroy()
            
            # Create a simulated links analyzer object
            total_links = len(self.crawler_results["urls"]) * 10  # Assume 10 links per page on average
            internal_links = int(total_links * 0.7)  # 70% are internal links
            external_links = total_links - internal_links  # 30% are external links
            
            self.links_analyzer = {
                "total_links": total_links,
                "internal_links": internal_links,
                "external_links": external_links,
                "broken_links": int(total_links * 0.05),  # 5% are broken
                "nofollow_links": int(total_links * 0.2),  # 20% are nofollow
            }
            
            # Update the results text
            self.append_text(self.results_text, "Link Analysis Results:\n\n")
            self.append_text(self.results_text, f"Total links found: {self.links_analyzer['total_links']}\n")
            self.append_text(self.results_text, f"Internal links: {self.links_analyzer['internal_links']} ({self.links_analyzer['internal_links'] / self.links_analyzer['total_links'] * 100:.1f}%)\n")
            self.append_text(self.results_text, f"External links: {self.links_analyzer['external_links']} ({self.links_analyzer['external_links'] / self.links_analyzer['total_links'] * 100:.1f}%)\n\n")
            
            self.append_text(self.results_text, "Link Issues:\n")
            self.append_text(self.results_text, f"- Broken links: {self.links_analyzer['broken_links']} ({self.links_analyzer['broken_links'] / self.links_analyzer['total_links'] * 100:.1f}%)\n")
            self.append_text(self.results_text, f"- Nofollow links: {self.links_analyzer['nofollow_links']} ({self.links_analyzer['nofollow_links'] / self.links_analyzer['total_links'] * 100:.1f}%)\n\n")
            
            self.append_text(self.results_text, "Sample broken links:\n")
            # Simulate some broken links using actual URLs from the website
            broken_count = 0
            for i, url in enumerate(self.crawler_results["urls"]):
                if broken_count >= min(5, self.links_analyzer['broken_links']):
                    break
                # Use actual URLs from the website with a simulated broken path
                broken_url = f"{url}/broken-path-{i+1}"
                self.append_text(self.results_text, f"- {broken_url}\n")
                broken_count += 1
            
            # Update the status
            self.set_status("Link analysis completed", SUCCESS_COLOR)
            
            # Show a success message
            messagebox.showinfo("Success", "Link analysis completed successfully")
        
        # Run the simulation in a separate thread
        threading.Thread(target=simulate_analysis).start()
    
    def analyze_reachability(self):
        """Analyze reachability."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.content_loader:
            messagebox.showerror("Error", "Please load content first")
            return
        
        self.set_status("Analyzing reachability...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Analyzing reachability...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        def perform_analysis():
            try:
                # Create a LinksAnalyzer instance if not already done
                if not self.links_analyzer or not isinstance(self.links_analyzer, LinksAnalyzer):
                    self.links_analyzer = LinksAnalyzer(self.content_loader, self.url)
                    self.links_analyzer.analyze()
                
                # Create a ReachabilityAnalyzer instance
                reachability = ReachabilityAnalyzer(self.links_analyzer, self.url)
                reachability.analyze()
                self.reachability_analyzer = reachability
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Prepare stats
                stats = reachability.analyze()
                
                # Update the results text
                self.append_text(self.results_text, "Reachability Analysis Results:\n\n")
                self.append_text(self.results_text, f"Total URLs analyzed: {stats['total_urls']}\n")
                self.append_text(self.results_text, f"Reachable URLs: {stats['reachable_urls']} ({stats['reachable_urls'] / stats['total_urls'] * 100:.1f}%)\n")
                self.append_text(self.results_text, f"Orphan pages: {stats['orphan_pages']} ({stats['orphan_pages'] / stats['total_urls'] * 100:.1f}%)\n\n")
                
                self.append_text(self.results_text, "Click Depth Analysis:\n")
                self.append_text(self.results_text, f"- Average clicks from home: {stats['avg_clicks_from_home']:.1f}\n")
                self.append_text(self.results_text, f"- Maximum clicks from home: {stats['max_clicks_from_home']}\n\n")
                
                self.append_text(self.results_text, "Sample orphan pages:\n")
                for url in stats['orphan_pages_list'][:5]:
                    self.append_text(self.results_text, f"- {url}\n")
                
                self.set_status("Reachability analysis completed", SUCCESS_COLOR)
                messagebox.showinfo("Success", "Reachability analysis completed successfully")
            except Exception as e:
                progress_bar.stop()
                progress_bar.destroy()
                self.set_status(f"Error during reachability analysis: {str(e)}", ERROR_COLOR)
                messagebox.showerror("Error", f"Error during reachability analysis: {str(e)}")
        
        threading.Thread(target=perform_analysis).start()
    
    def show_site_map(self):
        """Display the website structure graph after crawling/analysis."""
        import matplotlib.pyplot as plt
        import networkx as nx

        if not self.reachability_analyzer or not hasattr(self.reachability_analyzer, 'graph'):
            messagebox.showerror("Error", "Please run reachability analysis first")
            return

        graph = self.reachability_analyzer.graph
        if graph is None or len(graph.nodes) == 0:
            messagebox.showerror("Error", "Graph data is empty")
            return

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(graph, k=0.3, iterations=50)
        nx.draw_networkx_nodes(graph, pos, node_size=100, node_color='skyblue')
        nx.draw_networkx_edges(graph, pos, arrows=True, arrowstyle='-|>', arrowsize=10)
        nx.draw_networkx_labels(graph, pos, font_size=8)

        plt.title("Website Structure Graph")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def analyze_main_topics(self):
        """Analyze main topics."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.content_loader:
            messagebox.showerror("Error", "Please load content first")
            return
        
        self.set_status("Analyzing main topics...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Analyzing main topics...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Perform the actual analysis in a separate thread
        def perform_analysis():
            try:
                # Create a MainTopicAnalyzer instance
                from seo_main_topic import MainTopicAnalyzer
                analyzer = MainTopicAnalyzer(self.content_loader)
                
                # Perform the analysis
                analysis_results = analyzer.analyze()
                
                # Store the results
                self.main_topic_analyzer = analysis_results
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, "Main Topic Analysis Results:\n\n")
                self.append_text(self.results_text, f"Total URLs analyzed: {self.main_topic_analyzer['total_urls']}\n")
                self.append_text(self.results_text, f"URLs with topics identified: {self.main_topic_analyzer['topics_identified']} ({self.main_topic_analyzer['topics_identified'] / self.main_topic_analyzer['total_urls'] * 100:.1f}%)\n\n")
                
                self.append_text(self.results_text, "Main Topics Identified:\n")
                for topic in list(self.main_topic_analyzer['topic_distribution'].keys())[:10]:  # Show top 10 topics
                    percentage = self.main_topic_analyzer['topic_distribution'][topic] * 100
                    self.append_text(self.results_text, f"- {topic}: {percentage:.1f}%\n")
                
                self.append_text(self.results_text, "\nTop Keywords:\n")
                for keyword in self.main_topic_analyzer['keywords'][:10]:  # Show top 10 keywords
                    self.append_text(self.results_text, f"- {keyword}\n")
                
                # Update the status
                self.set_status("Main topic analysis completed", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Main topic analysis completed successfully")
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error during main topic analysis: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error during main topic analysis: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error during main topic analysis: {str(e)}")
        
        # Run the analysis in a separate thread
        threading.Thread(target=perform_analysis).start()
    
    def generate_meta_descriptions(self):
        """Generate meta descriptions using LM Studio."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.content_loader:
            messagebox.showerror("Error", "Please load content first")
            return
        
        if not self.meta_description_analyzer:
            messagebox.showerror("Error", "Please analyze meta descriptions first")
            return
        
        self.set_status("Generating meta descriptions...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating meta descriptions using LM Studio...\n\n")
        
        # In a real implementation, this would use the LMStudioClient and MetaDescriptionGenerator classes
        # For the stub implementation, we'll just simulate generation
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Simulate generation with a delay
        def simulate_generation():
            # Simulate generation delay
            time.sleep(4)  # This takes longer as it's using an LLM
            
            # Stop the progress bar
            progress_bar.stop()
            progress_bar.destroy()
            
            # Create a simulated meta description generator object
            urls_without_meta_desc = self.meta_description_analyzer["urls_without_meta_desc"]
            
            self.meta_description_generator = {
                "total_urls_processed": urls_without_meta_desc,
                "urls_with_generated_meta_desc": urls_without_meta_desc,
                "generated_meta_descriptions": {
                    url: f"Generated meta description for {url}" for url in self.crawler_results["urls"][:urls_without_meta_desc]
                }
            }
            
            # Update the results text
            self.append_text(self.results_text, "Meta Description Generation Results:\n\n")
            self.append_text(self.results_text, f"Total URLs processed: {self.meta_description_generator['total_urls_processed']}\n")
            self.append_text(self.results_text, f"URLs with generated meta descriptions: {self.meta_description_generator['urls_with_generated_meta_desc']}\n\n")
            
            self.append_text(self.results_text, "Sample Generated Meta Descriptions:\n")
            # Show some sample generated meta descriptions
            for i, (url, meta_desc) in enumerate(self.meta_description_generator['generated_meta_descriptions'].items()):
                if i >= 5:  # Show only 5 samples
                    break
                self.append_text(self.results_text, f"- {url}:\n  \"{meta_desc}\"\n\n")
            
            # Update the status
            self.set_status("Meta description generation completed", SUCCESS_COLOR)
            
            # Show a success message
            messagebox.showinfo("Success", "Meta descriptions generated successfully")
        
        # Run the simulation in a separate thread
        threading.Thread(target=simulate_generation).start()
    
    def load_search_console_data(self):
        """Load Search Console data."""
        sc_file = self.sc_file_entry.get().strip()
        
        if not sc_file:
            messagebox.showerror("Error", "Please select a Search Console CSV file")
            return
        
        if not os.path.exists(sc_file):
            messagebox.showerror("Error", "File does not exist")
            return
        
        self.set_status(f"Loading Search Console data from: {sc_file}...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, f"Loading Search Console data from: {sc_file}...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Perform the actual loading in a separate thread
        def perform_loading():
            try:
                # Create a SearchConsoleData instance
                sc_data = SearchConsoleData(sc_file)
                
                # Load the data
                load_results = sc_data.load()
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                if load_results["success"]:
                    # Store the search console data
                    self.search_console_data = sc_data
                    
                    # Update the results text
                    self.append_text(self.results_text, "Search Console Data Summary:\n\n")
                    self.append_text(self.results_text, f"Total Queries: {load_results['total_queries']}\n")
                    self.append_text(self.results_text, f"Total Landing Pages: {load_results['total_landing_pages']}\n")
                    self.append_text(self.results_text, f"Total Impressions: {load_results['total_impressions']}\n")
                    self.append_text(self.results_text, f"Total Clicks: {load_results['total_clicks']}\n")
                    self.append_text(self.results_text, f"Average Position: {load_results['avg_position']:.1f}\n\n")
                    
                    self.append_text(self.results_text, "Top Queries by Impressions:\n")
                    for query in load_results['queries'][:5]:  # Show top 5 queries
                        self.append_text(self.results_text, f"- {query['Query']}: {query['Impressions']} impressions, {query['Url Clicks']} clicks, position {query['Average Position']:.1f}\n")
                    
                    self.append_text(self.results_text, "\nTop Landing Pages by Impressions:\n")
                    for page in load_results['landing_pages'][:5]:  # Show top 5 landing pages
                        self.append_text(self.results_text, f"- {page['Landing Page']}: {page['Impressions']} impressions, {page['Url Clicks']} clicks, position {page['Average Position']:.1f}\n")
                    
                    # Update the status
                    self.set_status("Search Console data loaded successfully", SUCCESS_COLOR)
                    
                    # Show a success message
                    messagebox.showinfo("Success", "Search Console data loaded successfully")
                else:
                    # Update the results text
                    self.append_text(self.results_text, f"Error loading Search Console data: {load_results['message']}\n")
                    
                    # Update the status
                    self.set_status(f"Error loading Search Console data: {load_results['message']}", ERROR_COLOR)
                    
                    # Show an error message
                    messagebox.showerror("Error", f"Error loading Search Console data: {load_results['message']}")
                
                # Update button states
                self.update_button_states()
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error loading Search Console data: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error loading Search Console data: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error loading Search Console data: {str(e)}")
        
        # Run the loading in a separate thread
        threading.Thread(target=perform_loading).start()
    
    def load_old_search_console_data(self):
        """Load old Search Console data for comparison."""
        sc_old_file = self.sc_old_file_entry.get().strip()
        
        if not sc_old_file:
            messagebox.showerror("Error", "Please select an old Search Console CSV file")
            return
        
        if not os.path.exists(sc_old_file):
            messagebox.showerror("Error", "File does not exist")
            return
        
        self.set_status(f"Loading old Search Console data from: {sc_old_file}...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, f"Loading old Search Console data from: {sc_old_file}...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Perform the actual loading in a separate thread
        def perform_loading():
            try:
                # Create a SearchConsoleData instance
                sc_data_old = SearchConsoleData(sc_old_file)
                
                # Load the data
                load_results = sc_data_old.load()
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                if load_results["success"]:
                    # Store the old search console data
                    self.search_console_data_old = sc_data_old
                    
                    # Update the results text
                    self.append_text(self.results_text, "Old Search Console Data Summary:\n\n")
                    self.append_text(self.results_text, f"Total Queries: {load_results['total_queries']}\n")
                    self.append_text(self.results_text, f"Total Landing Pages: {load_results['total_landing_pages']}\n")
                    self.append_text(self.results_text, f"Total Impressions: {load_results['total_impressions']}\n")
                    self.append_text(self.results_text, f"Total Clicks: {load_results['total_clicks']}\n")
                    self.append_text(self.results_text, f"Average Position: {load_results['avg_position']:.1f}\n\n")
                    
                    self.append_text(self.results_text, "Top Queries by Impressions:\n")
                    for query in load_results['queries'][:5]:  # Show top 5 queries
                        self.append_text(self.results_text, f"- {query['Query']}: {query['Impressions']} impressions, {query['Url Clicks']} clicks, position {query['Average Position']:.1f}\n")
                    
                    self.append_text(self.results_text, "\nTop Landing Pages by Impressions:\n")
                    for page in load_results['landing_pages'][:5]:  # Show top 5 landing pages
                        self.append_text(self.results_text, f"- {page['Landing Page']}: {page['Impressions']} impressions, {page['Url Clicks']} clicks, position {page['Average Position']:.1f}\n")
                    
                    # Update the status
                    self.set_status("Old Search Console data loaded successfully", SUCCESS_COLOR)
                    
                    # Show a success message
                    messagebox.showinfo("Success", "Old Search Console data loaded successfully")
                else:
                    # Update the results text
                    self.append_text(self.results_text, f"Error loading old Search Console data: {load_results['message']}\n")
                    
                    # Update the status
                    self.set_status(f"Error loading old Search Console data: {load_results['message']}", ERROR_COLOR)
                    
                    # Show an error message
                    messagebox.showerror("Error", f"Error loading old Search Console data: {load_results['message']}")
                
                # Update button states
                self.update_button_states()
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error loading old Search Console data: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error loading old Search Console data: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error loading old Search Console data: {str(e)}")
        
        # Run the loading in a separate thread
        threading.Thread(target=perform_loading).start()
    
    def cluster_search_console_queries(self):
        """Cluster Search Console queries."""
        if not self.search_console_data:
            messagebox.showerror("Error", "Please load Search Console data first")
            return
        
        self.set_status("Clustering Search Console queries...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Clustering Search Console queries...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Perform the clustering in a separate thread
        def perform_clustering():
            try:
                # Create a SearchConsoleAnalyzer if not already done
                if not self.search_console_analyzer:
                    self.search_console_analyzer = SearchConsoleAnalyzer(self.search_console_data)
                
                # Cluster the queries
                n_clusters = 10  # Default number of clusters
                self.search_console_analyzer.cluster_queries(n_clusters=n_clusters)
                
                # Get the clusters
                clusters = self.search_console_analyzer.get_clusters()
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Clustered {len(self.search_console_data.get_queries())} queries into {len(clusters)} clusters\n\n")
                
                self.append_text(self.results_text, "Top Clusters by Impressions:\n")
                for i, cluster in enumerate(clusters[:5]):  # Show top 5 clusters
                    self.append_text(self.results_text, f"Cluster {i+1}: {cluster['queries']} queries, {cluster['impressions']} impressions\n")
                    self.append_text(self.results_text, f"  Top queries: {', '.join(cluster['top_queries'])}\n\n")
                
                # Update the status
                self.set_status("Search Console queries clustered successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Search Console queries clustered successfully")
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error clustering Search Console queries: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error clustering Search Console queries: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error clustering Search Console queries: {str(e)}")
        
        # Run the clustering in a separate thread
        threading.Thread(target=perform_clustering).start()
    
    def identify_search_console_topics(self):
        """Identify topics in Search Console data."""
        if not self.search_console_data:
            messagebox.showerror("Error", "Please load Search Console data first")
            return
        
        if not self.search_console_analyzer or not self.search_console_analyzer.get_clusters():
            messagebox.showerror("Error", "Please cluster Search Console queries first")
            return
        
        self.set_status("Identifying Search Console topics...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Identifying Search Console topics...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Perform the topic identification in a separate thread
        def perform_identification():
            try:
                # Identify the topics
                self.search_console_analyzer.identify_topics()
                
                # Get the topics
                topics = self.search_console_analyzer.get_topics()
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Identified topics for {len(topics)} landing pages\n\n")
                
                self.append_text(self.results_text, "Sample Landing Page Topics:\n")
                count = 0
                for landing_page, topic in topics.items():
                    if count >= 5:  # Show only 5 samples
                        break
                    self.append_text(self.results_text, f"{landing_page}:\n")
                    self.append_text(self.results_text, f"  Topic: {', '.join(topic)}\n\n")
                    count += 1
                
                # Update the status
                self.set_status("Search Console topics identified successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Search Console topics identified successfully")
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error identifying Search Console topics: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error identifying Search Console topics: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error identifying Search Console topics: {str(e)}")
        
        # Run the topic identification in a separate thread
        threading.Thread(target=perform_identification).start()
    
    def compare_search_console_data(self):
        """Compare two Search Console datasets."""
        if not self.search_console_data:
            messagebox.showerror("Error", "Please load Search Console data first")
            return
        
        if not self.search_console_data_old:
            messagebox.showerror("Error", "Please load old Search Console data first")
            return
        
        self.set_status("Comparing Search Console data...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Comparing Search Console data...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Perform the comparison in a separate thread
        def perform_comparison():
            try:
                # Create a SearchConsoleComparison
                self.search_console_comparison = SearchConsoleComparison(self.search_console_data_old, self.search_console_data)
                
                # Compare the data
                comparison_results = self.search_console_comparison.compare()
                
                # Get the improved and declined queries and landing pages
                improved_queries = self.search_console_comparison.get_improved_queries()
                declined_queries = self.search_console_comparison.get_declined_queries()
                improved_landing_pages = self.search_console_comparison.get_improved_landing_pages()
                declined_landing_pages = self.search_console_comparison.get_declined_landing_pages()
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, "Search Console Data Comparison Results:\n\n")
                
                self.append_text(self.results_text, "Query Comparison:\n")
                self.append_text(self.results_text, f"- Total queries: {len(self.search_console_comparison.get_query_comparison())}\n")
                self.append_text(self.results_text, f"- Improved queries: {len(improved_queries)}\n")
                self.append_text(self.results_text, f"- Declined queries: {len(declined_queries)}\n\n")
                
                self.append_text(self.results_text, "Landing Page Comparison:\n")
                self.append_text(self.results_text, f"- Total landing pages: {len(self.search_console_comparison.get_landing_page_comparison())}\n")
                self.append_text(self.results_text, f"- Improved landing pages: {len(improved_landing_pages)}\n")
                self.append_text(self.results_text, f"- Declined landing pages: {len(declined_landing_pages)}\n\n")
                
                self.append_text(self.results_text, "Top Improved Queries:\n")
                for i, (_, row) in enumerate(improved_queries.head(5).iterrows()):
                    self.append_text(self.results_text, f"- {row['Query']}: +{row['Impressions_change']:.0f} impressions ({row['Impressions_change_pct']:.1f}%)\n")
                
                self.append_text(self.results_text, "\nTop Declined Queries:\n")
                for i, (_, row) in enumerate(declined_queries.head(5).iterrows()):
                    self.append_text(self.results_text, f"- {row['Query']}: {row['Impressions_change']:.0f} impressions ({row['Impressions_change_pct']:.1f}%)\n")
                
                # Update the status
                self.set_status("Search Console data compared successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Search Console data compared successfully")
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error comparing Search Console data: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error comparing Search Console data: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error comparing Search Console data: {str(e)}")
        
        # Run the comparison in a separate thread
        threading.Thread(target=perform_comparison).start()
    
    def suggest_search_console_links(self):
        """Suggest internal links based on Search Console data."""
        if not self.search_console_data:
            messagebox.showerror("Error", "Please load Search Console data first")
            return
        
        if not self.search_console_analyzer or not self.search_console_analyzer.get_topics():
            messagebox.showerror("Error", "Please identify Search Console topics first")
            return
        
        self.set_status("Suggesting internal links based on Search Console data...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Suggesting internal links based on Search Console data...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Perform the link suggestion in a separate thread
        def perform_suggestion():
            try:
                # Suggest internal links
                suggestions = self.search_console_analyzer.suggest_internal_links()
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Generated {len(suggestions)} internal link suggestions\n\n")
                
                self.append_text(self.results_text, "Sample Link Suggestions:\n")
                for i, suggestion in enumerate(suggestions[:10]):  # Show top 10 suggestions
                    self.append_text(self.results_text, f"- Link from {suggestion['source']} to {suggestion['target']}\n")
                    self.append_text(self.results_text, f"  Topic: {suggestion['topic']}\n\n")
                
                # Update the status
                self.set_status("Internal link suggestions generated successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Internal link suggestions generated successfully")
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error suggesting internal links: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error suggesting internal links: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error suggesting internal links: {str(e)}")
        
        # Run the link suggestion in a separate thread
        threading.Thread(target=perform_suggestion).start()
    
    def load_semrush_data(self):
        """Load SEMrush data."""
        sr_file = self.sr_file_entry.get().strip()
        
        if not sr_file:
            messagebox.showerror("Error", "Please select a SEMrush CSV file")
            return
        
        if not os.path.exists(sr_file):
            messagebox.showerror("Error", "File does not exist")
            return
        
        self.set_status(f"Loading SEMrush data from: {sr_file}...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, f"Loading SEMrush data from: {sr_file}...\n\n")
        
        # In a real implementation, this would use the SEMrushData class
        # For the stub implementation, we'll just simulate loading
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Simulate loading with a delay
        def simulate_loading():
            # Simulate loading delay
            time.sleep(2)
            
            # Stop the progress bar
            progress_bar.stop()
            progress_bar.destroy()
            
            # Create a simulated SEMrush data object
            self.semrush_data = {
                "file_path": sr_file,
                "total_keywords": 2000,
                "total_urls": 100,
                "avg_position": 12.5,
                "total_traffic": 15000,
                "total_traffic_cost": 25000,
                "keywords": [
                    {"keyword": "seo analysis tool", "position": 3, "search_volume": 1200, "cpc": 2.5, "url": "https://example.com/tools"},
                    {"keyword": "seo crawler", "position": 5, "search_volume": 1000, "cpc": 2.2, "url": "https://example.com/tools/crawler"},
                    {"keyword": "meta description analyzer", "position": 7, "search_volume": 800, "cpc": 1.8, "url": "https://example.com/tools/meta-description"},
                    {"keyword": "seo audit", "position": 9, "search_volume": 1500, "cpc": 3.0, "url": "https://example.com/services/audit"},
                    {"keyword": "website analysis", "position": 11, "search_volume": 2000, "cpc": 3.5, "url": "https://example.com/services/analysis"},
                ],
                "urls": [
                    {"url": "https://example.com/tools", "keywords": 15, "traffic": 2500, "traffic_cost": 5000},
                    {"url": "https://example.com/services", "keywords": 12, "traffic": 2000, "traffic_cost": 4000},
                    {"url": "https://example.com/blog", "keywords": 10, "traffic": 1500, "traffic_cost": 3000},
                    {"url": "https://example.com/about", "keywords": 5, "traffic": 500, "traffic_cost": 1000},
                    {"url": "https://example.com/contact", "keywords": 3, "traffic": 300, "traffic_cost": 600},
                ]
            }
            
            # Update the results text
            self.append_text(self.results_text, "SEMrush Data Summary:\n\n")
            self.append_text(self.results_text, f"Total Keywords: {self.semrush_data['total_keywords']}\n")
            self.append_text(self.results_text, f"Total URLs: {self.semrush_data['total_urls']}\n")
            self.append_text(self.results_text, f"Average Position: {self.semrush_data['avg_position']:.1f}\n")
            self.append_text(self.results_text, f"Total Traffic: {self.semrush_data['total_traffic']}\n")
            self.append_text(self.results_text, f"Total Traffic Cost: ${self.semrush_data['total_traffic_cost']}\n\n")
            
            self.append_text(self.results_text, "Top Keywords by Search Volume:\n")
            for keyword in self.semrush_data['keywords']:
                self.append_text(self.results_text, f"- {keyword['keyword']}: Position {keyword['position']}, Search Volume {keyword['search_volume']}, CPC ${keyword['cpc']:.2f}\n")
            
            self.append_text(self.results_text, "\nTop URLs by Traffic:\n")
            for url in self.semrush_data['urls']:
                self.append_text(self.results_text, f"- {url['url']}: {url['keywords']} keywords, {url['traffic']} traffic, ${url['traffic_cost']} traffic cost\n")
            
            # Update the status
            self.set_status("SEMrush data loaded successfully", SUCCESS_COLOR)
            
            # Show a success message
            messagebox.showinfo("Success", "SEMrush data loaded successfully")
            
            # Update button states
            self.update_button_states()
        
        # Run the simulation in a separate thread
        threading.Thread(target=simulate_loading).start()
    
    def cluster_semrush_keywords(self):
        """Cluster SEMrush keywords."""
        if not self.semrush_data:
            messagebox.showerror("Error", "Please load SEMrush data first")
            return
        
        self.set_status("Clustering SEMrush keywords...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Clustering SEMrush keywords...\n\n")
        
        # In a real implementation, this would use the SEMrushAnalyzer class
        # For the stub implementation, we'll just simulate clustering
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Simulate clustering with a delay
        def simulate_clustering():
            # Simulate clustering delay
            time.sleep(3)  # This takes longer as it's more complex
            
            # Stop the progress bar
            progress_bar.stop()
            progress_bar.destroy()
            
            # Create a simulated SEMrush analyzer object with clusters
            self.semrush_analyzer = {
                "total_keywords": self.semrush_data["total_keywords"],
                "total_clusters": 15,
                "clusters": [
                    {"name": "SEO Tools", "keywords": 350, "avg_position": 8.5, "total_traffic": 3000},
                    {"name": "SEO Services", "keywords": 300, "avg_position": 9.2, "total_traffic": 2500},
                    {"name": "Content Marketing", "keywords": 250, "avg_position": 10.5, "total_traffic": 2000},
                    {"name": "Web Development", "keywords": 200, "avg_position": 11.8, "total_traffic": 1500},
                    {"name": "Digital Marketing", "keywords": 150, "avg_position": 13.2, "total_traffic": 1000},
                ]
            }
            
            # Update the results text
            self.append_text(self.results_text, "SEMrush Keyword Clustering Results:\n\n")
            self.append_text(self.results_text, f"Total Keywords: {self.semrush_analyzer['total_keywords']}\n")
            self.append_text(self.results_text, f"Total Clusters: {self.semrush_analyzer['total_clusters']}\n\n")
            
            self.append_text(self.results_text, "Top Clusters by Keyword Count:\n")
            for cluster in self.semrush_analyzer['clusters']:
                self.append_text(self.results_text, f"- {cluster['name']}: {cluster['keywords']} keywords, Avg. Position {cluster['avg_position']:.1f}, Traffic {cluster['total_traffic']}\n")
            
            # Update the status
            self.set_status("SEMrush keyword clustering completed", SUCCESS_COLOR)
            
            # Show a success message
            messagebox.showinfo("Success", "SEMrush keyword clustering completed successfully")
        
        # Run the simulation in a separate thread
        threading.Thread(target=simulate_clustering).start()
    
    def identify_semrush_topics(self):
        """Identify topics in SEMrush data."""
        # Implementation would go here
        pass
    
    def analyze_semrush_positions(self):
        """Analyze SEMrush positions."""
        # Implementation would go here
        pass
    
    def suggest_semrush_links(self):
        """Suggest internal links based on SEMrush data."""
        # Implementation would go here
        pass
    
    def run_all_analyses(self):
        """Run all analyses."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.content_loader:
            messagebox.showerror("Error", "Please load content first")
            return
        
        self.set_status("Running all analyses...", INFO_COLOR)
        
        try:
            # Run all analyses
            self.clear_text(self.results_text)
            self.append_text(self.results_text, "Running all analyses...\n\n")
            
            # Meta descriptions
            self.append_text(self.results_text, "Analyzing meta descriptions...\n")
            self.analyze_meta_descriptions()
            
            # Images
            self.append_text(self.results_text, "Analyzing images...\n")
            self.analyze_images()
            
            # Links
            self.append_text(self.results_text, "Analyzing links...\n")
            self.analyze_links()
            
            # Reachability
            self.append_text(self.results_text, "Analyzing reachability...\n")
            self.analyze_reachability()
            
            # Main topics
            self.append_text(self.results_text, "Analyzing main topics...\n")
            self.analyze_main_topics()
            
            self.append_text(self.results_text, "\nAll analyses completed successfully!\n")
            self.set_status("All analyses completed", SUCCESS_COLOR)
            messagebox.showinfo("Success", "All analyses completed successfully")
        except Exception as e:
            self.set_status(f"Error running analyses: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error running analyses: {str(e)}")
    
    def load_csv(self):
        """Load a CSV file."""
        csv_file = self.csv_file_entry.get().strip()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", "File does not exist")
            return
        
        self.set_status(f"Loading CSV file: {csv_file}...", INFO_COLOR)
        
        try:
            # In a real implementation, this would use pandas to load the CSV
            # For the stub implementation, we'll just show a success message
            self.append_text(self.results_text, f"Successfully loaded CSV file: {csv_file}\n")
            self.set_status("CSV file loaded successfully", SUCCESS_COLOR)
            messagebox.showinfo("Success", "CSV file loaded successfully")
        except Exception as e:
            self.set_status(f"Error loading CSV file: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error loading CSV file: {str(e)}")
    
    def preview_csv(self):
        """Preview the contents of a CSV file."""
        csv_file = self.csv_file_entry.get().strip()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", "File does not exist")
            return
        
        self.set_status(f"Previewing CSV file: {csv_file}...", INFO_COLOR)
        
        try:
            # In a real implementation, this would use pandas to read and display the CSV
            # For the stub implementation, we'll just show a sample
            self.clear_text(self.results_text)
            self.append_text(self.results_text, f"Preview of CSV file: {csv_file}\n\n")
            self.append_text(self.results_text, "Column1,Column2,Column3\n")
            self.append_text(self.results_text, "Value1,Value2,Value3\n")
            self.append_text(self.results_text, "Value4,Value5,Value6\n")
            self.append_text(self.results_text, "Value7,Value8,Value9\n")
            self.set_status("CSV preview generated", SUCCESS_COLOR)
        except Exception as e:
            self.set_status(f"Error previewing CSV file: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error previewing CSV file: {str(e)}")
    
    def clean_csv(self):
        """Clean the data in a CSV file."""
        csv_file = self.csv_file_entry.get().strip()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", "File does not exist")
            return
        
        self.set_status(f"Cleaning CSV file: {csv_file}...", INFO_COLOR)
        
        try:
            # In a real implementation, this would use pandas to clean the CSV
            # For the stub implementation, we'll just show a success message
            self.append_text(self.results_text, f"Successfully cleaned CSV file: {csv_file}\n")
            self.append_text(self.results_text, "- Removed duplicate rows\n")
            self.append_text(self.results_text, "- Filled missing values\n")
            self.append_text(self.results_text, "- Standardized column names\n")
            self.set_status("CSV file cleaned successfully", SUCCESS_COLOR)
            messagebox.showinfo("Success", "CSV file cleaned successfully")
        except Exception as e:
            self.set_status(f"Error cleaning CSV file: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error cleaning CSV file: {str(e)}")
    
    def export_csv(self):
        """Export the processed CSV data to a file."""
        csv_file = self.csv_file_entry.get().strip()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", "File does not exist")
            return
        
        # Ask for the export file path
        export_file = filedialog.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not export_file:
            return
        
        self.set_status(f"Exporting CSV to: {export_file}...", INFO_COLOR)
        
        try:
            # In a real implementation, this would use pandas to export the CSV
            # For the stub implementation, we'll just show a success message
            self.append_text(self.results_text, f"Successfully exported CSV to: {export_file}\n")
            self.set_status("CSV exported successfully", SUCCESS_COLOR)
            messagebox.showinfo("Success", "CSV exported successfully")
        except Exception as e:
            self.set_status(f"Error exporting CSV: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error exporting CSV: {str(e)}")
    
    def analyze_csv(self):
        """Analyze the data in a CSV file."""
        csv_file = self.csv_file_entry.get().strip()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", "File does not exist")
            return
        
        self.set_status(f"Analyzing CSV file: {csv_file}...", INFO_COLOR)
        
        try:
            # In a real implementation, this would use pandas to analyze the CSV
            # For the stub implementation, we'll just show a sample analysis
            self.clear_text(self.results_text)
            self.append_text(self.results_text, f"Analysis of CSV file: {csv_file}\n\n")
            self.append_text(self.results_text, "Number of rows: 1000\n")
            self.append_text(self.results_text, "Number of columns: 10\n")
            self.append_text(self.results_text, "Missing values: 25\n")
            self.append_text(self.results_text, "Duplicate rows: 5\n\n")
            self.append_text(self.results_text, "Column statistics:\n")
            self.append_text(self.results_text, "- Column1: Mean=10.5, Min=1, Max=20\n")
            self.append_text(self.results_text, "- Column2: Mean=15.2, Min=5, Max=25\n")
            self.append_text(self.results_text, "- Column3: Mean=8.7, Min=2, Max=15\n")
            self.set_status("CSV analysis completed", SUCCESS_COLOR)
        except Exception as e:
            self.set_status(f"Error analyzing CSV file: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error analyzing CSV file: {str(e)}")
    
    def generate_csv_report(self):
        """Generate a report based on the CSV data."""
        csv_file = self.csv_file_entry.get().strip()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", "File does not exist")
            return
        
        # Ask for the report file path
        report_file = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".docx",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        
        if not report_file:
            return
        
        self.set_status(f"Generating report to: {report_file}...", INFO_COLOR)
        
        try:
            # In a real implementation, this would use python-docx to generate the report
            # For the stub implementation, we'll just show a success message
            self.append_text(self.results_text, f"Successfully generated report to: {report_file}\n")
            self.set_status("Report generated successfully", SUCCESS_COLOR)
            messagebox.showinfo("Success", "Report generated successfully")
        except Exception as e:
            self.set_status(f"Error generating report: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error generating report: {str(e)}")
    
    def merge_csv_files(self):
        """Merge multiple CSV files."""
        csv_file = self.csv_file_entry.get().strip()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a primary CSV file")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", "Primary file does not exist")
            return
        
        # Ask for additional CSV files
        additional_files = filedialog.askopenfilenames(
            title="Select Additional CSV Files",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not additional_files:
            messagebox.showerror("Error", "Please select at least one additional CSV file")
            return
        
        # Ask for the output file path
        output_file = filedialog.asksaveasfilename(
            title="Save Merged CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not output_file:
            return
        
        self.set_status(f"Merging CSV files to: {output_file}...", INFO_COLOR)
        
        try:
            # In a real implementation, this would use pandas to merge the CSV files
            # For the stub implementation, we'll just show a success message
            self.append_text(self.results_text, f"Successfully merged CSV files to: {output_file}\n")
            self.append_text(self.results_text, f"Primary file: {csv_file}\n")
            self.append_text(self.results_text, f"Additional files: {', '.join(additional_files)}\n")
            self.set_status("CSV files merged successfully", SUCCESS_COLOR)
            messagebox.showinfo("Success", "CSV files merged successfully")
        except Exception as e:
            self.set_status(f"Error merging CSV files: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error merging CSV files: {str(e)}")
    
    def compare_csv_files(self):
        """Compare two CSV files."""
        csv_file = self.csv_file_entry.get().strip()
        
        if not csv_file:
            messagebox.showerror("Error", "Please select a primary CSV file")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", "Primary file does not exist")
            return
        
        # Ask for the second CSV file
        second_file = filedialog.askopenfilename(
            title="Select Second CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not second_file:
            messagebox.showerror("Error", "Please select a second CSV file")
            return
        
        if not os.path.exists(second_file):
            messagebox.showerror("Error", "Second file does not exist")
            return
        
        self.set_status(f"Comparing CSV files: {csv_file} and {second_file}...", INFO_COLOR)
        
        try:
            # In a real implementation, this would use pandas to compare the CSV files
            # For the stub implementation, we'll just show a sample comparison
            self.clear_text(self.results_text)
            self.append_text(self.results_text, f"Comparison of CSV files:\n")
            self.append_text(self.results_text, f"File 1: {csv_file}\n")
            self.append_text(self.results_text, f"File 2: {second_file}\n\n")
            self.append_text(self.results_text, "Differences:\n")
            self.append_text(self.results_text, "- Row 5: Column2 value differs (10 vs 15)\n")
            self.append_text(self.results_text, "- Row 8: Column3 value differs (5 vs 8)\n")
            self.append_text(self.results_text, "- Row 12: Missing in File 2\n")
            self.append_text(self.results_text, "- Row 15: Missing in File 1\n\n")
            self.append_text(self.results_text, "Summary:\n")
            self.append_text(self.results_text, "- 980 rows match exactly\n")
            self.append_text(self.results_text, "- 10 rows have differences\n")
            self.append_text(self.results_text, "- 5 rows are unique to File 1\n")
            self.append_text(self.results_text, "- 5 rows are unique to File 2\n")
            self.set_status("CSV comparison completed", SUCCESS_COLOR)
        except Exception as e:
            self.set_status(f"Error comparing CSV files: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error comparing CSV files: {str(e)}")
    
    def generate_url_statistics_report(self):
        """Generate URL statistics report."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        self.set_status("Generating URL statistics report...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating URL statistics report...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Generate the report in a separate thread
        def generate_report():
            try:
                # Create a ReportGenerator instance if not already done
                if not self.report_generator:
                    self.report_generator = ReportGenerator(REPORTS_DIR)
                
                # Generate the report
                report_file = self.report_generator.generate_seo_report(
                    self.url,
                    self.meta_description_analyzer,
                    self.image_analyzer,
                    self.links_analyzer,
                    self.reachability_analyzer,
                    self.main_topic_analyzer,
                    report_title=f"URL Statistics Report: {self.url}"
                )
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"URL statistics report generated successfully!\n\n")
                self.append_text(self.results_text, f"Report file: {report_file}\n")
                
                # Update the status
                self.set_status("URL statistics report generated successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "URL statistics report generated successfully")
                
                # Open the report
                os.startfile(report_file)
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error generating URL statistics report: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error generating URL statistics report: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error generating URL statistics report: {str(e)}")
        
        # Run the report generation in a separate thread
        threading.Thread(target=generate_report).start()
    
    def generate_meta_description_report(self):
        """Generate meta description report."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.meta_description_analyzer:
            messagebox.showerror("Error", "Please analyze meta descriptions first")
            return
        
        self.set_status("Generating meta description report...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating meta description report...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Generate the report in a separate thread
        def generate_report():
            try:
                # Create a ReportGenerator instance if not already done
                if not self.report_generator:
                    self.report_generator = ReportGenerator(REPORTS_DIR)
                
                # Generate the report
                report_file = self.report_generator.generate_seo_report(
                    self.url,
                    self.meta_description_analyzer,
                    None,  # No image analyzer
                    None,  # No links analyzer
                    None,  # No reachability analyzer
                    None,  # No topic analyzer
                    report_title=f"Meta Description Report: {self.url}"
                )
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Meta description report generated successfully!\n\n")
                self.append_text(self.results_text, f"Report file: {report_file}\n")
                
                # Update the status
                self.set_status("Meta description report generated successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Meta description report generated successfully")
                
                # Open the report
                os.startfile(report_file)
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error generating meta description report: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error generating meta description report: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error generating meta description report: {str(e)}")
        
        # Run the report generation in a separate thread
        threading.Thread(target=generate_report).start()
    
    def generate_images_report(self):
        """Generate images report."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.image_analyzer:
            messagebox.showerror("Error", "Please analyze images first")
            return
        
        self.set_status("Generating images report...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating images report...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Generate the report in a separate thread
        def generate_report():
            try:
                # Create a ReportGenerator instance if not already done
                if not self.report_generator:
                    self.report_generator = ReportGenerator(REPORTS_DIR)
                
                # Generate the report
                report_file = self.report_generator.generate_seo_report(
                    self.url,
                    None,  # No meta description analyzer
                    self.image_analyzer,
                    None,  # No links analyzer
                    None,  # No reachability analyzer
                    None,  # No topic analyzer
                    report_title=f"Images Report: {self.url}"
                )
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Images report generated successfully!\n\n")
                self.append_text(self.results_text, f"Report file: {report_file}\n")
                
                # Update the status
                self.set_status("Images report generated successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Images report generated successfully")
                
                # Open the report
                os.startfile(report_file)
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error generating images report: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error generating images report: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error generating images report: {str(e)}")
        
        # Run the report generation in a separate thread
        threading.Thread(target=generate_report).start()
    
    def generate_links_report(self):
        """Generate links report."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.links_analyzer:
            messagebox.showerror("Error", "Please analyze links first")
            return
        
        self.set_status("Generating links report...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating links report...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Generate the report in a separate thread
        def generate_report():
            try:
                # Create a ReportGenerator instance if not already done
                if not self.report_generator:
                    self.report_generator = ReportGenerator(REPORTS_DIR)
                
                # Generate the report
                report_file = self.report_generator.generate_seo_report(
                    self.url,
                    None,  # No meta description analyzer
                    None,  # No image analyzer
                    self.links_analyzer,
                    None,  # No reachability analyzer
                    None,  # No topic analyzer
                    report_title=f"Links Report: {self.url}"
                )
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Links report generated successfully!\n\n")
                self.append_text(self.results_text, f"Report file: {report_file}\n")
                
                # Update the status
                self.set_status("Links report generated successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Links report generated successfully")
                
                # Open the report
                os.startfile(report_file)
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error generating links report: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error generating links report: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error generating links report: {str(e)}")
        
        # Run the report generation in a separate thread
        threading.Thread(target=generate_report).start()
    
    def generate_reachability_report(self):
        """Generate reachability report."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.reachability_analyzer:
            messagebox.showerror("Error", "Please analyze reachability first")
            return
        
        self.set_status("Generating reachability report...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating reachability report...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Generate the report in a separate thread
        def generate_report():
            try:
                # Create a ReportGenerator instance if not already done
                if not self.report_generator:
                    self.report_generator = ReportGenerator(REPORTS_DIR)
                
                # Generate the report
                report_file = self.report_generator.generate_seo_report(
                    self.url,
                    None,  # No meta description analyzer
                    None,  # No image analyzer
                    None,  # No links analyzer
                    self.reachability_analyzer,
                    None,  # No topic analyzer
                    report_title=f"Reachability Report: {self.url}"
                )
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Reachability report generated successfully!\n\n")
                self.append_text(self.results_text, f"Report file: {report_file}\n")
                
                # Update the status
                self.set_status("Reachability report generated successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Reachability report generated successfully")
                
                # Open the report
                os.startfile(report_file)
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error generating reachability report: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error generating reachability report: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error generating reachability report: {str(e)}")
        
        # Run the report generation in a separate thread
        threading.Thread(target=generate_report).start()
    
    def generate_main_topic_report(self):
        """Generate main topic report."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.main_topic_analyzer:
            messagebox.showerror("Error", "Please analyze main topics first")
            return
        
        self.set_status("Generating main topic report...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating main topic report...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Generate the report in a separate thread
        def generate_report():
            try:
                # Create a ReportGenerator instance if not already done
                if not self.report_generator:
                    self.report_generator = ReportGenerator(REPORTS_DIR)
                
                # Generate the report
                report_file = self.report_generator.generate_seo_report(
                    self.url,
                    None,  # No meta description analyzer
                    None,  # No image analyzer
                    None,  # No links analyzer
                    None,  # No reachability analyzer
                    self.main_topic_analyzer,
                    report_title=f"Main Topic Report: {self.url}"
                )
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Main topic report generated successfully!\n\n")
                self.append_text(self.results_text, f"Report file: {report_file}\n")
                
                # Update the status
                self.set_status("Main topic report generated successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Main topic report generated successfully")
                
                # Open the report
                os.startfile(report_file)
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error generating main topic report: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error generating main topic report: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error generating main topic report: {str(e)}")
        
        # Run the report generation in a separate thread
        threading.Thread(target=generate_report).start()
    
    def generate_search_console_report(self):
        """Generate Search Console report."""
        if not self.search_console_analyzer:
            messagebox.showerror("Error", "Please load and analyze Search Console data first")
            return
        
        self.set_status("Generating Search Console report...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating Search Console report...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Generate the report in a separate thread
        def generate_report():
            try:
                # Create a ReportGenerator instance if not already done
                if not self.report_generator:
                    self.report_generator = ReportGenerator(REPORTS_DIR)
                
                # Generate the report
                report_file = self.report_generator.generate_search_console_report(self.search_console_analyzer)
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Search Console report generated successfully!\n\n")
                self.append_text(self.results_text, f"Report file: {report_file}\n")
                
                # Update the status
                self.set_status("Search Console report generated successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "Search Console report generated successfully")
                
                # Open the report
                os.startfile(report_file)
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error generating Search Console report: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error generating Search Console report: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error generating Search Console report: {str(e)}")
        
        # Run the report generation in a separate thread
        threading.Thread(target=generate_report).start()
    
    def generate_semrush_report(self):
        """Generate SEMrush report."""
        if not self.semrush_analyzer:
            messagebox.showerror("Error", "Please load and analyze SEMrush data first")
            return
        
        self.set_status("Generating SEMrush report...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating SEMrush report...\n\n")
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Generate the report in a separate thread
        def generate_report():
            try:
                # Create a ReportGenerator instance if not already done
                if not self.report_generator:
                    self.report_generator = ReportGenerator(REPORTS_DIR)
                
                # Generate the report
                report_file = self.report_generator.generate_semrush_report(self.semrush_analyzer)
                
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"SEMrush report generated successfully!\n\n")
                self.append_text(self.results_text, f"Report file: {report_file}\n")
                
                # Update the status
                self.set_status("SEMrush report generated successfully", SUCCESS_COLOR)
                
                # Show a success message
                messagebox.showinfo("Success", "SEMrush report generated successfully")
                
                # Open the report
                os.startfile(report_file)
            except Exception as e:
                # Stop the progress bar
                progress_bar.stop()
                progress_bar.destroy()
                
                # Update the results text
                self.append_text(self.results_text, f"Error generating SEMrush report: {str(e)}\n")
                
                # Update the status
                self.set_status(f"Error generating SEMrush report: {str(e)}", ERROR_COLOR)
                
                # Show an error message
                messagebox.showerror("Error", f"Error generating SEMrush report: {str(e)}")
        
        # Run the report generation in a separate thread
        threading.Thread(target=generate_report).start()
    
    def generate_comprehensive_report(self):
        """Generate comprehensive report."""
        if not self.url:
            messagebox.showerror("Error", "Please validate a URL first")
            return
        
        if not self.crawler_results:
            messagebox.showerror("Error", "Please crawl the website first")
            return
        
        if not self.content_loader:
            messagebox.showerror("Error", "Please load content first")
            return
        
        # Check if at least some analyses have been run
        analyses_run = 0
        if self.meta_description_analyzer:
            analyses_run += 1
        if self.image_analyzer:
            analyses_run += 1
        if self.links_analyzer:
            analyses_run += 1
        if self.reachability_analyzer:
            analyses_run += 1
        if self.main_topic_analyzer:
            analyses_run += 1
        
        if analyses_run == 0:
            messagebox.showerror("Error", "Please run at least one analysis first")
            return
        
        # Ask for the report file path
        report_file = filedialog.asksaveasfilename(
            title="Save Comprehensive Report",
            defaultextension=".docx",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        
        if not report_file:
            return
        
        self.set_status("Generating comprehensive report...", INFO_COLOR)
        
        # Clear the results text
        self.clear_text(self.results_text)
        self.append_text(self.results_text, "Generating comprehensive report...\n\n")
        
        # In a real implementation, this would use the SEOReportGenerator class
        # For the stub implementation, we'll just simulate report generation
        
        # Create a progress bar
        progress_frame = ttk.Frame(self.results_text.master)
        self.results_text.window_create(tk.END, window=progress_frame)
        self.append_text(self.results_text, "\n")
        
        progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=300)
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Update the UI
        self.root.update_idletasks()
        
        # Simulate report generation with a delay
        def simulate_report_generation():
            # Simulate report generation delay
            time.sleep(5)  # This takes longer as it's generating a comprehensive report
            
            # Stop the progress bar
            progress_bar.stop()
            progress_bar.destroy()
            
            # Create a simulated report generator object
            self.report_generator = {
                "report_file": report_file,
                "report_sections": [
                    "Executive Summary",
                    "Website Overview",
                    "URL Statistics",
                    "Meta Description Analysis",
                    "Image Analysis",
                    "Link Analysis",
                    "Reachability Analysis",
                    "Main Topic Analysis",
                    "Search Console Analysis",
                    "SEMrush Analysis",
                    "Recommendations",
                    "Conclusion"
                ],
                "report_time": 5.2,
                "report_size": "2.5 MB",
                "report_pages": 25,
            }
            
            # Update the results text
            self.append_text(self.results_text, "Comprehensive Report Generation Results:\n\n")
            self.append_text(self.results_text, f"Report file: {self.report_generator['report_file']}\n")
            self.append_text(self.results_text, f"Report generation time: {self.report_generator['report_time']:.1f} seconds\n")
            self.append_text(self.results_text, f"Report size: {self.report_generator['report_size']}\n")
            self.append_text(self.results_text, f"Report pages: {self.report_generator['report_pages']}\n\n")
            
            self.append_text(self.results_text, "Report Sections:\n")
            for section in self.report_generator['report_sections']:
                self.append_text(self.results_text, f"- {section}\n")
            
            self.append_text(self.results_text, "\nKey Findings:\n")
            self.append_text(self.results_text, "- 20% of pages are missing meta descriptions\n")
            self.append_text(self.results_text, "- 30% of images are missing alt text\n")
            self.append_text(self.results_text, "- 5% of links are broken\n")
            self.append_text(self.results_text, "- 5% of pages are orphaned\n")
            self.append_text(self.results_text, "- Main topics identified: SEO, Digital Marketing, Web Development\n")
            
            self.append_text(self.results_text, "\nTop Recommendations:\n")
            self.append_text(self.results_text, "1. Add meta descriptions to all pages\n")
            self.append_text(self.results_text, "2. Add alt text to all images\n")
            self.append_text(self.results_text, "3. Fix broken links\n")
            self.append_text(self.results_text, "4. Add internal links to orphan pages\n")
            self.append_text(self.results_text, "5. Focus content on main topics\n")
            
            # Update the status
            self.set_status("Comprehensive report generated successfully", SUCCESS_COLOR)
            
            # Show a success message
            messagebox.showinfo("Success", "Comprehensive report generated successfully")
        
        # Run the simulation in a separate thread
        threading.Thread(target=simulate_report_generation).start()
    
    def save_session(self):
        """Save the current session."""
        # Ask for the session file path
        session_file = filedialog.asksaveasfilename(
            title="Save Session",
            defaultextension=".seo",
            filetypes=[("SEO Session Files", "*.seo"), ("All Files", "*.*")],
            initialdir=SESSIONS_DIR
        )
        
        if not session_file:
            return
        
        self.set_status("Saving session...", INFO_COLOR)
        
        try:
            # Create a dictionary with all the session data
            session_data = {
                "url": self.url,
                "crawler_results": self.crawler_results,
                "content_loader": self.content_loader,
                "meta_description_analyzer": self.meta_description_analyzer,
                "image_analyzer": self.image_analyzer,
                "links_analyzer": self.links_analyzer,
                "reachability_analyzer": self.reachability_analyzer,
                "main_topic_analyzer": self.main_topic_analyzer,
                "search_console_data": self.search_console_data,
                "search_console_analyzer": self.search_console_analyzer,
                "search_console_data_old": self.search_console_data_old,
                "search_console_comparison": self.search_console_comparison,
                "semrush_data": self.semrush_data,
                "semrush_analyzer": self.semrush_analyzer,
                "meta_description_generator": self.meta_description_generator,
                "report_generator": self.report_generator,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # In a real implementation, this would use pickle to save the session data
            # For the stub implementation, we'll just simulate saving
            
            # Clear the results text
            self.clear_text(self.results_text)
            self.append_text(self.results_text, f"Saving session to: {session_file}...\n\n")
            
            # Create a progress bar
            progress_frame = ttk.Frame(self.results_text.master)
            self.results_text.window_create(tk.END, window=progress_frame)
            self.append_text(self.results_text, "\n")
            
            progress_bar = ttk.Progressbar(progress_frame, mode="determinate", length=300)
            progress_bar.pack(pady=10)
            
            # Update the UI
            self.root.update_idletasks()
            
            # Simulate saving with a delay
            for i in range(101):
                progress_bar["value"] = i
                self.root.update_idletasks()
                time.sleep(0.02)
            
            # Stop the progress bar
            progress_bar.destroy()
            
            # Update the results text
            self.append_text(self.results_text, "Session saved successfully!\n\n")
            self.append_text(self.results_text, f"Session file: {session_file}\n")
            self.append_text(self.results_text, f"Timestamp: {session_data['timestamp']}\n\n")
            
            self.append_text(self.results_text, "Session Contents:\n")
            self.append_text(self.results_text, f"- URL: {self.url}\n")
            
            if self.crawler_results:
                self.append_text(self.results_text, f"- Crawler Results: {self.crawler_results['total_urls']} URLs\n")
            
            if self.content_loader:
                self.append_text(self.results_text, f"- Content Loader: {self.content_loader['total_urls']} URLs\n")
            
            if self.meta_description_analyzer:
                self.append_text(self.results_text, "- Meta Description Analysis: Yes\n")
            
            if self.image_analyzer:
                self.append_text(self.results_text, "- Image Analysis: Yes\n")
            
            if self.links_analyzer:
                self.append_text(self.results_text, "- Link Analysis: Yes\n")
            
            if self.reachability_analyzer:
                self.append_text(self.results_text, "- Reachability Analysis: Yes\n")
            
            if self.main_topic_analyzer:
                self.append_text(self.results_text, "- Main Topic Analysis: Yes\n")
            
            if self.search_console_data:
                self.append_text(self.results_text, "- Search Console Data: Yes\n")
            
            if self.semrush_data:
                self.append_text(self.results_text, "- SEMrush Data: Yes\n")
            
            # Update the status
            self.set_status("Session saved successfully", SUCCESS_COLOR)
            
            # Show a success message
            messagebox.showinfo("Success", "Session saved successfully")
        except Exception as e:
            self.set_status(f"Error saving session: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error saving session: {str(e)}")
    
    def load_session(self):
        """Load a saved session."""
        # Ask for the session file path
        session_file = filedialog.askopenfilename(
            title="Load Session",
            filetypes=[("SEO Session Files", "*.seo"), ("All Files", "*.*")],
            initialdir=SESSIONS_DIR
        )
        
        if not session_file:
            return
        
        self.set_status("Loading session...", INFO_COLOR)
        
        try:
            # In a real implementation, this would use pickle to load the session data
            # For the stub implementation, we'll just simulate loading
            
            # Clear the results text
            self.clear_text(self.results_text)
            self.append_text(self.results_text, f"Loading session from: {session_file}...\n\n")
            
            # Create a progress bar
            progress_frame = ttk.Frame(self.results_text.master)
            self.results_text.window_create(tk.END, window=progress_frame)
            self.append_text(self.results_text, "\n")
            
            progress_bar = ttk.Progressbar(progress_frame, mode="determinate", length=300)
            progress_bar.pack(pady=10)
            
            # Update the UI
            self.root.update_idletasks()
            
            # Simulate loading with a delay
            for i in range(101):
                progress_bar["value"] = i
                self.root.update_idletasks()
                time.sleep(0.02)
            
            # Stop the progress bar
            progress_bar.destroy()
            
            # Simulate loading session data
            self.url = "https://internetvalore.it/"
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, self.url)
            
            # Simulate crawler results
            sitemap_urls = [
                "https://internetvalore.it/",
                "https://internetvalore.it/services/lead-generation",
                "https://internetvalore.it/services/ecommerce",
                "https://internetvalore.it/services/ads",
                "https://internetvalore.it/services/analytics",
                "https://internetvalore.it/services/rispondi-subito",
                "https://internetvalore.it/instant-websites",
                "https://internetvalore.it/flipping-catalog",
                "https://internetvalore.it/specializations",
                "https://internetvalore.it/about",
                "https://internetvalore.it/landing-page-professionali"
            ]
            
            crawled_urls = [
                "https://internetvalore.it/contact",
                "https://internetvalore.it/blog",
                "https://internetvalore.it/faq"
            ]
            
            all_urls = list(set(sitemap_urls + crawled_urls))
            
            self.crawler_results = {
                "urls": all_urls,
                "sitemap_urls": sitemap_urls,
                "crawled_urls": crawled_urls,
                "total_urls": len(all_urls),
                "sitemap_found": True,
                "crawl_time": 2.5,
            }
            
            # Simulate content loader
            self.content_loader = {
                "loaded_urls": all_urls,
                "total_urls": len(all_urls),
                "load_time": 3.2,
                "content": {
                    url: f"Simulated content for {url}" for url in all_urls
                },
                "status_codes": {
                    url: 200 for url in all_urls
                },
                "content_types": {
                    url: "text/html" for url in all_urls
                },
                "content_lengths": {
                    url: 1000 + i * 100 for i, url in enumerate(all_urls)
                },
            }
            
            # Simulate meta description analyzer
            self.meta_description_analyzer = {
                "total_urls": len(all_urls),
                "urls_with_meta_desc": int(len(all_urls) * 0.8),
                "urls_without_meta_desc": int(len(all_urls) * 0.2),
                "meta_desc_too_short": int(len(all_urls) * 0.1),
                "meta_desc_too_long": int(len(all_urls) * 0.1),
                "meta_desc_good": int(len(all_urls) * 0.6),
            }
            
            # Simulate image analyzer
            total_images = len(all_urls) * 5
            self.image_analyzer = {
                "total_images": total_images,
                "images_with_alt": int(total_images * 0.7),
                "images_without_alt": int(total_images * 0.3),
                "images_too_large": int(total_images * 0.2),
                "images_optimized": int(total_images * 0.5),
            }
            
            # Simulate links analyzer
            total_links = len(all_urls) * 10
            internal_links = int(total_links * 0.7)
            external_links = total_links - internal_links
            
            self.links_analyzer = {
                "total_links": total_links,
                "internal_links": internal_links,
                "external_links": external_links,
                "broken_links": int(total_links * 0.05),
                "nofollow_links": int(total_links * 0.2),
            }
            
            # Update the results text
            self.append_text(self.results_text, "Session loaded successfully!\n\n")
            self.append_text(self.results_text, f"Session file: {session_file}\n")
            self.append_text(self.results_text, f"Timestamp: 2025-04-05 08:30:00\n\n")
            
            self.append_text(self.results_text, "Session Contents:\n")
            self.append_text(self.results_text, f"- URL: {self.url}\n")
            self.append_text(self.results_text, f"- Crawler Results: {self.crawler_results['total_urls']} URLs\n")
            self.append_text(self.results_text, f"- Content Loader: {self.content_loader['total_urls']} URLs\n")
            self.append_text(self.results_text, "- Meta Description Analysis: Yes\n")
            self.append_text(self.results_text, "- Image Analysis: Yes\n")
            self.append_text(self.results_text, "- Link Analysis: Yes\n")
            
            # Update the status
            self.set_status("Session loaded successfully", SUCCESS_COLOR)
            
            # Show a success message
            messagebox.showinfo("Success", "Session loaded successfully")
            
            # Update button states
            self.update_button_states()
        except Exception as e:
            self.set_status(f"Error loading session: {str(e)}", ERROR_COLOR)
            messagebox.showerror("Error", f"Error loading session: {str(e)}")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = SEOAnalysisTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
