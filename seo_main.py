#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main module for the SEO Analysis Tool.
Contains the main entry point and GUI.
"""

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import threading
import time
import json
from datetime import datetime

# Import modules
from seo_config_settings import *
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("seo_analysis.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

class SEOAnalysisTool:
    """Main class for the SEO Analysis Tool."""
    
    def __init__(self, root):
        """
        Initialize the SEO Analysis Tool.
        
        Args:
            root (tk.Tk): The root window
        """
        self.root = root
        self.root.title("SEO Analysis Tool")
        self.root.geometry("800x600")
        
        # Create a notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_crawl_tab()
        self.create_analysis_tab()
        self.create_search_console_tab()
        self.create_semrush_tab()
        self.create_report_tab()
        self.create_lmstudio_tab()
        
        # Initialize data
        self.base_url = ""
        self.urls = []
        self.content_loader = None
        self.meta_analyzer = None
        self.image_analyzer = None
        self.links_analyzer = None
        self.reachability_analyzer = None
        self.topic_analyzer = None
        self.search_console_data = None
        self.search_console_analyzer = None
        self.search_console_data_old = None
        self.search_console_comparison = None
        self.semrush_data = None
        self.semrush_analyzer = None
        self.lmstudio_client = None
        self.meta_description_generator = None
        self.report_generator = None
        
        # Create a status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create a menu
        self.create_menu()
        
        # Initialize the report generator
        self.report_generator = ReportGenerator(REPORT_OUTPUT_DIR)
        
        # Initialize the LM Studio client
        self.lmstudio_client = LMStudioClient(LMSTUDIO_API_URL)
        self.meta_description_generator = MetaDescriptionGenerator(self.lmstudio_client)
    
    def create_menu(self):
        """Create the menu."""
        # Create a menu bar
        menu_bar = tk.Menu(self.root)
        
        # Create a file menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save Session", command=self.save_session)
        file_menu.add_command(label="Load Session", command=self.load_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Add the file menu to the menu bar
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Create a help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Add the help menu to the menu bar
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Set the menu bar
        self.root.config(menu=menu_bar)
    
    def create_crawl_tab(self):
        """Create the crawl tab."""
        # Create a frame
        crawl_frame = ttk.Frame(self.notebook)
        self.notebook.add(crawl_frame, text="Crawl")
        
        # Create a frame for the URL input
        url_frame = ttk.Frame(crawl_frame)
        url_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a label for the URL input
        url_label = ttk.Label(url_frame, text="URL:")
        url_label.pack(side=tk.LEFT, padx=5)
        
        # Create an entry for the URL input
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        
        # Create a button to validate the URL
        validate_button = ttk.Button(url_frame, text="Validate", command=self.validate_url)
        validate_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the crawl options
        crawl_options_frame = ttk.LabelFrame(crawl_frame, text="Crawl Options")
        crawl_options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a frame for the max pages option
        max_pages_frame = ttk.Frame(crawl_options_frame)
        max_pages_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a label for the max pages option
        max_pages_label = ttk.Label(max_pages_frame, text="Max Pages:")
        max_pages_label.pack(side=tk.LEFT, padx=5)
        
        # Create an entry for the max pages option
        self.max_pages_entry = ttk.Entry(max_pages_frame, width=10)
        self.max_pages_entry.pack(side=tk.LEFT, padx=5)
        self.max_pages_entry.insert(0, str(CRAWLER_MAX_PAGES))
        
        # Create a frame for the max depth option
        max_depth_frame = ttk.Frame(crawl_options_frame)
        max_depth_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a label for the max depth option
        max_depth_label = ttk.Label(max_depth_frame, text="Max Depth:")
        max_depth_label.pack(side=tk.LEFT, padx=5)
        
        # Create an entry for the max depth option
        self.max_depth_entry = ttk.Entry(max_depth_frame, width=10)
        self.max_depth_entry.pack(side=tk.LEFT, padx=5)
        self.max_depth_entry.insert(0, str(CRAWLER_MAX_DEPTH))
        
        # Create a frame for the crawl buttons
        crawl_buttons_frame = ttk.Frame(crawl_frame)
        crawl_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a button to crawl the website
        self.crawl_button = ttk.Button(crawl_buttons_frame, text="Crawl Website", command=self.crawl_website)
        self.crawl_button.pack(side=tk.LEFT, padx=5)
        self.crawl_button["state"] = "disabled"
        
        # Create a button to process the sitemap
        self.sitemap_button = ttk.Button(crawl_buttons_frame, text="Process Sitemap", command=self.process_sitemap)
        self.sitemap_button.pack(side=tk.LEFT, padx=5)
        self.sitemap_button["state"] = "disabled"
        
        # Create a button to load content
        self.load_content_button = ttk.Button(crawl_buttons_frame, text="Load Content", command=self.load_content)
        self.load_content_button.pack(side=tk.LEFT, padx=5)
        self.load_content_button["state"] = "disabled"
        
        # Create a frame for the results
        results_frame = ttk.LabelFrame(crawl_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for the results
        self.crawl_results_text = tk.Text(results_frame, wrap=tk.WORD, width=80, height=20)
        self.crawl_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a scrollbar for the text widget
        crawl_results_scrollbar = ttk.Scrollbar(self.crawl_results_text, command=self.crawl_results_text.yview)
        crawl_results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.crawl_results_text.config(yscrollcommand=crawl_results_scrollbar.set)
    
    def create_analysis_tab(self):
        """Create the analysis tab."""
        # Create a frame
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Analysis")
        
        # Create a frame for the analysis buttons
        analysis_buttons_frame = ttk.Frame(analysis_frame)
        analysis_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a button to analyze meta descriptions
        self.meta_desc_button = ttk.Button(analysis_buttons_frame, text="Analyze Meta Descriptions", command=self.analyze_meta_descriptions)
        self.meta_desc_button.pack(side=tk.LEFT, padx=5)
        self.meta_desc_button["state"] = "disabled"
        
        # Create a button to analyze images
        self.images_button = ttk.Button(analysis_buttons_frame, text="Analyze Images", command=self.analyze_images)
        self.images_button.pack(side=tk.LEFT, padx=5)
        self.images_button["state"] = "disabled"
        
        # Create a button to analyze links
        self.links_button = ttk.Button(analysis_buttons_frame, text="Analyze Links", command=self.analyze_links)
        self.links_button.pack(side=tk.LEFT, padx=5)
        self.links_button["state"] = "disabled"
        
        # Create a button to analyze reachability
        self.reachability_button = ttk.Button(analysis_buttons_frame, text="Analyze Reachability", command=self.analyze_reachability)
        self.reachability_button.pack(side=tk.LEFT, padx=5)
        self.reachability_button["state"] = "disabled"
        
        # Create a button to analyze topics
        self.topics_button = ttk.Button(analysis_buttons_frame, text="Analyze Topics", command=self.analyze_topics)
        self.topics_button.pack(side=tk.LEFT, padx=5)
        self.topics_button["state"] = "disabled"
        
        # Create a frame for the results
        results_frame = ttk.LabelFrame(analysis_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for the results
        self.analysis_results_text = tk.Text(results_frame, wrap=tk.WORD, width=80, height=20)
        self.analysis_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a scrollbar for the text widget
        analysis_results_scrollbar = ttk.Scrollbar(self.analysis_results_text, command=self.analysis_results_text.yview)
        analysis_results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.analysis_results_text.config(yscrollcommand=analysis_results_scrollbar.set)
    
    def create_search_console_tab(self):
        """Create the Search Console tab."""
        # Create a frame
        search_console_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_console_frame, text="Search Console")
        
        # Create a frame for the file input
        file_frame = ttk.Frame(search_console_frame)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a label for the file input
        file_label = ttk.Label(file_frame, text="CSV File:")
        file_label.pack(side=tk.LEFT, padx=5)
        
        # Create an entry for the file input
        self.search_console_file_entry = ttk.Entry(file_frame, width=50)
        self.search_console_file_entry.pack(side=tk.LEFT, padx=5)
        
        # Create a button to browse for the file
        browse_button = ttk.Button(file_frame, text="Browse", command=lambda: self.browse_file(self.search_console_file_entry))
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # Create a button to load the file
        self.load_search_console_button = ttk.Button(file_frame, text="Load", command=self.load_search_console_data)
        self.load_search_console_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the comparison file input
        comparison_file_frame = ttk.Frame(search_console_frame)
        comparison_file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a label for the comparison file input
        comparison_file_label = ttk.Label(comparison_file_frame, text="Comparison CSV File:")
        comparison_file_label.pack(side=tk.LEFT, padx=5)
        
        # Create an entry for the comparison file input
        self.search_console_comparison_file_entry = ttk.Entry(comparison_file_frame, width=50)
        self.search_console_comparison_file_entry.pack(side=tk.LEFT, padx=5)
        
        # Create a button to browse for the comparison file
        comparison_browse_button = ttk.Button(comparison_file_frame, text="Browse", command=lambda: self.browse_file(self.search_console_comparison_file_entry))
        comparison_browse_button.pack(side=tk.LEFT, padx=5)
        
        # Create a button to load the comparison file
        self.load_search_console_comparison_button = ttk.Button(comparison_file_frame, text="Load", command=self.load_search_console_comparison_data)
        self.load_search_console_comparison_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the analysis buttons
        analysis_buttons_frame = ttk.Frame(search_console_frame)
        analysis_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a button to analyze the data
        self.analyze_search_console_button = ttk.Button(analysis_buttons_frame, text="Analyze Data", command=self.analyze_search_console_data)
        self.analyze_search_console_button.pack(side=tk.LEFT, padx=5)
        self.analyze_search_console_button["state"] = "disabled"
        
        # Create a button to compare the data
        self.compare_search_console_button = ttk.Button(analysis_buttons_frame, text="Compare Data", command=self.compare_search_console_data)
        self.compare_search_console_button.pack(side=tk.LEFT, padx=5)
        self.compare_search_console_button["state"] = "disabled"
        
        # Create a frame for the results
        results_frame = ttk.LabelFrame(search_console_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for the results
        self.search_console_results_text = tk.Text(results_frame, wrap=tk.WORD, width=80, height=20)
        self.search_console_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a scrollbar for the text widget
        search_console_results_scrollbar = ttk.Scrollbar(self.search_console_results_text, command=self.search_console_results_text.yview)
        search_console_results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_console_results_text.config(yscrollcommand=search_console_results_scrollbar.set)
    
    def create_semrush_tab(self):
        """Create the SEMrush tab."""
        # Create a frame
        semrush_frame = ttk.Frame(self.notebook)
        self.notebook.add(semrush_frame, text="SEMrush")
        
        # Create a frame for the file input
        file_frame = ttk.Frame(semrush_frame)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a label for the file input
        file_label = ttk.Label(file_frame, text="CSV File:")
        file_label.pack(side=tk.LEFT, padx=5)
        
        # Create an entry for the file input
        self.semrush_file_entry = ttk.Entry(file_frame, width=50)
        self.semrush_file_entry.pack(side=tk.LEFT, padx=5)
        
        # Create a button to browse for the file
        browse_button = ttk.Button(file_frame, text="Browse", command=lambda: self.browse_file(self.semrush_file_entry))
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # Create a button to load the file
        self.load_semrush_button = ttk.Button(file_frame, text="Load", command=self.load_semrush_data)
        self.load_semrush_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the analysis buttons
        analysis_buttons_frame = ttk.Frame(semrush_frame)
        analysis_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a button to analyze the data
        self.analyze_semrush_button = ttk.Button(analysis_buttons_frame, text="Analyze Data", command=self.analyze_semrush_data)
        self.analyze_semrush_button.pack(side=tk.LEFT, padx=5)
        self.analyze_semrush_button["state"] = "disabled"
        
        # Create a frame for the results
        results_frame = ttk.LabelFrame(semrush_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for the results
        self.semrush_results_text = tk.Text(results_frame, wrap=tk.WORD, width=80, height=20)
        self.semrush_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a scrollbar for the text widget
        semrush_results_scrollbar = ttk.Scrollbar(self.semrush_results_text, command=self.semrush_results_text.yview)
        semrush_results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.semrush_results_text.config(yscrollcommand=semrush_results_scrollbar.set)
    
    def create_report_tab(self):
        """Create the report tab."""
        # Create a frame
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="Report")
        
        # Create a frame for the report buttons
        report_buttons_frame = ttk.Frame(report_frame)
        report_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a button to generate an SEO report
        self.seo_report_button = ttk.Button(report_buttons_frame, text="Generate SEO Report", command=self.generate_seo_report)
        self.seo_report_button.pack(side=tk.LEFT, padx=5)
        self.seo_report_button["state"] = "disabled"
        
        # Create a button to generate a Search Console report
        self.search_console_report_button = ttk.Button(report_buttons_frame, text="Generate Search Console Report", command=self.generate_search_console_report)
        self.search_console_report_button.pack(side=tk.LEFT, padx=5)
        self.search_console_report_button["state"] = "disabled"
        
        # Create a button to generate a SEMrush report
        self.semrush_report_button = ttk.Button(report_buttons_frame, text="Generate SEMrush Report", command=self.generate_semrush_report)
        self.semrush_report_button.pack(side=tk.LEFT, padx=5)
        self.semrush_report_button["state"] = "disabled"
        
        # Create a button to generate a comparison report
        self.comparison_report_button = ttk.Button(report_buttons_frame, text="Generate Comparison Report", command=self.generate_comparison_report)
        self.comparison_report_button.pack(side=tk.LEFT, padx=5)
        self.comparison_report_button["state"] = "disabled"
        
        # Create a button to generate a final report
        self.final_report_button = ttk.Button(report_buttons_frame, text="Generate Final Report", command=self.generate_final_report)
        self.final_report_button.pack(side=tk.LEFT, padx=5)
        self.final_report_button["state"] = "disabled"
        
        # Create a frame for the results
        results_frame = ttk.LabelFrame(report_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for the results
        self.report_results_text = tk.Text(results_frame, wrap=tk.WORD, width=80, height=20)
        self.report_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a scrollbar for the text widget
        report_results_scrollbar = ttk.Scrollbar(self.report_results_text, command=self.report_results_text.yview)
        report_results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_results_text.config(yscrollcommand=report_results_scrollbar.set)
    
    def create_lmstudio_tab(self):
        """Create the LM Studio tab."""
        # Create a frame
        lmstudio_frame = ttk.Frame(self.notebook)
        self.notebook.add(lmstudio_frame, text="LM Studio")
        
        # Create a frame for the LM Studio options
        lmstudio_options_frame = ttk.LabelFrame(lmstudio_frame, text="LM Studio Options")
        lmstudio_options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a frame for the API URL option
        api_url_frame = ttk.Frame(lmstudio_options_frame)
        api_url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a label for the API URL option
        api_url_label = ttk.Label(api_url_frame, text="API URL:")
        api_url_label.pack(side=tk.LEFT, padx=5)
        
        # Create an entry for the API URL option
        self.api_url_entry = ttk.Entry(api_url_frame, width=50)
        self.api_url_entry.pack(side=tk.LEFT, padx=5)
        self.api_url_entry.insert(0, LMSTUDIO_API_URL)
        
        # Create a button to check the connection
        check_connection_button = ttk.Button(api_url_frame, text="Check Connection", command=self.check_lmstudio_connection)
        check_connection_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the LM Studio buttons
        lmstudio_buttons_frame = ttk.Frame(lmstudio_frame)
        lmstudio_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create a button to generate meta descriptions
        self.generate_meta_desc_button = ttk.Button(lmstudio_buttons_frame, text="Generate Meta Descriptions", command=self.generate_meta_descriptions)
        self.generate_meta_desc_button.pack(side=tk.LEFT, padx=5)
        self.generate_meta_desc_button["state"] = "disabled"
        
        # Create a button to generate ADS questions
        self.generate_ads_question_button = ttk.Button(lmstudio_buttons_frame, text="Generate ADS Questions", command=self.generate_ads_questions)
        self.generate_ads_question_button.pack(side=tk.LEFT, padx=5)
        self.generate_ads_question_button["state"] = "disabled"
        
        # Create a frame for the results
        results_frame = ttk.LabelFrame(lmstudio_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for the results
        self.lmstudio_results_text = tk.Text(results_frame, wrap=tk.WORD, width=80, height=20)
        self.lmstudio_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a scrollbar for the text widget
        lmstudio_results_scrollbar = ttk.Scrollbar(self.lmstudio_results_text, command=self.lmstudio_results_text.yview)
        lmstudio_results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lmstudio_results_text.config(yscrollcommand=lmstudio_results_scrollbar.set)
    
    def validate_url(self):
        """Validate the URL."""
        # Get the URL
        url = self.url_entry.get().strip()
        
        # Check if the URL is valid
        if SEOURLValidator.is_valid_url(url):
            # Normalize the URL
            self.base_url = SEOURLValidator.normalize_url(url)
            
            # Update the URL entry
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, self.base_url)
            
            # Enable the crawl and sitemap buttons
            self.crawl_button["state"] = "normal"
            self.sitemap_button["state"] = "normal"
            
            # Update the status
            self.status_var.set(f"URL validated: {self.base_url}")
            
            # Show a message
            messagebox.showinfo("URL Validation", f"URL is valid: {self.base_url}")
        else:
            # Update the status
            self.status_var.set("Invalid URL")
            
            # Show an error message
            messagebox.showerror("URL Validation", "Invalid URL")
    
    def crawl_website(self):
        """Crawl the website."""
        # Get the max pages and max depth
        try:
            max_pages = int(self.max_pages_entry.get().strip())
            max_depth = int(self.max_depth_entry.get().strip())
        except ValueError:
            # Show an error message
            messagebox.showerror("Crawl Website", "Invalid max pages or max depth")
            return
        
        # Update the status
        self.status_var.set(f"Crawling website: {self.base_url}")
        
        # Clear the results
        self.crawl_results_text.delete(1.0, tk.END)
        
        # Create a crawler
        crawler = SEOCrawler(self.base_url, max_pages, max_depth)
        
        # Crawl the website in a separate thread
        threading.Thread(target=self.crawl_website_thread, args=(crawler,)).start()
    
    def crawl_website_thread(self, crawler):
        """
        Crawl the website in a separate thread.
        
        Args:
            crawler (SEOCrawler): The crawler
        """
        try:
            # Crawl the website
            result = crawler.crawl()
            
            # Store the URLs
            self.urls = result["visited_urls"]
            
            # Update the status
            self.status_var.set(f"Crawled {len(self.urls)} URLs in {result['crawl_time']:.2f} seconds")
            
            # Enable the load content button
            self.root.after(0, lambda: self.load_content_button.config(state="normal"))
            
            # Show the results
            self.root.after(0, lambda: self.crawl_results_text.insert(tk.END, f"Crawled {len(self.urls)} URLs in {result['crawl_time']:.2f} seconds\n\n"))
            
            # Show the visited URLs
            self.root.after(0, lambda: self.crawl_results_text.insert(tk.END, "Visited URLs:\n"))
            for url in self.urls:
                self.root.after(0, lambda url=url: self.crawl_results_text.insert(tk.END, f"{url}\n"))
            
            # Show the errors
            if result["urls_with_errors"]:
                self.root.after(0, lambda: self.crawl_results_text.insert(tk.END, "\nErrors:\n"))
                for url, error in result["urls_with_errors"].items():
                    self.root.after(0, lambda url=url, error=error: self.crawl_results_text.insert(tk.END, f"{url}: {error}\n"))
        except Exception as e:
            # Update the status
            self.status_var.set(f"Error crawling website: {str(e)}")
