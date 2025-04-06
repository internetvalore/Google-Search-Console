#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
URL validation module.
Contains functions for validating URLs.
"""

import validators
import requests
from urllib.parse import urlparse
from config import VALID_SCHEMES, REQUEST_TIMEOUT


class URLValidator:
    """Class for validating URLs."""
    
    @staticmethod
    def is_empty(url):
        """Check if URL is empty."""
        return not url.strip()
    
    @staticmethod
    def has_valid_format(url):
        """Check if URL has a valid format."""
        return validators.url(url)
    
    @staticmethod
    def has_valid_scheme(url):
        """Check if URL has a valid scheme (http or https)."""
        parsed_url = urlparse(url)
        return parsed_url.scheme in VALID_SCHEMES
    
    @staticmethod
    def is_accessible(url):
        """
        Check if URL is accessible.
        
        Returns:
            tuple: (is_success, message, status_code)
                - is_success: True if URL is accessible, False otherwise
                - message: Success or error message
                - status_code: HTTP status code or None if request failed
        """
        try:
            response = requests.head(url, timeout=REQUEST_TIMEOUT)
            if response.status_code < 400:
                return True, f"URL is valid and accessible: {url}", response.status_code
            else:
                return False, f"URL returned error status {response.status_code}: {url}", response.status_code
        except requests.exceptions.RequestException as e:
            return False, f"Could not access URL: {url}\nError: {str(e)}", None
    
    @classmethod
    def validate(cls, url):
        """
        Validate URL format and accessibility.
        
        Args:
            url (str): URL to validate
            
        Returns:
            tuple: (is_valid, message, status_code)
                - is_valid: True if URL is valid and accessible, False otherwise
                - message: Success or error message
                - status_code: HTTP status code or None if request failed
        """
        # Check if URL is empty
        if cls.is_empty(url):
            return False, "Please enter a URL", None
        
        # Check URL format
        if not cls.has_valid_format(url):
            return False, f"Invalid URL format: {url}", None
        
        # Check if URL has a valid scheme
        if not cls.has_valid_scheme(url):
            return False, f"URL must use http or https scheme: {url}", None
        
        # Check if URL is accessible
        return cls.is_accessible(url)
