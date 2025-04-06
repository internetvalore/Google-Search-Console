#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Meta description analyzer module for the SEO Analysis Tool.
Contains classes for analyzing meta descriptions.
"""

import logging
import pandas as pd
from bs4 import BeautifulSoup
from seo_config_settings import META_DESC_MIN_LENGTH, META_DESC_MAX_LENGTH

class MetaDescriptionAnalyzer:
    """Class for analyzing meta descriptions."""
    
    def __init__(self, content_loader):
        """
        Initialize the meta description analyzer.
        
        Args:
            content_loader (ContentLoader): The content loader
        """
        self.content_loader = content_loader
        self.urls = content_loader.urls
        
        self.meta_descriptions = {}
        self.has_meta_desc = {}
        self.meta_desc_length = {}
        self.meta_desc_quality = {}
        
        self.logger = logging.getLogger(__name__)
    
    def analyze(self):
        """
        Analyze meta descriptions.
        
        Returns:
            dict: The analysis results
        """
        self.logger.info("Analyzing meta descriptions")
        
        # Analyze each URL
        for url in self.urls:
            self.analyze_url(url)
        
        # Count URLs with and without meta descriptions
        urls_with_meta_desc = sum(1 for has_meta in self.has_meta_desc.values() if has_meta)
        urls_without_meta_desc = len(self.urls) - urls_with_meta_desc
        
        # Count meta description quality
        meta_desc_too_short = sum(1 for quality in self.meta_desc_quality.values() if quality == "too_short")
        meta_desc_too_long = sum(1 for quality in self.meta_desc_quality.values() if quality == "too_long")
        meta_desc_good = sum(1 for quality in self.meta_desc_quality.values() if quality == "good")
        
        # Return the results
        return {
            "total_urls": len(self.urls),
            "urls_with_meta_desc": urls_with_meta_desc,
            "urls_without_meta_desc": urls_without_meta_desc,
            "meta_desc_too_short": meta_desc_too_short,
            "meta_desc_too_long": meta_desc_too_long,
            "meta_desc_good": meta_desc_good,
            "meta_descriptions": self.meta_descriptions,
            "has_meta_desc": self.has_meta_desc,
            "meta_desc_length": self.meta_desc_length,
            "meta_desc_quality": self.meta_desc_quality,
        }
    
    def analyze_url(self, url):
        """
        Analyze the meta description for a URL.
        
        Args:
            url (str): The URL to analyze
        """
        # Get the meta description
        meta_desc = self.content_loader.get_meta_description(url)
        
        # Store the meta description
        self.meta_descriptions[url] = meta_desc
        
        # Check if the URL has a meta description
        has_meta = bool(meta_desc)
        self.has_meta_desc[url] = has_meta
        
        # Get the meta description length
        meta_desc_length = len(meta_desc) if meta_desc else 0
        self.meta_desc_length[url] = meta_desc_length
        
        # Evaluate the meta description quality
        if not has_meta:
            quality = "missing"
        elif meta_desc_length < META_DESC_MIN_LENGTH:
            quality = "too_short"
        elif meta_desc_length > META_DESC_MAX_LENGTH:
            quality = "too_long"
        else:
            quality = "good"
        
        self.meta_desc_quality[url] = quality
        
        self.logger.info(f"Analyzed meta description for URL: {url} (quality: {quality})")
    
    def get_urls_without_meta_desc(self):
        """
        Get URLs without meta descriptions.
        
        Returns:
            list: The URLs without meta descriptions
        """
        return [url for url, has_meta in self.has_meta_desc.items() if not has_meta]
    
    def get_urls_with_short_meta_desc(self):
        """
        Get URLs with short meta descriptions.
        
        Returns:
            list: The URLs with short meta descriptions
        """
        return [url for url, quality in self.meta_desc_quality.items() if quality == "too_short"]
    
    def get_urls_with_long_meta_desc(self):
        """
        Get URLs with long meta descriptions.
        
        Returns:
            list: The URLs with long meta descriptions
        """
        return [url for url, quality in self.meta_desc_quality.items() if quality == "too_long"]
    
    def get_urls_with_good_meta_desc(self):
        """
        Get URLs with good meta descriptions.
        
        Returns:
            list: The URLs with good meta descriptions
        """
        return [url for url, quality in self.meta_desc_quality.items() if quality == "good"]
    
    def get_meta_description(self, url):
        """
        Get the meta description for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The meta description
        """
        return self.meta_descriptions.get(url, "")
    
    def has_meta_description(self, url):
        """
        Check if a URL has a meta description.
        
        Args:
            url (str): The URL
        
        Returns:
            bool: True if the URL has a meta description, False otherwise
        """
        return self.has_meta_desc.get(url, False)
    
    def get_meta_description_length(self, url):
        """
        Get the meta description length for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            int: The meta description length
        """
        return self.meta_desc_length.get(url, 0)
    
    def get_meta_description_quality(self, url):
        """
        Get the meta description quality for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The meta description quality
        """
        return self.meta_desc_quality.get(url, "missing")
    
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
                "Has Meta Description": self.has_meta_desc.get(url, False),
                "Meta Description": self.meta_descriptions.get(url, ""),
                "Meta Description Length": self.meta_desc_length.get(url, 0),
                "Meta Description Quality": self.meta_desc_quality.get(url, "missing"),
            })
        
        return pd.DataFrame(data)
