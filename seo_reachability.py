#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Reachability analyzer module for the SEO Analysis Tool.
Contains classes for analyzing the reachability of web pages.
"""

import logging
import pandas as pd
import networkx as nx
from urllib.parse import urlparse

from seo_url_validator import SEOURLValidator

class ReachabilityAnalyzer:
    """Class for analyzing the reachability of web pages."""
    
    def __init__(self, links_analyzer, base_url):
        """
        Initialize the reachability analyzer.
        
        Args:
            links_analyzer (LinksAnalyzer): The links analyzer
            base_url (str): The base URL
        """
        self.links_analyzer = links_analyzer
        self.base_url = SEOURLValidator.normalize_url(base_url)
        self.urls = links_analyzer.urls
        
        self.graph = None
        self.reachable_urls = set()
        self.orphan_pages = set()
        self.clicks_from_home = {}
        
        self.logger = logging.getLogger(__name__)
    
    def analyze(self):
        """
        Analyze the reachability of web pages.
        
        Returns:
            dict: The analysis results
        """
        self.logger.info("Analyzing reachability")
        
        # Build the graph
        self.build_graph()
        
        # Find reachable URLs
        self.find_reachable_urls()
        
        # Find orphan pages
        self.find_orphan_pages()
        
        # Calculate clicks from home
        self.calculate_clicks_from_home()
        
        # Calculate average and maximum clicks from home
        avg_clicks = sum(self.clicks_from_home.values()) / len(self.clicks_from_home) if self.clicks_from_home else 0
        max_clicks = max(self.clicks_from_home.values()) if self.clicks_from_home else 0
        
        # Return the results
        return {
            "total_urls": len(self.urls),
            "reachable_urls": len(self.reachable_urls),
            "orphan_pages": len(self.orphan_pages),
            "avg_clicks_from_home": avg_clicks,
            "max_clicks_from_home": max_clicks,
            "reachable_urls_list": list(self.reachable_urls),
            "orphan_pages_list": list(self.orphan_pages),
            "clicks_from_home": self.clicks_from_home,
        }
    
    def build_graph(self):
        """Build the graph of internal links."""
        # Create a directed graph
        self.graph = nx.DiGraph()
        
        # Add nodes for all URLs
        for url in self.urls:
            self.graph.add_node(url)
        
        # Add edges for internal links
        for url in self.urls:
            internal_links = self.links_analyzer.get_internal_links(url)
            
            for link in internal_links:
                # Skip links that are not in the URLs list
                if link not in self.urls:
                    continue
                
                # Add an edge from the URL to the link
                self.graph.add_edge(url, link)
    
    def find_reachable_urls(self):
        """Find URLs that are reachable from the home page."""
        # Get the home page URL
        home_url = self.base_url
        
        # If the home page is not in the URLs list, try to find it
        if home_url not in self.urls:
            # Try with a trailing slash
            home_url = f"{home_url}/"
            
            if home_url not in self.urls:
                # Try with /index.html
                home_url = f"{self.base_url}/index.html"
                
                if home_url not in self.urls:
                    # Try with /index.php
                    home_url = f"{self.base_url}/index.php"
                    
                    if home_url not in self.urls:
                        # Use the first URL as the home page
                        home_url = self.urls[0]
        
        # Find reachable URLs from the home page
        if home_url in self.urls:
            self.reachable_urls = set(nx.descendants(self.graph, home_url))
            self.reachable_urls.add(home_url)  # Add the home page itself
    
    def find_orphan_pages(self):
        """Find orphan pages (URLs that are not reachable from the home page)."""
        self.orphan_pages = set(self.urls) - self.reachable_urls
    
    def calculate_clicks_from_home(self):
        """Calculate the number of clicks from the home page to each URL."""
        # Get the home page URL
        home_url = self.base_url
        
        # If the home page is not in the URLs list, try to find it
        if home_url not in self.urls:
            # Try with a trailing slash
            home_url = f"{home_url}/"
            
            if home_url not in self.urls:
                # Try with /index.html
                home_url = f"{self.base_url}/index.html"
                
                if home_url not in self.urls:
                    # Try with /index.php
                    home_url = f"{self.base_url}/index.php"
                    
                    if home_url not in self.urls:
                        # Use the first URL as the home page
                        home_url = self.urls[0]
        
        # Calculate shortest paths from the home page
        if home_url in self.urls:
            # Calculate shortest path lengths
            shortest_paths = nx.single_source_shortest_path_length(self.graph, home_url)
            
            # Store the results
            self.clicks_from_home = shortest_paths
    
    def is_reachable(self, url):
        """
        Check if a URL is reachable from the home page.
        
        Args:
            url (str): The URL
        
        Returns:
            bool: True if the URL is reachable, False otherwise
        """
        return url in self.reachable_urls
    
    def is_orphan_page(self, url):
        """
        Check if a URL is an orphan page.
        
        Args:
            url (str): The URL
        
        Returns:
            bool: True if the URL is an orphan page, False otherwise
        """
        return url in self.orphan_pages
    
    def get_clicks_from_home(self, url):
        """
        Get the number of clicks from the home page to a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            int: The number of clicks from the home page
        """
        return self.clicks_from_home.get(url, float('inf'))
    
    def to_dataframe(self):
        """
        Convert the analysis results to a pandas DataFrame.
        
        Returns:
            pandas.DataFrame: The DataFrame
        """
        data = []
        
        for url in self.urls:
            data.append({
                "URL": url,
                "Is Reachable": self.is_reachable(url),
                "Is Orphan Page": self.is_orphan_page(url),
                "Clicks from Home": self.get_clicks_from_home(url),
            })
        
        return pd.DataFrame(data)
