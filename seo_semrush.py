#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SEMrush module for the SEO Analysis Tool.
Contains classes for loading and analyzing SEMrush data.
"""

import logging
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import re
import os
from datetime import datetime

class SEMrushData:
    """Class for loading and processing SEMrush data."""
    
    def __init__(self, file_path):
        """
        Initialize the SEMrush data loader.
        
        Args:
            file_path (str): The path to the SEMrush CSV file
        """
        self.file_path = file_path
        self.data = None
        self.keywords = []
        self.urls = []
        
        self.logger = logging.getLogger(__name__)
    
    def load(self):
        """
        Load the SEMrush data.
        
        Returns:
            dict: The load results
        """
        self.logger.info(f"Loading SEMrush data from: {self.file_path}")
        
        try:
            # Load the CSV file
            self.data = pd.read_csv(self.file_path)
            
            # Check if the required columns are present
            required_columns = ["Keyword", "Position", "Search Volume", "URL", "Traffic"]
            
            for column in required_columns:
                if column not in self.data.columns:
                    self.logger.error(f"Required column not found: {column}")
                    return {
                        "success": False,
                        "message": f"Required column not found: {column}",
                    }
            
            # Clean the data
            self.clean_data()
            
            # Extract keywords and URLs
            self.extract_keywords_and_urls()
            
            # Return the results
            return {
                "success": True,
                "message": "SEMrush data loaded successfully",
                "file_path": self.file_path,
                "total_keywords": len(self.keywords),
                "total_urls": len(self.urls),
                "total_traffic": self.data["Traffic"].sum(),
                "avg_position": self.data["Position"].mean(),
                "keywords": self.keywords,
                "urls": self.urls,
            }
        except Exception as e:
            self.logger.error(f"Error loading SEMrush data: {str(e)}")
            return {
                "success": False,
                "message": f"Error loading SEMrush data: {str(e)}",
            }
    
    def clean_data(self):
        """Clean the SEMrush data."""
        # Remove rows with missing values
        self.data = self.data.dropna(subset=["Keyword", "Position", "Search Volume", "URL", "Traffic"])
        
        # Convert numeric columns to numeric types
        self.data["Position"] = pd.to_numeric(self.data["Position"], errors="coerce")
        self.data["Search Volume"] = pd.to_numeric(self.data["Search Volume"], errors="coerce")
        self.data["Traffic"] = pd.to_numeric(self.data["Traffic"], errors="coerce")
        
        # Remove rows with invalid numeric values
        self.data = self.data.dropna(subset=["Position", "Search Volume", "Traffic"])
        
        # Add a Topic column if it doesn't exist
        if "Topic" not in self.data.columns:
            self.data["Topic"] = ""
    
    def extract_keywords_and_urls(self):
        """Extract keywords and URLs from the data."""
        # Group by keyword and aggregate metrics
        keyword_data = self.data.groupby("Keyword").agg({
            "Position": "mean",
            "Search Volume": "first",
            "Traffic": "sum",
        }).reset_index()
        
        # Sort by traffic in descending order
        keyword_data = keyword_data.sort_values("Traffic", ascending=False)
        
        # Convert to list of dictionaries
        self.keywords = keyword_data.to_dict("records")
        
        # Group by URL and aggregate metrics
        url_data = self.data.groupby("URL").agg({
            "Position": "mean",
            "Traffic": "sum",
        }).reset_index()
        
        # Sort by traffic in descending order
        url_data = url_data.sort_values("Traffic", ascending=False)
        
        # Convert to list of dictionaries
        self.urls = url_data.to_dict("records")
    
    def get_data(self):
        """
        Get the SEMrush data.
        
        Returns:
            pandas.DataFrame: The data
        """
        return self.data
    
    def get_keywords(self):
        """
        Get the keywords.
        
        Returns:
            list: The keywords
        """
        return self.keywords
    
    def get_urls(self):
        """
        Get the URLs.
        
        Returns:
            list: The URLs
        """
        return self.urls
    
    def get_keyword_data(self, keyword):
        """
        Get data for a specific keyword.
        
        Args:
            keyword (str): The keyword
        
        Returns:
            pandas.DataFrame: The data for the keyword
        """
        return self.data[self.data["Keyword"] == keyword]
    
    def get_url_data(self, url):
        """
        Get data for a specific URL.
        
        Args:
            url (str): The URL
        
        Returns:
            pandas.DataFrame: The data for the URL
        """
        return self.data[self.data["URL"] == url]
    
    def to_dataframe(self):
        """
        Convert the data to a pandas DataFrame.
        
        Returns:
            pandas.DataFrame: The DataFrame
        """
        return self.data


class SEMrushAnalyzer:
    """Class for analyzing SEMrush data."""
    
    def __init__(self, semrush_data):
        """
        Initialize the SEMrush analyzer.
        
        Args:
            semrush_data (SEMrushData): The SEMrush data
        """
        self.semrush_data = semrush_data
        self.data = semrush_data.get_data()
        
        self.clusters = []
        self.topics = {}
        self.visibility = {}
        self.traffic = {}
        
        self.logger = logging.getLogger(__name__)
    
    def analyze(self):
        """
        Analyze the SEMrush data.
        
        Returns:
            dict: The analysis results
        """
        self.logger.info("Analyzing SEMrush data")
        
        # Cluster keywords
        self.cluster_keywords()
        
        # Identify topics
        self.identify_topics()
        
        # Calculate visibility and traffic per topic
        self.calculate_visibility_and_traffic()
        
        # Return the results
        return {
            "clusters": self.clusters,
            "topics": self.topics,
            "visibility": self.visibility,
            "traffic": self.traffic,
        }
    
    def cluster_keywords(self, n_clusters=10):
        """
        Cluster keywords using TF-IDF and K-means.
        
        Args:
            n_clusters (int): The number of clusters
        """
        # Get the keywords
        keywords = self.data["Keyword"].tolist()
        
        # Create a TF-IDF vectorizer
        vectorizer = TfidfVectorizer(max_features=100)
        
        # Transform the keywords
        tfidf_matrix = vectorizer.fit_transform(keywords)
        
        # Cluster the keywords
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(tfidf_matrix)
        
        # Add the cluster to the data
        self.data["Cluster"] = clusters
        
        # Extract cluster information
        cluster_data = []
        
        for cluster_id in range(n_clusters):
            # Get the keywords in this cluster
            cluster_keywords = self.data[self.data["Cluster"] == cluster_id]
            
            # Skip empty clusters
            if len(cluster_keywords) == 0:
                continue
            
            # Get the top 5 keywords by traffic
            top_keywords = cluster_keywords.sort_values("Traffic", ascending=False).head(5)["Keyword"].tolist()
            
            # Calculate metrics for this cluster
            traffic = cluster_keywords["Traffic"].sum()
            avg_position = cluster_keywords["Position"].mean()
            search_volume = cluster_keywords["Search Volume"].sum()
            
            # Add the cluster to the list
            cluster_data.append({
                "cluster_id": cluster_id,
                "keywords": len(cluster_keywords),
                "traffic": traffic,
                "avg_position": avg_position,
                "search_volume": search_volume,
                "top_keywords": top_keywords,
            })
        
        # Sort clusters by traffic in descending order
        self.clusters = sorted(cluster_data, key=lambda x: x["traffic"], reverse=True)
    
    def identify_topics(self):
        """Identify topics for URLs based on clustered keywords."""
        # Group by URL and cluster
        url_clusters = self.data.groupby(["URL", "Cluster"]).agg({
            "Traffic": "sum",
        }).reset_index()
        
        # Find the dominant cluster for each URL
        for url in self.data["URL"].unique():
            # Get the clusters for this URL
            url_clusters_data = url_clusters[url_clusters["URL"] == url]
            
            # Skip URLs with no clusters
            if len(url_clusters_data) == 0:
                continue
            
            # Find the dominant cluster
            dominant_cluster = url_clusters_data.loc[url_clusters_data["Traffic"].idxmax()]["Cluster"]
            
            # Get the top keywords for this cluster
            cluster_data = next((c for c in self.clusters if c["cluster_id"] == dominant_cluster), None)
            
            if cluster_data:
                # Use the top keywords as the topic
                self.topics[url] = cluster_data["top_keywords"]
    
    def calculate_visibility_and_traffic(self):
        """Calculate visibility and traffic per topic."""
        # Group by topic
        topic_data = {}
        
        for url, topic_keywords in self.topics.items():
            # Convert the topic to a string for grouping
            topic_str = ", ".join(topic_keywords)
            
            if topic_str not in topic_data:
                topic_data[topic_str] = {
                    "urls": [],
                    "keywords": 0,
                    "traffic": 0,
                    "visibility": 0,
                }
            
            # Add the URL to the topic
            topic_data[topic_str]["urls"].append(url)
            
            # Get the keywords for this URL
            url_keywords = self.data[self.data["URL"] == url]
            
            # Add the number of keywords
            topic_data[topic_str]["keywords"] += len(url_keywords)
            
            # Add the traffic
            topic_data[topic_str]["traffic"] += url_keywords["Traffic"].sum()
            
            # Calculate visibility (percentage of keywords in top 10)
            top_10_keywords = len(url_keywords[url_keywords["Position"] <= 10])
            visibility = (top_10_keywords / len(url_keywords)) * 100 if len(url_keywords) > 0 else 0
            
            # Add the visibility
            topic_data[topic_str]["visibility"] += visibility
        
        # Calculate average visibility per topic
        for topic, data in topic_data.items():
            data["visibility"] = data["visibility"] / len(data["urls"]) if len(data["urls"]) > 0 else 0
        
        # Store the results
        self.visibility = {topic: data["visibility"] for topic, data in topic_data.items()}
        self.traffic = {topic: data["traffic"] for topic, data in topic_data.items()}
    
    def get_clusters(self):
        """
        Get the clusters.
        
        Returns:
            list: The clusters
        """
        return self.clusters
    
    def get_topics(self):
        """
        Get the topics.
        
        Returns:
            dict: The topics
        """
        return self.topics
    
    def get_url_topic(self, url):
        """
        Get the topic for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The topic
        """
        return self.topics.get(url, [])
    
    def get_visibility(self):
        """
        Get the visibility per topic.
        
        Returns:
            dict: The visibility
        """
        return self.visibility
    
    def get_traffic(self):
        """
        Get the traffic per topic.
        
        Returns:
            dict: The traffic
        """
        return self.traffic
    
    def suggest_internal_links(self):
        """
        Suggest internal links based on topics.
        
        Returns:
            list: The suggested links
        """
        suggestions = []
        
        # Group URLs by topic
        topic_urls = {}
        
        for url, topic in self.topics.items():
            # Convert the topic to a string for grouping
            topic_str = ", ".join(topic)
            
            if topic_str not in topic_urls:
                topic_urls[topic_str] = []
            
            topic_urls[topic_str].append(url)
        
        # Suggest links between URLs with the same topic
        for topic, urls in topic_urls.items():
            # Skip topics with only one URL
            if len(urls) <= 1:
                continue
            
            # Suggest links between all URLs
            for i, source in enumerate(urls):
                for target in urls[i+1:]:
                    suggestions.append({
                        "source": source,
                        "target": target,
                        "topic": topic,
                    })
        
        return suggestions
    
    def to_dataframe(self):
        """
        Convert the analysis results to a pandas DataFrame.
        
        Returns:
            pandas.DataFrame: The DataFrame
        """
        return self.data
