#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Links analyzer module for the SEO Analysis Tool.
Contains classes for analyzing links on web pages.
"""

import logging
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import time

from seo_url_validator import SEOURLValidator

class LinksAnalyzer:
    """Class for analyzing links on web pages."""
    
    def __init__(self, content_loader, base_url):
        """
        Initialize the links analyzer.
        
        Args:
            content_loader (ContentLoader): The content loader
            base_url (str): The base URL
        """
        self.content_loader = content_loader
        self.urls = content_loader.urls
        self.base_url = SEOURLValidator.normalize_url(base_url)
        
        self.links = {}
        self.internal_links = {}
        self.external_links = {}
        self.broken_links = {}
        self.nofollow_links = {}
        
        self.logger = logging.getLogger(__name__)
    
    def analyze(self):
        """
        Analyze links on web pages.
        
        Returns:
            dict: The analysis results
        """
        self.logger.info("Analyzing links")
        
        # Analyze each URL
        for url in self.urls:
            self.analyze_url(url)
        
        # Count total links
        total_links = sum(len(links) for links in self.links.values())
        
        # Count internal and external links
        internal_links = sum(len(links) for links in self.internal_links.values())
        external_links = sum(len(links) for links in self.external_links.values())
        
        # Count broken and nofollow links
        broken_links = sum(len(links) for links in self.broken_links.values())
        nofollow_links = sum(len(links) for links in self.nofollow_links.values())
        
        # Return the results
        return {
            "total_links": total_links,
            "internal_links": internal_links,
            "external_links": external_links,
            "broken_links": broken_links,
            "nofollow_links": nofollow_links,
            "links": self.links,
            "internal_links": self.internal_links,
            "external_links": self.external_links,
            "broken_links": self.broken_links,
            "nofollow_links": self.nofollow_links,
        }
    
    def analyze_url(self, url):
        """
        Analyze links on a web page.
        
        Args:
            url (str): The URL to analyze
        """
        # Get the soup
        soup = self.content_loader.get_soup(url)
        
        if not soup:
            self.logger.warning(f"No content for URL: {url}")
            return
        
        # Find all links
        a_tags = soup.find_all("a", href=True)
        
        # Initialize lists for this URL
        self.links[url] = []
        self.internal_links[url] = []
        self.external_links[url] = []
        self.broken_links[url] = []
        self.nofollow_links[url] = []
        
        # Analyze each link
        for a_tag in a_tags:
            # Get the link href
            href = a_tag["href"].strip()
            
            # Skip empty links
            if not href:
                continue
            
            # Skip anchors
            if href.startswith("#"):
                continue
            
            # Skip javascript: links
            if href.startswith("javascript:"):
                continue
            
            # Skip mailto: links
            if href.startswith("mailto:"):
                continue
            
            # Skip tel: links
            if href.startswith("tel:"):
                continue
            
            # Convert relative URLs to absolute URLs
            if not href.startswith(("http://", "https://")):
                href = urljoin(url, href)
            
            # Add the link to the list
            self.links[url].append(href)
            
            # Check if the link is internal or external
            if SEOURLValidator.is_internal_url(self.base_url, href):
                self.internal_links[url].append(href)
            else:
                self.external_links[url].append(href)
            
            # Check if the link is nofollow
            rel = a_tag.get("rel", "")
            
            if rel and "nofollow" in rel:
                self.nofollow_links[url].append(href)
            
            # Check if the link is broken
            if self.is_broken_link(href):
                self.broken_links[url].append(href)
        
        self.logger.info(f"Analyzed links for URL: {url} (found: {len(self.links[url])})")
    
    def is_broken_link(self, href):
        """
        Check if a link is broken.
        
        Args:
            href (str): The link href
        
        Returns:
            bool: True if the link is broken, False otherwise
        """
        try:
            # Send a HEAD request to check if the link is broken
            response = requests.head(href, timeout=10, allow_redirects=True)
            
            # Check if the status code indicates a broken link
            return response.status_code >= 400
        except Exception:
            # If an exception occurs, the link is considered broken
            return True
    
    def get_links(self, url):
        """
        Get all links on a web page.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The links
        """
        return self.links.get(url, [])
    
    def get_internal_links(self, url):
        """
        Get internal links on a web page.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The internal links
        """
        return self.internal_links.get(url, [])
    
    def get_external_links(self, url):
        """
        Get external links on a web page.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The external links
        """
        return self.external_links.get(url, [])
    
    def get_broken_links(self, url):
        """
        Get broken links on a web page.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The broken links
        """
        return self.broken_links.get(url, [])
    
    def get_nofollow_links(self, url):
        """
        Get nofollow links on a web page.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The nofollow links
        """
        return self.nofollow_links.get(url, [])
    
    def to_dataframe(self):
        """
        Convert the analysis results to a pandas DataFrame.
        
        Returns:
            pandas.DataFrame: The DataFrame
        """
        data = []
        
        for url in self.urls:
            for link in self.get_links(url):
                data.append({
                    "URL": url,
                    "Link": link,
                    "Is Internal": link in self.get_internal_links(url),
                    "Is External": link in self.get_external_links(url),
                    "Is Broken": link in self.get_broken_links(url),
                    "Is Nofollow": link in self.get_nofollow_links(url),
                })
        
        return pd.DataFrame(data)
