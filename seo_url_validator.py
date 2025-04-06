#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
URL validator module for the SEO Analysis Tool.
Contains classes for validating and normalizing URLs.
"""

import logging
import re
from urllib.parse import urlparse, urljoin, urlunparse

class SEOURLValidator:
    """Class for validating and normalizing URLs."""
    
    @staticmethod
    def is_valid_url(url):
        """
        Check if a URL is valid.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is valid, False otherwise
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Check if the URL has a scheme and netloc
            return bool(parsed_url.scheme and parsed_url.netloc)
        except Exception:
            return False
    
    @staticmethod
    def normalize_url(url):
        """
        Normalize a URL.
        
        Args:
            url (str): The URL to normalize
        
        Returns:
            str: The normalized URL
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Normalize the scheme
            scheme = parsed_url.scheme.lower() or "http"
            
            # Normalize the netloc
            netloc = parsed_url.netloc.lower()
            
            # Remove trailing slash from path
            path = parsed_url.path
            if path == "/":
                path = ""
            
            # Remove default port
            if netloc.endswith(":80") and scheme == "http":
                netloc = netloc[:-3]
            elif netloc.endswith(":443") and scheme == "https":
                netloc = netloc[:-4]
            
            # Reconstruct the URL
            normalized_url = urlunparse((scheme, netloc, path, parsed_url.params, parsed_url.query, ""))
            
            return normalized_url
        except Exception:
            return url
    
    @staticmethod
    def is_internal_url(base_url, url):
        """
        Check if a URL is internal to a base URL.
        
        Args:
            base_url (str): The base URL
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is internal, False otherwise
        """
        try:
            # Parse the URLs
            parsed_base_url = urlparse(base_url)
            parsed_url = urlparse(url)
            
            # Check if the netloc is the same
            return parsed_base_url.netloc == parsed_url.netloc
        except Exception:
            return False
    
    @staticmethod
    def get_domain(url):
        """
        Get the domain from a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The domain
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Get the netloc
            netloc = parsed_url.netloc.lower()
            
            # Remove port if present
            if ":" in netloc:
                netloc = netloc.split(":")[0]
            
            return netloc
        except Exception:
            return ""
    
    @staticmethod
    def get_path(url):
        """
        Get the path from a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The path
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Get the path
            path = parsed_url.path
            
            return path
        except Exception:
            return ""
    
    @staticmethod
    def get_query(url):
        """
        Get the query from a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The query
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Get the query
            query = parsed_url.query
            
            return query
        except Exception:
            return ""
    
    @staticmethod
    def remove_query(url):
        """
        Remove the query from a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The URL without the query
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Reconstruct the URL without the query
            url_without_query = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, "", ""))
            
            return url_without_query
        except Exception:
            return url
    
    @staticmethod
    def remove_fragment(url):
        """
        Remove the fragment from a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The URL without the fragment
        """
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            
            # Reconstruct the URL without the fragment
            url_without_fragment = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, parsed_url.query, ""))
            
            return url_without_fragment
        except Exception:
            return url
    
    @staticmethod
    def is_same_page(url1, url2):
        """
        Check if two URLs point to the same page.
        
        Args:
            url1 (str): The first URL
            url2 (str): The second URL
        
        Returns:
            bool: True if the URLs point to the same page, False otherwise
        """
        try:
            # Normalize the URLs
            url1 = SEOURLValidator.normalize_url(url1)
            url2 = SEOURLValidator.normalize_url(url2)
            
            # Remove fragments
            url1 = SEOURLValidator.remove_fragment(url1)
            url2 = SEOURLValidator.remove_fragment(url2)
            
            return url1 == url2
        except Exception:
            return False
    
    @staticmethod
    def is_sitemap_url(url):
        """
        Check if a URL is a sitemap URL.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is a sitemap URL, False otherwise
        """
        try:
            # Check if the URL ends with sitemap.xml
            return url.endswith("sitemap.xml") or url.endswith("sitemap.xml.gz")
        except Exception:
            return False
    
    @staticmethod
    def is_robots_txt_url(url):
        """
        Check if a URL is a robots.txt URL.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is a robots.txt URL, False otherwise
        """
        try:
            # Check if the URL ends with robots.txt
            return url.endswith("robots.txt")
        except Exception:
            return False
    
    @staticmethod
    def is_image_url(url):
        """
        Check if a URL is an image URL.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is an image URL, False otherwise
        """
        try:
            # Check if the URL ends with an image extension
            image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico"]
            
            for ext in image_extensions:
                if url.lower().endswith(ext):
                    return True
            
            return False
        except Exception:
            return False
    
    @staticmethod
    def is_css_url(url):
        """
        Check if a URL is a CSS URL.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is a CSS URL, False otherwise
        """
        try:
            # Check if the URL ends with .css
            return url.lower().endswith(".css")
        except Exception:
            return False
    
    @staticmethod
    def is_js_url(url):
        """
        Check if a URL is a JavaScript URL.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is a JavaScript URL, False otherwise
        """
        try:
            # Check if the URL ends with .js
            return url.lower().endswith(".js")
        except Exception:
            return False
    
    @staticmethod
    def is_pdf_url(url):
        """
        Check if a URL is a PDF URL.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is a PDF URL, False otherwise
        """
        try:
            # Check if the URL ends with .pdf
            return url.lower().endswith(".pdf")
        except Exception:
            return False
    
    @staticmethod
    def is_html_url(url):
        """
        Check if a URL is an HTML URL.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is an HTML URL, False otherwise
        """
        try:
            # Check if the URL ends with .html or .htm
            return url.lower().endswith(".html") or url.lower().endswith(".htm")
        except Exception:
            return False
    
    @staticmethod
    def is_xml_url(url):
        """
        Check if a URL is an XML URL.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is an XML URL, False otherwise
        """
        try:
            # Check if the URL ends with .xml
            return url.lower().endswith(".xml")
        except Exception:
            return False
    
    @staticmethod
    def is_json_url(url):
        """
        Check if a URL is a JSON URL.
        
        Args:
            url (str): The URL to check
        
        Returns:
            bool: True if the URL is a JSON URL, False otherwise
        """
        try:
            # Check if the URL ends with .json
            return url.lower().endswith(".json")
        except Exception:
            return False
