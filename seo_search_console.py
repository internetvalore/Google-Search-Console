#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Search Console module for the SEO Analysis Tool.
Contains classes for loading and analyzing Search Console data.
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

class SearchConsoleData:
    """Class for loading and processing Search Console data."""
    
    def __init__(self, file_path):
        """
        Initialize the Search Console data loader.
        
        Args:
            file_path (str): The path to the Search Console CSV file
        """
        self.file_path = file_path
        self.data = None
        self.queries = []
        self.landing_pages = []
        
        self.logger = logging.getLogger(__name__)
    
    def load(self):
        """
        Load the Search Console data.
        
        Returns:
            dict: The load results
        """
        self.logger.info(f"Loading Search Console data from: {self.file_path}")
        
        try:
            # Load the CSV file
            self.data = pd.read_csv(self.file_path)
            
            # Check if the required columns are present
            required_columns = ["Query", "Landing Page", "Impressions", "Url Clicks", "Average Position"]
            
            for column in required_columns:
                if column not in self.data.columns:
                    self.logger.error(f"Required column not found: {column}")
                    return {
                        "success": False,
                        "message": f"Required column not found: {column}",
                    }
            
            # Clean the data
            self.clean_data()
            
            # Extract queries and landing pages
            self.extract_queries_and_landing_pages()
            
            # Return the results
            return {
                "success": True,
                "message": "Search Console data loaded successfully",
                "file_path": self.file_path,
                "total_queries": len(self.queries),
                "total_landing_pages": len(self.landing_pages),
                "total_impressions": self.data["Impressions"].sum(),
                "total_clicks": self.data["Url Clicks"].sum(),
                "avg_position": self.data["Average Position"].mean(),
                "queries": self.queries,
                "landing_pages": self.landing_pages,
            }
        except Exception as e:
            self.logger.error(f"Error loading Search Console data: {str(e)}")
            return {
                "success": False,
                "message": f"Error loading Search Console data: {str(e)}",
            }
    
    def clean_data(self):
        """Clean the Search Console data."""
        # Remove rows with missing values
        self.data = self.data.dropna(subset=["Query", "Landing Page", "Impressions", "Url Clicks", "Average Position"])
        
        # Convert numeric columns to numeric types
        self.data["Impressions"] = pd.to_numeric(self.data["Impressions"], errors="coerce")
        self.data["Url Clicks"] = pd.to_numeric(self.data["Url Clicks"], errors="coerce")
        self.data["Average Position"] = pd.to_numeric(self.data["Average Position"], errors="coerce")
        
        # Remove rows with invalid numeric values
        self.data = self.data.dropna(subset=["Impressions", "Url Clicks", "Average Position"])
        
        # Add a Topic column if it doesn't exist
        if "Topic" not in self.data.columns:
            self.data["Topic"] = ""
    
    def extract_queries_and_landing_pages(self):
        """Extract queries and landing pages from the data."""
        # Group by query and aggregate metrics
        query_data = self.data.groupby("Query").agg({
            "Impressions": "sum",
            "Url Clicks": "sum",
            "Average Position": "mean",
        }).reset_index()
        
        # Sort by impressions in descending order
        query_data = query_data.sort_values("Impressions", ascending=False)
        
        # Convert to list of dictionaries
        self.queries = query_data.to_dict("records")
        
        # Group by landing page and aggregate metrics
        landing_page_data = self.data.groupby("Landing Page").agg({
            "Impressions": "sum",
            "Url Clicks": "sum",
            "Average Position": "mean",
        }).reset_index()
        
        # Sort by impressions in descending order
        landing_page_data = landing_page_data.sort_values("Impressions", ascending=False)
        
        # Convert to list of dictionaries
        self.landing_pages = landing_page_data.to_dict("records")
    
    def get_data(self):
        """
        Get the Search Console data.
        
        Returns:
            pandas.DataFrame: The data
        """
        return self.data
    
    def get_queries(self):
        """
        Get the queries.
        
        Returns:
            list: The queries
        """
        return self.queries
    
    def get_landing_pages(self):
        """
        Get the landing pages.
        
        Returns:
            list: The landing pages
        """
        return self.landing_pages
    
    def get_query_data(self, query):
        """
        Get data for a specific query.
        
        Args:
            query (str): The query
        
        Returns:
            pandas.DataFrame: The data for the query
        """
        return self.data[self.data["Query"] == query]
    
    def get_landing_page_data(self, landing_page):
        """
        Get data for a specific landing page.
        
        Args:
            landing_page (str): The landing page
        
        Returns:
            pandas.DataFrame: The data for the landing page
        """
        return self.data[self.data["Landing Page"] == landing_page]
    
    def to_dataframe(self):
        """
        Convert the data to a pandas DataFrame.
        
        Returns:
            pandas.DataFrame: The DataFrame
        """
        return self.data


class SearchConsoleAnalyzer:
    """Class for analyzing Search Console data."""
    
    def __init__(self, search_console_data):
        """
        Initialize the Search Console analyzer.
        
        Args:
            search_console_data (SearchConsoleData): The Search Console data
        """
        self.search_console_data = search_console_data
        self.data = search_console_data.get_data()
        
        self.clusters = []
        self.topics = {}
        
        self.logger = logging.getLogger(__name__)
    
    def analyze(self):
        """
        Analyze the Search Console data.
        
        Returns:
            dict: The analysis results
        """
        self.logger.info("Analyzing Search Console data")
        
        # Cluster queries
        self.cluster_queries()
        
        # Identify topics
        self.identify_topics()
        
        # Return the results
        return {
            "clusters": self.clusters,
            "topics": self.topics,
        }
    
    def cluster_queries(self, n_clusters=10):
        """
        Cluster queries using TF-IDF and K-means.
        
        Args:
            n_clusters (int): The number of clusters
        """
        # Get the queries
        queries = self.data["Query"].tolist()
        
        # Create a TF-IDF vectorizer
        vectorizer = TfidfVectorizer(max_features=100)
        
        # Transform the queries
        tfidf_matrix = vectorizer.fit_transform(queries)
        
        # Cluster the queries
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(tfidf_matrix)
        
        # Add the cluster to the data
        self.data["Cluster"] = clusters
        
        # Extract cluster information
        cluster_data = []
        
        for cluster_id in range(n_clusters):
            # Get the queries in this cluster
            cluster_queries = self.data[self.data["Cluster"] == cluster_id]
            
            # Skip empty clusters
            if len(cluster_queries) == 0:
                continue
            
            # Get the top 5 queries by impressions
            top_queries = cluster_queries.sort_values("Impressions", ascending=False).head(5)["Query"].tolist()
            
            # Calculate metrics for this cluster
            impressions = cluster_queries["Impressions"].sum()
            clicks = cluster_queries["Url Clicks"].sum()
            avg_position = cluster_queries["Average Position"].mean()
            
            # Add the cluster to the list
            cluster_data.append({
                "cluster_id": cluster_id,
                "queries": len(cluster_queries),
                "impressions": impressions,
                "clicks": clicks,
                "avg_position": avg_position,
                "top_queries": top_queries,
            })
        
        # Sort clusters by impressions in descending order
        self.clusters = sorted(cluster_data, key=lambda x: x["impressions"], reverse=True)
    
    def identify_topics(self):
        """Identify topics for landing pages based on clustered queries."""
        # Group by landing page and cluster
        landing_page_clusters = self.data.groupby(["Landing Page", "Cluster"]).agg({
            "Impressions": "sum",
        }).reset_index()
        
        # Find the dominant cluster for each landing page
        for landing_page in self.data["Landing Page"].unique():
            # Get the clusters for this landing page
            page_clusters = landing_page_clusters[landing_page_clusters["Landing Page"] == landing_page]
            
            # Skip landing pages with no clusters
            if len(page_clusters) == 0:
                continue
            
            # Find the dominant cluster
            dominant_cluster = page_clusters.loc[page_clusters["Impressions"].idxmax()]["Cluster"]
            
            # Get the top queries for this cluster
            cluster_data = next((c for c in self.clusters if c["cluster_id"] == dominant_cluster), None)
            
            if cluster_data:
                # Use the top queries as the topic
                self.topics[landing_page] = cluster_data["top_queries"]
    
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
    
    def get_landing_page_topic(self, landing_page):
        """
        Get the topic for a landing page.
        
        Args:
            landing_page (str): The landing page
        
        Returns:
            list: The topic
        """
        return self.topics.get(landing_page, [])
    
    def suggest_internal_links(self):
        """
        Suggest internal links based on topics.
        
        Returns:
            list: The suggested links
        """
        suggestions = []
        
        # Group landing pages by topic
        topic_pages = {}
        
        for landing_page, topic in self.topics.items():
            # Convert the topic to a string for grouping
            topic_str = ", ".join(topic)
            
            if topic_str not in topic_pages:
                topic_pages[topic_str] = []
            
            topic_pages[topic_str].append(landing_page)
        
        # Suggest links between pages with the same topic
        for topic, pages in topic_pages.items():
            # Skip topics with only one page
            if len(pages) <= 1:
                continue
            
            # Suggest links between all pages
            for i, source in enumerate(pages):
                for target in pages[i+1:]:
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


class SearchConsoleComparison:
    """Class for comparing two Search Console datasets."""
    
    def __init__(self, old_data, new_data):
        """
        Initialize the Search Console comparison.
        
        Args:
            old_data (SearchConsoleData): The old Search Console data
            new_data (SearchConsoleData): The new Search Console data
        """
        self.old_data = old_data
        self.new_data = new_data
        
        self.query_comparison = None
        self.landing_page_comparison = None
        
        self.logger = logging.getLogger(__name__)
    
    def compare(self):
        """
        Compare the two Search Console datasets.
        
        Returns:
            dict: The comparison results
        """
        self.logger.info("Comparing Search Console datasets")
        
        # Compare queries
        self.compare_queries()
        
        # Compare landing pages
        self.compare_landing_pages()
        
        # Return the results
        return {
            "query_comparison": self.query_comparison,
            "landing_page_comparison": self.landing_page_comparison,
        }
    
    def compare_queries(self):
        """Compare queries between the two datasets."""
        # Get the data
        old_data = self.old_data.get_data()
        new_data = self.new_data.get_data()
        
        # Group by query and aggregate metrics
        old_queries = old_data.groupby("Query").agg({
            "Impressions": "sum",
            "Url Clicks": "sum",
            "Average Position": "mean",
        }).reset_index()
        
        new_queries = new_data.groupby("Query").agg({
            "Impressions": "sum",
            "Url Clicks": "sum",
            "Average Position": "mean",
        }).reset_index()
        
        # Merge the data
        merged = pd.merge(old_queries, new_queries, on="Query", how="outer", suffixes=("_old", "_new"))
        
        # Fill missing values with 0
        merged = merged.fillna(0)
        
        # Calculate changes
        merged["Impressions_change"] = merged["Impressions_new"] - merged["Impressions_old"]
        merged["Impressions_change_pct"] = (merged["Impressions_change"] / merged["Impressions_old"]) * 100
        merged["Url Clicks_change"] = merged["Url Clicks_new"] - merged["Url Clicks_old"]
        merged["Url Clicks_change_pct"] = (merged["Url Clicks_change"] / merged["Url Clicks_old"]) * 100
        merged["Average Position_change"] = merged["Average Position_new"] - merged["Average Position_old"]
        
        # Replace infinity with 0
        merged = merged.replace([np.inf, -np.inf], 0)
        
        # Sort by impressions change in descending order
        merged = merged.sort_values("Impressions_change", ascending=False)
        
        # Store the comparison
        self.query_comparison = merged
    
    def compare_landing_pages(self):
        """Compare landing pages between the two datasets."""
        # Get the data
        old_data = self.old_data.get_data()
        new_data = self.new_data.get_data()
        
        # Group by landing page and aggregate metrics
        old_landing_pages = old_data.groupby("Landing Page").agg({
            "Impressions": "sum",
            "Url Clicks": "sum",
            "Average Position": "mean",
        }).reset_index()
        
        new_landing_pages = new_data.groupby("Landing Page").agg({
            "Impressions": "sum",
            "Url Clicks": "sum",
            "Average Position": "mean",
        }).reset_index()
        
        # Merge the data
        merged = pd.merge(old_landing_pages, new_landing_pages, on="Landing Page", how="outer", suffixes=("_old", "_new"))
        
        # Fill missing values with 0
        merged = merged.fillna(0)
        
        # Calculate changes
        merged["Impressions_change"] = merged["Impressions_new"] - merged["Impressions_old"]
        merged["Impressions_change_pct"] = (merged["Impressions_change"] / merged["Impressions_old"]) * 100
        merged["Url Clicks_change"] = merged["Url Clicks_new"] - merged["Url Clicks_old"]
        merged["Url Clicks_change_pct"] = (merged["Url Clicks_change"] / merged["Url Clicks_old"]) * 100
        merged["Average Position_change"] = merged["Average Position_new"] - merged["Average Position_old"]
        
        # Replace infinity with 0
        merged = merged.replace([np.inf, -np.inf], 0)
        
        # Sort by impressions change in descending order
        merged = merged.sort_values("Impressions_change", ascending=False)
        
        # Store the comparison
        self.landing_page_comparison = merged
    
    def get_query_comparison(self):
        """
        Get the query comparison.
        
        Returns:
            pandas.DataFrame: The query comparison
        """
        return self.query_comparison
    
    def get_landing_page_comparison(self):
        """
        Get the landing page comparison.
        
        Returns:
            pandas.DataFrame: The landing page comparison
        """
        return self.landing_page_comparison
    
    def get_improved_queries(self):
        """
        Get queries that have improved.
        
        Returns:
            pandas.DataFrame: The improved queries
        """
        return self.query_comparison[self.query_comparison["Impressions_change"] > 0]
    
    def get_declined_queries(self):
        """
        Get queries that have declined.
        
        Returns:
            pandas.DataFrame: The declined queries
        """
        return self.query_comparison[self.query_comparison["Impressions_change"] < 0]
    
    def get_improved_landing_pages(self):
        """
        Get landing pages that have improved.
        
        Returns:
            pandas.DataFrame: The improved landing pages
        """
        return self.landing_page_comparison[self.landing_page_comparison["Impressions_change"] > 0]
    
    def get_declined_landing_pages(self):
        """
        Get landing pages that have declined.
        
        Returns:
            pandas.DataFrame: The declined landing pages
        """
        return self.landing_page_comparison[self.landing_page_comparison["Impressions_change"] < 0]
    
    def to_dataframe(self):
        """
        Convert the comparison results to a pandas DataFrame.
        
        Returns:
            dict: The DataFrames
        """
        return {
            "query_comparison": self.query_comparison,
            "landing_page_comparison": self.landing_page_comparison,
        }
