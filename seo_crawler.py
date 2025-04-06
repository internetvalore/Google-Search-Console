#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Crawler module for the SEO Analysis Tool.
Contains classes for crawling websites and processing sitemaps.
"""

import logging
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET
import gzip
import io
import re

from seo_config_settings import CRAWLER_MAX_PAGES, CRAWLER_MAX_DEPTH, CRAWLER_TIMEOUT, CRAWLER_USER_AGENT
from seo_url_validator import SEOURLValidator

class SEOCrawler:
    """Class for crawling websites."""
    
    def __init__(self, base_url, max_pages=CRAWLER_MAX_PAGES, max_depth=CRAWLER_MAX_DEPTH, timeout=CRAWLER_TIMEOUT, user_agent=CRAWLER_USER_AGENT):
        """
        Initialize the crawler.
        
        Args:
            base_url (str): The base URL to crawl
            max_pages (int): The maximum number of pages to crawl
            max_depth (int): The maximum depth to crawl
            timeout (int): The timeout for requests in seconds
            user_agent (str): The user agent to use
        """
        self.base_url = SEOURLValidator.normalize_url(base_url)
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.timeout = timeout
        self.user_agent = user_agent
        
        self.visited_urls = set()
        self.urls_to_visit = []
        self.urls_in_queue = set()
        self.urls_with_errors = {}
        
        self.logger = logging.getLogger(__name__)
    
    def crawl(self):
        """
        Crawl the website.
        
        Returns:
            dict: The crawl results
        """
        self.logger.info(f"Crawling website: {self.base_url}")
        
        # Start with the base URL
        self.urls_to_visit.append((self.base_url, 0))  # (url, depth)
        self.urls_in_queue.add(self.base_url)
        
        # Start time
        start_time = time.time()
        
        # Crawl until we reach the maximum number of pages or run out of URLs
        while self.urls_to_visit and len(self.visited_urls) < self.max_pages:
            # Get the next URL to visit
            url, depth = self.urls_to_visit.pop(0)
            self.urls_in_queue.remove(url)
            
            # Skip if we've already visited this URL
            if url in self.visited_urls:
                continue
            
            # Skip if we've reached the maximum depth
            if depth > self.max_depth:
                continue
            
            # Visit the URL
            self.logger.info(f"Visiting URL: {url} (depth: {depth})")
            
            try:
                # Send a GET request
                response = requests.get(
                    url,
                    timeout=self.timeout,
                    headers={"User-Agent": self.user_agent},
                )
                
                # Check if the request was successful
                if response.status_code == 200:
                    # Add the URL to the visited URLs
                    self.visited_urls.add(url)
                    
                    # Parse the HTML
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Find all links
                    links = soup.find_all("a", href=True)
                    
                    # Process each link
                    for link in links:
                        # Get the href
                        href = link["href"].strip()
                        
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
                        
                        # Skip external links
                        if not SEOURLValidator.is_internal_url(self.base_url, href):
                            continue
                        
                        # Skip non-HTML links
                        if SEOURLValidator.is_image_url(href) or SEOURLValidator.is_css_url(href) or SEOURLValidator.is_js_url(href) or SEOURLValidator.is_pdf_url(href):
                            continue
                        
                        # Skip if we've already visited or queued this URL
                        if href in self.visited_urls or href in self.urls_in_queue:
                            continue
                        
                        # Add the URL to the queue
                        self.urls_to_visit.append((href, depth + 1))
                        self.urls_in_queue.add(href)
                else:
                    # Add the URL to the errors
                    self.urls_with_errors[url] = f"HTTP {response.status_code}"
            except Exception as e:
                # Add the URL to the errors
                self.urls_with_errors[url] = str(e)
        
        # Calculate crawl time
        crawl_time = time.time() - start_time
        
        # Return the results
        return {
            "base_url": self.base_url,
            "visited_urls": list(self.visited_urls),
            "urls_with_errors": self.urls_with_errors,
            "total_urls": len(self.visited_urls),
            "total_errors": len(self.urls_with_errors),
            "crawl_time": crawl_time,
        }


class SitemapProcessor:
    """Class for processing sitemaps."""
    
    def __init__(self, sitemap_url, timeout=CRAWLER_TIMEOUT, user_agent=CRAWLER_USER_AGENT):
        """
        Initialize the sitemap processor.
        
        Args:
            sitemap_url (str): The URL of the sitemap
            timeout (int): The timeout for requests in seconds
            user_agent (str): The user agent to use
        """
        self.sitemap_url = sitemap_url
        self.timeout = timeout
        self.user_agent = user_agent
        
        self.urls = []
        self.sitemap_index_urls = []
        
        self.logger = logging.getLogger(__name__)
    
    def process(self):
        """
        Process the sitemap.
        
        Returns:
            dict: The processing results
        """
        self.logger.info(f"Processing sitemap: {self.sitemap_url}")
        
        # Start time
        start_time = time.time()
        
        try:
            # Send a GET request
            response = requests.get(
                self.sitemap_url,
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent},
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                # Check if the sitemap is gzipped
                content = response.content
                
                if self.sitemap_url.endswith(".gz"):
                    # Decompress the content
                    content = gzip.decompress(content)
                
                # Parse the XML
                if b"<sitemapindex" in content:
                    # This is a sitemap index
                    self.process_sitemap_index(content)
                else:
                    # This is a regular sitemap
                    self.process_sitemap(content)
            else:
                self.logger.error(f"Error processing sitemap: HTTP {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error processing sitemap: {str(e)}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Return the results
        return {
            "sitemap_url": self.sitemap_url,
            "urls": self.urls,
            "sitemap_index_urls": self.sitemap_index_urls,
            "total_urls": len(self.urls),
            "total_sitemap_index_urls": len(self.sitemap_index_urls),
            "processing_time": processing_time,
        }
    
    def process_sitemap_index(self, content):
        """
        Process a sitemap index.
        
        Args:
            content (bytes): The sitemap index content
        """
        self.logger.info("Processing sitemap index")
        
        try:
            # Parse the XML
            root = ET.fromstring(content)
            
            # Find all sitemap elements
            ns = self.get_namespace(root)
            sitemap_elements = root.findall(f".//{ns}sitemap")
            
            # Process each sitemap
            for sitemap_element in sitemap_elements:
                # Get the loc element
                loc_element = sitemap_element.find(f"{ns}loc")
                
                if loc_element is not None:
                    # Get the URL
                    url = loc_element.text.strip()
                    
                    # Add the URL to the sitemap index URLs
                    self.sitemap_index_urls.append(url)
                    
                    # Process the sitemap
                    processor = SitemapProcessor(url, self.timeout, self.user_agent)
                    result = processor.process()
                    
                    # Add the URLs to our list
                    self.urls.extend(result["urls"])
        except Exception as e:
            self.logger.error(f"Error processing sitemap index: {str(e)}")
    
    def process_sitemap(self, content):
        """
        Process a sitemap.
        
        Args:
            content (bytes): The sitemap content
        """
        self.logger.info("Processing sitemap")
        
        try:
            # Parse the XML
            root = ET.fromstring(content)
            
            # Find all url elements
            ns = self.get_namespace(root)
            url_elements = root.findall(f".//{ns}url")
            
            # Process each URL
            for url_element in url_elements:
                # Get the loc element
                loc_element = url_element.find(f"{ns}loc")
                
                if loc_element is not None:
                    # Get the URL
                    url = loc_element.text.strip()
                    
                    # Add the URL to the list
                    self.urls.append(url)
        except Exception as e:
            self.logger.error(f"Error processing sitemap: {str(e)}")
    
    def get_namespace(self, element):
        """
        Get the namespace from an XML element.
        
        Args:
            element (Element): The XML element
        
        Returns:
            str: The namespace
        """
        # Get the namespace
        m = re.match(r'\{.*\}', element.tag)
        
        if m:
            # Return the namespace with curly braces
            return m.group(0)
        
        return ""
