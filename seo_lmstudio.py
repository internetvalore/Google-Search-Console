#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LM Studio integration module for the SEO Analysis Tool.
Contains classes for interacting with the LM Studio API.
"""

import logging
import requests
import json
import time
import os
from typing import List, Dict, Any, Optional

class LMStudioClient:
    """Class for interacting with the LM Studio API."""
    
    def __init__(self, api_url="http://localhost:1234/v1"):
        """
        Initialize the LM Studio client.
        
        Args:
            api_url (str): The URL of the LM Studio API
        """
        self.api_url = api_url
        self.logger = logging.getLogger(__name__)
    
    def generate_text(self, prompt, max_tokens=500, temperature=0.7, top_p=0.95, stop=None):
        """
        Generate text using the LM Studio API.
        
        Args:
            prompt (str): The prompt to generate text from
            max_tokens (int): The maximum number of tokens to generate
            temperature (float): The temperature for sampling
            top_p (float): The top-p value for nucleus sampling
            stop (list): A list of strings to stop generation at
        
        Returns:
            dict: The generation results
        """
        self.logger.info("Generating text with LM Studio")
        
        try:
            # Prepare the request
            url = f"{self.api_url}/completions"
            
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": stop or [],
            }
            
            headers = {
                "Content-Type": "application/json",
            }
            
            # Send the request
            response = requests.post(url, json=payload, headers=headers)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the response
                result = response.json()
                
                # Extract the generated text
                text = result.get("choices", [{}])[0].get("text", "")
                
                return {
                    "success": True,
                    "text": text,
                    "result": result,
                }
            else:
                self.logger.error(f"Error generating text: {response.status_code} {response.text}")
                return {
                    "success": False,
                    "message": f"Error generating text: {response.status_code} {response.text}",
                }
        except Exception as e:
            self.logger.error(f"Error generating text: {str(e)}")
            return {
                "success": False,
                "message": f"Error generating text: {str(e)}",
            }
    
    def generate_chat_completion(self, messages, max_tokens=500, temperature=0.7, top_p=0.95, stop=None):
        """
        Generate a chat completion using the LM Studio API.
        
        Args:
            messages (list): A list of message objects
            max_tokens (int): The maximum number of tokens to generate
            temperature (float): The temperature for sampling
            top_p (float): The top-p value for nucleus sampling
            stop (list): A list of strings to stop generation at
        
        Returns:
            dict: The generation results
        """
        self.logger.info("Generating chat completion with LM Studio")
        
        try:
            # Prepare the request
            url = f"{self.api_url}/chat/completions"
            
            payload = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": stop or [],
            }
            
            headers = {
                "Content-Type": "application/json",
            }
            
            # Send the request
            response = requests.post(url, json=payload, headers=headers)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the response
                result = response.json()
                
                # Extract the generated text
                text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                return {
                    "success": True,
                    "text": text,
                    "result": result,
                }
            else:
                self.logger.error(f"Error generating chat completion: {response.status_code} {response.text}")
                return {
                    "success": False,
                    "message": f"Error generating chat completion: {response.status_code} {response.text}",
                }
        except Exception as e:
            self.logger.error(f"Error generating chat completion: {str(e)}")
            return {
                "success": False,
                "message": f"Error generating chat completion: {str(e)}",
            }
    
    def check_connection(self):
        """
        Check if the LM Studio API is available.
        
        Returns:
            bool: True if the API is available, False otherwise
        """
        try:
            # Prepare the request
            url = f"{self.api_url}/models"
            
            # Send the request
            response = requests.get(url)
            
            # Check if the request was successful
            return response.status_code == 200
        except Exception:
            return False


class MetaDescriptionGenerator:
    """Class for generating meta descriptions using LM Studio."""
    
    def __init__(self, lm_studio_client):
        """
        Initialize the meta description generator.
        
        Args:
            lm_studio_client (LMStudioClient): The LM Studio client
        """
        self.lm_studio_client = lm_studio_client
        self.logger = logging.getLogger(__name__)
    
    def generate_meta_description(self, url, title, content, max_length=160):
        """
        Generate a meta description for a URL.
        
        Args:
            url (str): The URL
            title (str): The page title
            content (str): The page content
            max_length (int): The maximum length of the meta description
        
        Returns:
            dict: The generation results
        """
        self.logger.info(f"Generating meta description for URL: {url}")
        
        # Prepare the prompt
        prompt = f"""
        Write a compelling meta description for the following web page. The meta description should be concise, informative, and include relevant keywords. It should accurately summarize the page content and entice users to click through from search results.

        URL: {url}
        Title: {title}
        
        Page Content (excerpt):
        {content[:1000]}...
        
        Meta Description (max {max_length} characters):
        """
        
        # Generate the meta description
        result = self.lm_studio_client.generate_text(
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
            top_p=0.95,
            stop=["\n\n"],
        )
        
        if not result["success"]:
            return result
        
        # Extract the meta description
        meta_description = result["text"].strip()
        
        # Truncate the meta description if it's too long
        if len(meta_description) > max_length:
            meta_description = meta_description[:max_length].rsplit(" ", 1)[0] + "..."
        
        return {
            "success": True,
            "meta_description": meta_description,
            "url": url,
        }
    
    def generate_meta_descriptions_batch(self, urls, titles, contents, max_length=160):
        """
        Generate meta descriptions for multiple URLs.
        
        Args:
            urls (list): The URLs
            titles (list): The page titles
            contents (list): The page contents
            max_length (int): The maximum length of the meta descriptions
        
        Returns:
            list: The generation results
        """
        self.logger.info(f"Generating meta descriptions for {len(urls)} URLs")
        
        results = []
        
        for i, (url, title, content) in enumerate(zip(urls, titles, contents)):
            # Generate the meta description
            result = self.generate_meta_description(url, title, content, max_length)
            
            # Add the result to the list
            results.append(result)
            
            # Log progress
            self.logger.info(f"Generated meta description {i+1}/{len(urls)}")
            
            # Sleep to avoid rate limiting
            if i < len(urls) - 1:
                time.sleep(1)
        
        return results


class ContentGenerator:
    """Class for generating content using LM Studio."""
    
    def __init__(self, lm_studio_client):
        """
        Initialize the content generator.
        
        Args:
            lm_studio_client (LMStudioClient): The LM Studio client
        """
        self.lm_studio_client = lm_studio_client
        self.logger = logging.getLogger(__name__)
    
    def generate_content(self, topic, keywords, length="medium", tone="informative"):
        """
        Generate content for a topic.
        
        Args:
            topic (str): The topic
            keywords (list): The keywords to include
            length (str): The length of the content (short, medium, long)
            tone (str): The tone of the content (informative, persuasive, conversational)
        
        Returns:
            dict: The generation results
        """
        self.logger.info(f"Generating content for topic: {topic}")
        
        # Map length to token count
        length_map = {
            "short": 200,
            "medium": 500,
            "long": 1000,
        }
        
        max_tokens = length_map.get(length, 500)
        
        # Prepare the prompt
        prompt = f"""
        Write a {length} article about {topic} in a {tone} tone. Include the following keywords: {', '.join(keywords)}.
        
        Article:
        """
        
        # Generate the content
        result = self.lm_studio_client.generate_text(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
        )
        
        if not result["success"]:
            return result
        
        # Extract the content
        content = result["text"].strip()
        
        return {
            "success": True,
            "content": content,
            "topic": topic,
            "keywords": keywords,
        }
    
    def generate_ads_question(self, topic, keywords):
        """
        Generate an ADS question for a topic.
        
        Args:
            topic (str): The topic
            keywords (list): The keywords to include
        
        Returns:
            dict: The generation results
        """
        self.logger.info(f"Generating ADS question for topic: {topic}")
        
        # Prepare the prompt
        prompt = f"""
        Generate an ADS (Audience, Desire, Solution) question for the topic: {topic}. The question should address the audience's pain points, desires, and hint at a solution. Include the following keywords: {', '.join(keywords)}.
        
        ADS Question:
        """
        
        # Generate the question
        result = self.lm_studio_client.generate_text(
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
            top_p=0.95,
            stop=["\n\n"],
        )
        
        if not result["success"]:
            return result
        
        # Extract the question
        question = result["text"].strip()
        
        return {
            "success": True,
            "question": question,
            "topic": topic,
            "keywords": keywords,
        }
