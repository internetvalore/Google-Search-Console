#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Image analyzer module for the SEO Analysis Tool.
Contains classes for analyzing images on web pages.
"""

import logging
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os
import time

class ImageAnalyzer:
    """Class for analyzing images on web pages."""
    
    def __init__(self, content_loader):
        """
        Initialize the image analyzer.
        
        Args:
            content_loader (ContentLoader): The content loader
        """
        self.content_loader = content_loader
        self.urls = content_loader.urls
        
        self.images = {}
        self.images_with_alt = {}
        self.images_without_alt = {}
        self.image_sizes = {}
        self.image_formats = {}
        
        self.logger = logging.getLogger(__name__)
    
    def analyze(self):
        """
        Analyze images on web pages.
        
        Returns:
            dict: The analysis results
        """
        self.logger.info("Analyzing images")
        
        # Analyze each URL
        for url in self.urls:
            self.analyze_url(url)
        
        # Count total images
        total_images = sum(len(images) for images in self.images.values())
        
        # Count images with and without alt text
        images_with_alt = sum(len(images) for images in self.images_with_alt.values())
        images_without_alt = sum(len(images) for images in self.images_without_alt.values())
        
        # Count large images
        images_too_large = sum(1 for sizes in self.image_sizes.values() for size in sizes.values() if size > 100000)  # > 100 KB
        
        # Count optimized images
        images_optimized = total_images - images_too_large
        
        # Return the results
        return {
            "total_images": total_images,
            "images_with_alt": images_with_alt,
            "images_without_alt": images_without_alt,
            "images_too_large": images_too_large,
            "images_optimized": images_optimized,
            "images": self.images,
            "images_with_alt": self.images_with_alt,
            "images_without_alt": self.images_without_alt,
            "image_sizes": self.image_sizes,
            "image_formats": self.image_formats,
        }
    
    def analyze_url(self, url):
        """
        Analyze images on a web page.
        
        Args:
            url (str): The URL to analyze
        """
        # Get the soup
        soup = self.content_loader.get_soup(url)
        
        if not soup:
            self.logger.warning(f"No content for URL: {url}")
            return
        
        # Find all images
        img_tags = soup.find_all("img")
        
        # Initialize lists for this URL
        self.images[url] = []
        self.images_with_alt[url] = []
        self.images_without_alt[url] = []
        self.image_sizes[url] = {}
        self.image_formats[url] = {}
        
        # Analyze each image
        for img in img_tags:
            # Get the image source
            src = img.get("src", "")
            
            # Skip empty sources
            if not src:
                continue
            
            # Convert relative URLs to absolute URLs
            if not src.startswith(("http://", "https://")):
                src = urljoin(url, src)
            
            # Add the image to the list
            self.images[url].append(src)
            
            # Check if the image has alt text
            alt = img.get("alt", "")
            
            if alt:
                self.images_with_alt[url].append(src)
            else:
                self.images_without_alt[url].append(src)
            
            # Get the image format
            image_format = self.get_image_format(src)
            self.image_formats[url][src] = image_format
            
            # Get the image size
            image_size = self.get_image_size(src)
            self.image_sizes[url][src] = image_size
        
        self.logger.info(f"Analyzed images for URL: {url} (found: {len(self.images[url])})")
    
    def get_image_format(self, src):
        """
        Get the image format from the source URL.
        
        Args:
            src (str): The image source URL
        
        Returns:
            str: The image format
        """
        # Get the file extension
        _, ext = os.path.splitext(src)
        
        # Remove the dot
        ext = ext.lstrip(".").lower()
        
        # Map common extensions to formats
        format_map = {
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "png": "PNG",
            "gif": "GIF",
            "webp": "WebP",
            "svg": "SVG",
            "ico": "ICO",
        }
        
        return format_map.get(ext, ext.upper() if ext else "Unknown")
    
    def get_image_size(self, src):
        """
        Get the image size in bytes.
        
        Args:
            src (str): The image source URL
        
        Returns:
            int: The image size in bytes
        """
        try:
            # Send a HEAD request to get the content length
            response = requests.head(src, timeout=10)
            
            # Get the content length
            content_length = response.headers.get("Content-Length")
            
            if content_length:
                return int(content_length)
            
            # If content length is not available, send a GET request
            response = requests.get(src, timeout=10, stream=True)
            
            # Get the content length
            content_length = response.headers.get("Content-Length")
            
            if content_length:
                return int(content_length)
            
            # If content length is still not available, download the image
            content = response.content
            
            return len(content)
        except Exception as e:
            self.logger.error(f"Error getting image size: {src} ({str(e)})")
            return 0
    
    def get_images(self, url):
        """
        Get all images on a web page.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The images
        """
        return self.images.get(url, [])
    
    def get_images_with_alt(self, url):
        """
        Get images with alt text on a web page.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The images with alt text
        """
        return self.images_with_alt.get(url, [])
    
    def get_images_without_alt(self, url):
        """
        Get images without alt text on a web page.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The images without alt text
        """
        return self.images_without_alt.get(url, [])
    
    def get_image_size(self, url, src):
        """
        Get the size of an image.
        
        Args:
            url (str): The URL
            src (str): The image source URL
        
        Returns:
            int: The image size in bytes
        """
        return self.image_sizes.get(url, {}).get(src, 0)
    
    def get_image_format(self, url, src):
        """
        Get the format of an image.
        
        Args:
            url (str): The URL
            src (str): The image source URL
        
        Returns:
            str: The image format
        """
        return self.image_formats.get(url, {}).get(src, "Unknown")
    
    def to_dataframe(self):
        """
        Convert the analysis results to a pandas DataFrame.
        
        Returns:
            pandas.DataFrame: The DataFrame
        """
        data = []
        
        for url in self.urls:
            for src in self.get_images(url):
                data.append({
                    "URL": url,
                    "Image Source": src,
                    "Has Alt Text": src in self.get_images_with_alt(url),
                    "Image Size": self.get_image_size(url, src),
                    "Image Format": self.get_image_format(url, src),
                })
        
        return pd.DataFrame(data)
