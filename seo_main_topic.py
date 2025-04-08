#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main topic analyzer module for the SEO Analysis Tool.
Contains classes for analyzing the main topics of web pages.
"""

import logging
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import spacy
import string

class MainTopicAnalyzer:
    """Class for analyzing the main topics of web pages."""
    
    def __init__(self, content_loader):
        """
        Initialize the main topic analyzer.
        
        Args:
            content_loader (ContentLoader): The content loader
        """
        self.content_loader = content_loader
        self.urls = content_loader.urls
        
        self.main_topics = {}
        self.keywords = {}
        self.topic_distribution = {}
        
        self.logger = logging.getLogger(__name__)
        
        # Download NLTK resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        # Explicitly download punkt_tab if it's being requested
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            try:
                nltk.download('punkt_tab')
            except:
                # If punkt_tab doesn't exist, we'll handle it in preprocess_text
                self.logger.warning("Could not download punkt_tab resource, will use alternative tokenization")
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        # Initialize NLP components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Load spaCy model
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            # If the model is not installed, download it
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
            self.nlp = spacy.load('en_core_web_sm')
    
    def analyze(self):
        """
        Analyze the main topics of web pages.
        
        Returns:
            dict: The analysis results
        """
        self.logger.info("Analyzing main topics")
        
        # Extract text from each URL
        texts = {}
        for url in self.urls:
            text = self.extract_text(url)
            if text:
                texts[url] = text
        
        # Preprocess the texts
        preprocessed_texts = {url: self.preprocess_text(text) for url, text in texts.items()}
        
        # Extract keywords
        self.extract_keywords(preprocessed_texts)
        
        # Identify main topics
        self.identify_main_topics(preprocessed_texts)
        
        # Calculate topic distribution
        self.calculate_topic_distribution()
        
        # Count URLs with topics identified
        topics_identified = sum(1 for topics in self.main_topics.values() if topics)
        
        # Return the results
        return {
            "total_urls": len(self.urls),
            "topics_identified": topics_identified,
            "main_topics": list(self.topic_distribution.keys()),
            "topic_distribution": self.topic_distribution,
            "keywords": list(set(keyword for keywords in self.keywords.values() for keyword in keywords)),
            "url_topics": self.main_topics,
            "url_keywords": self.keywords,
        }
    
    def extract_text(self, url):
        """
        Extract text from a web page.
        
        Args:
            url (str): The URL
        
        Returns:
            str: The extracted text
        """
        # Get the soup
        soup = self.content_loader.get_soup(url)
        
        if not soup:
            self.logger.warning(f"No content for URL: {url}")
            return ""
        
        # Extract title
        title = soup.find("title")
        title_text = title.text.strip() if title else ""
        
        # Extract meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_desc_text = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
        
        # Extract headings
        h1_tags = soup.find_all("h1")
        h1_text = " ".join(h1.text.strip() for h1 in h1_tags)
        
        h2_tags = soup.find_all("h2")
        h2_text = " ".join(h2.text.strip() for h2 in h2_tags)
        
        # Extract main content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        content_text = " ".join(chunk for chunk in chunks if chunk)
        
        # Combine all text
        all_text = f"{title_text} {meta_desc_text} {h1_text} {h2_text} {content_text}"
        
        return all_text
    
    def preprocess_text(self, text):
        """
        Preprocess text for analysis.
        
        Args:
            text (str): The text to preprocess
        
        Returns:
            str: The preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))
        
        # Tokenize - use a fallback method if word_tokenize fails
        try:
            tokens = word_tokenize(text)
        except LookupError:
            # Simple fallback tokenization
            self.logger.warning("Using fallback tokenization method")
            tokens = text.split()
        
        # Remove stop words
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # Join tokens
        preprocessed_text = " ".join(tokens)
        
        return preprocessed_text
    
    def extract_keywords(self, preprocessed_texts):
        """
        Extract keywords from preprocessed texts.
        
        Args:
            preprocessed_texts (dict): The preprocessed texts
        """
        # Use TF-IDF to extract keywords
        vectorizer = TfidfVectorizer(max_features=100)
        tfidf_matrix = vectorizer.fit_transform(preprocessed_texts.values())
        
        # Get feature names
        feature_names = vectorizer.get_feature_names_out()
        
        # Extract keywords for each URL
        for i, url in enumerate(preprocessed_texts.keys()):
            # Get the TF-IDF scores for this document
            tfidf_scores = tfidf_matrix[i].toarray()[0]
            
            # Get the indices of the top 10 scores
            top_indices = tfidf_scores.argsort()[-10:][::-1]
            
            # Get the keywords
            keywords = [feature_names[idx] for idx in top_indices]
            
            # Store the keywords
            self.keywords[url] = keywords
    
    def identify_main_topics(self, preprocessed_texts):
        """
        Identify main topics from preprocessed texts.
        
        Args:
            preprocessed_texts (dict): The preprocessed texts
        """
        # Use spaCy to extract entities and noun chunks
        for url, text in preprocessed_texts.items():
            # Process the text with spaCy
            doc = self.nlp(text)
            
            # Extract entities
            entities = [ent.text for ent in doc.ents]
            
            # Extract noun chunks
            noun_chunks = [chunk.text for chunk in doc.noun_chunks]
            
            # Combine entities and noun chunks
            topics = entities + noun_chunks
            
            # Count the frequency of each topic
            topic_counts = Counter(topics)
            
            # Get the top 5 topics
            top_topics = [topic for topic, _ in topic_counts.most_common(5)]
            
            # Store the topics
            self.main_topics[url] = top_topics
    
    def calculate_topic_distribution(self):
        """Calculate the distribution of topics across all URLs."""
        # Count the frequency of each topic
        topic_counts = Counter()
        
        for topics in self.main_topics.values():
            topic_counts.update(topics)
        
        # Calculate the total number of topics
        total_topics = sum(topic_counts.values())
        
        # Calculate the distribution
        if total_topics > 0:
            self.topic_distribution = {topic: count / total_topics for topic, count in topic_counts.most_common()}
    
    def get_main_topics(self, url):
        """
        Get the main topics for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The main topics
        """
        return self.main_topics.get(url, [])
    
    def get_keywords(self, url):
        """
        Get the keywords for a URL.
        
        Args:
            url (str): The URL
        
        Returns:
            list: The keywords
        """
        return self.keywords.get(url, [])
    
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
                "Main Topics": ", ".join(self.get_main_topics(url)),
                "Keywords": ", ".join(self.get_keywords(url)),
            })
        
        return pd.DataFrame(data)
