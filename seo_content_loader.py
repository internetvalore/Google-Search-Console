#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Content loader module for the SEO Analysis Tool.
Contains classes for loading content from URLs.
"""

import requests
import logging
import time
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import concurrent.futures

class ContentLoader:
    """Class for loading content from URLs."""
    
    def __init__(self, urls, max_concurrent=10, timeout=30):
        """
        Initialize the content loader.
        
        Args:
            urls (list): The URLs to load content from
            max_concurrent (int): The maximum number of concurrent requests
            timeout (int): The timeout for requests in seconds
        """
        self.urls = urls
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        
        self.content = {}
        self.status_codes = {}
        self.content_types = {}
        self.content_lengths = {}
        
        self.logger = logging.getLogger(__name__)
    
    def load_content(self):
        """
        Load content from URLs.
        
        Returns:
            dict: The load results
        """
        start_time = time.time()
        
        # Load content asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async load function
            loop.run_until_complete(self.async_load_content())
        finally:
            # Close the event loop
            loop.close()
        
        # Calculate load time
        load_time = time.time() - start_time
        
        # Return the results
        return {
            "loaded_urls": list(self.content.keys()),
            "total_urls": len(self.content),
            "load_time": load_time,
            "content": self.content,
            "status_codes": self.status_codes,
            "content_types": self.content_types,
            "content_lengths": self.content_lengths,
        }
    
    async def async_load_content(self):
        """Load content from URLs asynchronously."""
        # Create a session
        async with aiohttp.ClientSession() as session:
            # Create tasks for each URL
            tasks = []
            for url in self.urls:
                task = asyncio.ensure_future(self.fetch_url(session, url))
                tasks.append(task)
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
    
    async def fetch_url(self, session, url):
        """
        Fetch a URL asynchronously.
        
        Args:
            session (aiohttp.ClientSession): The session to use
            url (str): The URL to fetch
        """
        try:
            # Fetch the URL
            async with session.get(url, timeout=self.timeout) as response:
                # Get the content
                content = await response.text()
                
                # Store the results
                self.content[url] = content
                self.status_codes[url] = response.status
                self.content_types[url] = response.headers.get("Content-Type", "")
                self.content_lengths[url] = len(content)
                
                self.logger.info(f"Loaded URL: {url} (status code: {response.status})")
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout fetching URL: {url}")
            
            # Store empty results
            self.content[url] = ""
            self.status_codes[url] = 0
            self.content_types[url] = ""
            self.content_lengths[url] = 0
        except Exception as e:
            self.logger.error(f"Error fetching URL: {url} ({str(e)})")
            
            # Store empty results
            self.content[url] = ""
            self.status_codes[url] = 0
            self.content_types[url] = ""
            self.content_lengths[url] = 0
    
    def load_content_sync(self):
        """
        Load content from URLs synchronously.
        
        Returns:
            dict: The load results
        """
        start_time = time.time()
        
        # Load content using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit tasks for each URL
            futures = {executor.submit(self.fetch_url_sync, url): url for url in self.urls}
            
            # Wait for all tasks to complete
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error fetching URL: {url} ({str(e)})")
        
        # Calculate load time
        load_time = time.time() - start_time
        
        # Return the results
        return {
            "loaded_urls": list(self.content.keys()),
            "total_urls": len(self.content),
            "load_time": load_time,
            "content": self.content,
            "status_codes": self.status_codes,
            "content_types": self.content_types,
            "content_lengths": self.content_lengths,
        }
    
    def fetch_url_sync(self, url):
        """
        Fetch a URL synchronously.
        
        Args:
            url (str): The URL to fetch
        """
        try:
            # Fetch the URL
            response = requests.get(url, timeout=self.timeout)
            
            # Store the results
            self.content[url] = response.text
            self.status_codes[url] = response.status_code
            self.content_types[url] = response.headers.get("Content-Type", "")
            self.content_lengths[url] = len(response.text)
            
            self.logger.info(f"Loaded URL: {url} (status code: {response.status_code})")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching URL: {url} ({str(e)})")
            
            # Store empty results
            self.content[url] = ""
            self.status_codes[url] = 0
            self.content_types[url] = ""
            self.content_lengths[url] = 0
    
    def get_content(self, url):
        """
        Get the content for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The content
        """
        return self.content.get(url, "")
    
    def get_status_code(self, url):
        """
        Get the status code for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            int: The status code
        """
        return self.status_codes.get(url, 0)
    
    def get_content_type(self, url):
        """
        Get the content type for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The content type
        """
        return self.content_types.get(url, "")
    
    def get_content_length(self, url):
        """
        Get the content length for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            int: The content length
        """
        return self.content_lengths.get(url, 0)
    
    def get_soup(self, url):
        """
        Get a BeautifulSoup object for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            BeautifulSoup: The BeautifulSoup object
        """
        content = self.get_content(url)
        
        if not content:
            return None
        
        return BeautifulSoup(content, "html.parser")
    
    def get_title(self, url):
        """
        Get the title for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The title
        """
        soup = self.get_soup(url)
        
        if not soup:
            return ""
        
        title_tag = soup.find("title")
        
        if not title_tag:
            return ""
        
        return title_tag.text.strip()
    
    def get_meta_description(self, url):
        """
        Get the meta description for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The meta description
        """
        soup = self.get_soup(url)
        
        if not soup:
            return ""
        
        meta_tag = soup.find("meta", attrs={"name": "description"})
        
        if not meta_tag:
            return ""
        
        return meta_tag.get("content", "").strip()
    
    def get_h1(self, url):
        """
        Get the H1 for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The H1
        """
        soup = self.get_soup(url)
        
        if not soup:
            return ""
        
        h1_tag = soup.find("h1")
        
        if not h1_tag:
            return ""
        
        return h1_tag.text.strip()
