#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Report generator module for the SEO Analysis Tool.
Contains classes for generating reports.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import os
from datetime import datetime
import io
from wordcloud import WordCloud
import matplotlib.cm as cm
import matplotlib.colors as mcolors

class ReportGenerator:
    """Class for generating reports."""
    
    def __init__(self, output_dir="reports"):
        """
        Initialize the report generator.
        
        Args:
            output_dir (str): The output directory for reports
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_seo_report(self, url, meta_analyzer, image_analyzer, links_analyzer, reachability_analyzer, topic_analyzer, report_title=None):
        """
        Generate an SEO report.
        
        Args:
            url (str): The URL
            meta_analyzer (MetaDescriptionAnalyzer): The meta description analyzer
            image_analyzer (ImageAnalyzer): The image analyzer
            links_analyzer (LinksAnalyzer): The links analyzer
            reachability_analyzer (ReachabilityAnalyzer): The reachability analyzer
            topic_analyzer (MainTopicAnalyzer): The main topic analyzer
            report_title (str, optional): Custom report title. If None, a default title will be used.
        
        Returns:
            str: The path to the generated report
        """
        self.logger.info(f"Generating SEO report for URL: {url}")
        
        # Create a new document
        doc = Document()
        
        # Add styles
        self._add_styles(doc)
        
        # Add title
        if report_title:
            self._add_title(doc, report_title)
        else:
            self._add_title(doc, f"SEO Analysis Report: {url}")
        
        # Add date
        self._add_date(doc)
        
        # Add summary
        self._add_summary(doc, url, meta_analyzer, image_analyzer, links_analyzer, reachability_analyzer, topic_analyzer)
        
        # Add meta description analysis
        self._add_meta_description_analysis(doc, meta_analyzer)
        
        # Add image analysis
        self._add_image_analysis(doc, image_analyzer)
        
        # Add links analysis
        self._add_links_analysis(doc, links_analyzer)
        
        # Add reachability analysis
        self._add_reachability_analysis(doc, reachability_analyzer)
        
        # Add topic analysis
        self._add_topic_analysis(doc, topic_analyzer)
        
        # Add recommendations
        self._add_recommendations(doc, meta_analyzer, image_analyzer, links_analyzer, reachability_analyzer, topic_analyzer)
        
        # Save the document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seo_report_{timestamp}.docx"
        filepath = os.path.join(self.output_dir, filename)
        
        doc.save(filepath)
        
        self.logger.info(f"SEO report saved to: {filepath}")
        
        return filepath
    
    def generate_search_console_report(self, search_console_analyzer):
        """
        Generate a Search Console report.
        
        Args:
            search_console_analyzer (SearchConsoleAnalyzer): The Search Console analyzer
        
        Returns:
            str: The path to the generated report
        """
        self.logger.info("Generating Search Console report")
        
        # Create a new document
        doc = Document()
        
        # Add styles
        self._add_styles(doc)
        
        # Add title
        self._add_title(doc, "Search Console Analysis Report")
        
        # Add date
        self._add_date(doc)
        
        # Add clusters analysis
        self._add_clusters_analysis(doc, search_console_analyzer.get_clusters(), "Query")
        
        # Add topics analysis
        self._add_topics_analysis(doc, search_console_analyzer.get_topics())
        
        # Add internal link suggestions
        self._add_internal_link_suggestions(doc, search_console_analyzer.suggest_internal_links())
        
        # Save the document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"search_console_report_{timestamp}.docx"
        filepath = os.path.join(self.output_dir, filename)
        
        doc.save(filepath)
        
        self.logger.info(f"Search Console report saved to: {filepath}")
        
        return filepath
    
    def generate_semrush_report(self, semrush_analyzer):
        """
        Generate a SEMrush report.
        
        Args:
            semrush_analyzer (SEMrushAnalyzer): The SEMrush analyzer
        
        Returns:
            str: The path to the generated report
        """
        self.logger.info("Generating SEMrush report")
        
        # Create a new document
        doc = Document()
        
        # Add styles
        self._add_styles(doc)
        
        # Add title
        self._add_title(doc, "SEMrush Analysis Report")
        
        # Add date
        self._add_date(doc)
        
        # Add clusters analysis
        self._add_clusters_analysis(doc, semrush_analyzer.get_clusters(), "Keyword")
        
        # Add topics analysis
        self._add_topics_analysis(doc, semrush_analyzer.get_topics())
        
        # Add visibility and traffic analysis
        self._add_visibility_traffic_analysis(doc, semrush_analyzer.get_visibility(), semrush_analyzer.get_traffic())
        
        # Add internal link suggestions
        self._add_internal_link_suggestions(doc, semrush_analyzer.suggest_internal_links())
        
        # Save the document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"semrush_report_{timestamp}.docx"
        filepath = os.path.join(self.output_dir, filename)
        
        doc.save(filepath)
        
        self.logger.info(f"SEMrush report saved to: {filepath}")
        
        return filepath
    
    def generate_comparison_report(self, search_console_comparison):
        """
        Generate a comparison report.
        
        Args:
            search_console_comparison (SearchConsoleComparison): The Search Console comparison
        
        Returns:
            str: The path to the generated report
        """
        self.logger.info("Generating comparison report")
        
        # Create a new document
        doc = Document()
        
        # Add styles
        self._add_styles(doc)
        
        # Add title
        self._add_title(doc, "Search Console Comparison Report")
        
        # Add date
        self._add_date(doc)
        
        # Add query comparison
        self._add_query_comparison(doc, search_console_comparison.get_query_comparison())
        
        # Add landing page comparison
        self._add_landing_page_comparison(doc, search_console_comparison.get_landing_page_comparison())
        
        # Add improved queries
        self._add_improved_queries(doc, search_console_comparison.get_improved_queries())
        
        # Add declined queries
        self._add_declined_queries(doc, search_console_comparison.get_declined_queries())
        
        # Add improved landing pages
        self._add_improved_landing_pages(doc, search_console_comparison.get_improved_landing_pages())
        
        # Add declined landing pages
        self._add_declined_landing_pages(doc, search_console_comparison.get_declined_landing_pages())
        
        # Save the document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_report_{timestamp}.docx"
        filepath = os.path.join(self.output_dir, filename)
        
        doc.save(filepath)
        
        self.logger.info(f"Comparison report saved to: {filepath}")
        
        return filepath
    
    def generate_final_report(self, url, meta_analyzer, image_analyzer, links_analyzer, reachability_analyzer, topic_analyzer, search_console_analyzer=None, semrush_analyzer=None):
        """
        Generate a final report.
        
        Args:
            url (str): The URL
            meta_analyzer (MetaDescriptionAnalyzer): The meta description analyzer
            image_analyzer (ImageAnalyzer): The image analyzer
            links_analyzer (LinksAnalyzer): The links analyzer
            reachability_analyzer (ReachabilityAnalyzer): The reachability analyzer
            topic_analyzer (MainTopicAnalyzer): The main topic analyzer
            search_console_analyzer (SearchConsoleAnalyzer, optional): The Search Console analyzer
            semrush_analyzer (SEMrushAnalyzer, optional): The SEMrush analyzer
        
        Returns:
            str: The path to the generated report
        """
        self.logger.info(f"Generating final report for URL: {url}")
        
        # Create a new document
        doc = Document()
        
        # Add styles
        self._add_styles(doc)
        
        # Add title
        self._add_title(doc, f"SEO Final Report: {url}")
        
        # Add date
        self._add_date(doc)
        
        # Add executive summary
        self._add_executive_summary(doc, url, meta_analyzer, image_analyzer, links_analyzer, reachability_analyzer, topic_analyzer, search_console_analyzer, semrush_analyzer)
        
        # Add SEO analysis
        doc.add_heading("SEO Analysis", level=1)
        
        # Add meta description analysis
        self._add_meta_description_analysis(doc, meta_analyzer)
        
        # Add image analysis
        self._add_image_analysis(doc, image_analyzer)
        
        # Add links analysis
        self._add_links_analysis(doc, links_analyzer)
        
        # Add reachability analysis
        self._add_reachability_analysis(doc, reachability_analyzer)
        
        # Add topic analysis
        self._add_topic_analysis(doc, topic_analyzer)
        
        # Add Search Console analysis if available
        if search_console_analyzer:
            doc.add_heading("Search Console Analysis", level=1)
            self._add_clusters_analysis(doc, search_console_analyzer.get_clusters(), "Query")
            self._add_topics_analysis(doc, search_console_analyzer.get_topics())
        
        # Add SEMrush analysis if available
        if semrush_analyzer:
            doc.add_heading("SEMrush Analysis", level=1)
            self._add_clusters_analysis(doc, semrush_analyzer.get_clusters(), "Keyword")
            self._add_topics_analysis(doc, semrush_analyzer.get_topics())
            self._add_visibility_traffic_analysis(doc, semrush_analyzer.get_visibility(), semrush_analyzer.get_traffic())
        
        # Add internal link suggestions
        doc.add_heading("Internal Link Suggestions", level=1)
        
        if search_console_analyzer:
            self._add_internal_link_suggestions(doc, search_console_analyzer.suggest_internal_links(), "Search Console")
        
        if semrush_analyzer:
            self._add_internal_link_suggestions(doc, semrush_analyzer.suggest_internal_links(), "SEMrush")
        
        # Add recommendations
        self._add_recommendations(doc, meta_analyzer, image_analyzer, links_analyzer, reachability_analyzer, topic_analyzer, search_console_analyzer, semrush_analyzer)
        
        # Save the document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"final_report_{timestamp}.docx"
        filepath = os.path.join(self.output_dir, filename)
        
        doc.save(filepath)
        
        self.logger.info(f"Final report saved to: {filepath}")
        
        return filepath
    
    def _add_styles(self, doc):
        """
        Add styles to the document.
        
        Args:
            doc (Document): The document
        """
        # Add title style
        title_style = doc.styles.add_style("Title", WD_STYLE_TYPE.PARAGRAPH)
        title_style.font.name = "Arial"
        title_style.font.size = Pt(24)
        title_style.font.bold = True
        title_style.font.color.rgb = RGBColor(0, 0, 128)
        title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_style.paragraph_format.space_after = Pt(12)
        
        # Add heading 1 style
        heading1_style = doc.styles["Heading 1"]
        heading1_style.font.name = "Arial"
        heading1_style.font.size = Pt(18)
        heading1_style.font.bold = True
        heading1_style.font.color.rgb = RGBColor(0, 0, 128)
        heading1_style.paragraph_format.space_before = Pt(12)
        heading1_style.paragraph_format.space_after = Pt(6)
        
        # Add heading 2 style
        heading2_style = doc.styles["Heading 2"]
        heading2_style.font.name = "Arial"
        heading2_style.font.size = Pt(14)
        heading2_style.font.bold = True
        heading2_style.font.color.rgb = RGBColor(0, 0, 128)
        heading2_style.paragraph_format.space_before = Pt(12)
        heading2_style.paragraph_format.space_after = Pt(6)
        
        # Add normal style
        normal_style = doc.styles["Normal"]
        normal_style.font.name = "Arial"
        normal_style.font.size = Pt(11)
        normal_style.paragraph_format.space_after = Pt(6)
    
    def _add_title(self, doc, title):
        """
        Add a title to the document.
        
        Args:
            doc (Document): The document
            title (str): The title
        """
        doc.add_paragraph(title, style="Title")
    
    def _add_date(self, doc):
        """
        Add the current date to the document.
        
        Args:
            doc (Document): The document
        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_paragraph = doc.add_paragraph(f"Generated on: {date}")
        date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()
    
    def _add_summary(self, doc, url, meta_analyzer, image_analyzer, links_analyzer, reachability_analyzer, topic_analyzer):
        """
        Add a summary to the document.
        
        Args:
            doc (Document): The document
            url (str): The URL
            meta_analyzer (MetaDescriptionAnalyzer): The meta description analyzer
            image_analyzer (ImageAnalyzer): The image analyzer
            links_analyzer (LinksAnalyzer): The links analyzer
            reachability_analyzer (ReachabilityAnalyzer): The reachability analyzer
            topic_analyzer (MainTopicAnalyzer): The main topic analyzer
        """
        doc.add_heading("Summary", level=1)
        
        # Add URL
        doc.add_paragraph(f"URL: {url}")
        
        # Add meta description summary
        meta_desc_df = meta_analyzer.to_dataframe()
        urls_with_meta_desc = len(meta_desc_df[meta_desc_df["Has Meta Description"]])
        urls_without_meta_desc = len(meta_desc_df) - urls_with_meta_desc
        
        doc.add_paragraph(f"Meta Descriptions: {urls_with_meta_desc} URLs have meta descriptions, {urls_without_meta_desc} URLs don't have meta descriptions.")
        
        # Add image summary
        image_df = image_analyzer.to_dataframe()
        images_with_alt = len(image_df[image_df["Has Alt Text"]])
        images_without_alt = len(image_df) - images_with_alt
        
        doc.add_paragraph(f"Images: {len(image_df)} images found, {images_with_alt} have alt text, {images_without_alt} don't have alt text.")
        
        # Add links summary
        links_df = links_analyzer.to_dataframe()
        internal_links = len(links_df[links_df["Is Internal"]])
        external_links = len(links_df[links_df["Is External"]])
        broken_links = len(links_df[links_df["Is Broken"]])
        
        doc.add_paragraph(f"Links: {len(links_df)} links found, {internal_links} internal links, {external_links} external links, {broken_links} broken links.")
        
        # Add reachability summary
        reachability_df = reachability_analyzer.to_dataframe()
        reachable_urls = len(reachability_df[reachability_df["Is Reachable"]])
        orphan_pages = len(reachability_df[reachability_df["Is Orphan Page"]])
        
        doc.add_paragraph(f"Reachability: {reachable_urls} URLs are reachable from the home page, {orphan_pages} URLs are orphan pages.")
        
        # Add topic summary
        topic_df = topic_analyzer.to_dataframe()
        
        doc.add_paragraph(f"Topics: {len(topic_df)} URLs analyzed for topics.")
    
    def _add_meta_description_analysis(self, doc, meta_analyzer):
        """
        Add meta description analysis to the document.
        
        Args:
            doc (Document): The document
            meta_analyzer (MetaDescriptionAnalyzer): The meta description analyzer
        """
        doc.add_heading("Meta Description Analysis", level=1)
        
        # Get the data
        meta_desc_df = meta_analyzer.to_dataframe()
        
        # Add summary
        urls_with_meta_desc = len(meta_desc_df[meta_desc_df["Has Meta Description"]])
        urls_without_meta_desc = len(meta_desc_df) - urls_with_meta_desc
        
        doc.add_paragraph(f"URLs with meta descriptions: {urls_with_meta_desc}")
        doc.add_paragraph(f"URLs without meta descriptions: {urls_without_meta_desc}")
        
        # Add URLs without meta descriptions
        if urls_without_meta_desc > 0:
            doc.add_heading("URLs Without Meta Descriptions", level=2)
            
            urls_without_meta_desc_df = meta_desc_df[~meta_desc_df["Has Meta Description"]]
            
            for _, row in urls_without_meta_desc_df.iterrows():
                doc.add_paragraph(row["URL"], style="List Bullet")
        
        # Add URLs with short meta descriptions
        urls_with_short_meta_desc = len(meta_desc_df[meta_desc_df["Meta Description Quality"] == "too_short"])
        
        if urls_with_short_meta_desc > 0:
            doc.add_heading("URLs With Short Meta Descriptions", level=2)
            
            urls_with_short_meta_desc_df = meta_desc_df[meta_desc_df["Meta Description Quality"] == "too_short"]
            
            for _, row in urls_with_short_meta_desc_df.iterrows():
                doc.add_paragraph(f"{row['URL']} ({row['Meta Description Length']} characters)", style="List Bullet")
        
        # Add URLs with long meta descriptions
        urls_with_long_meta_desc = len(meta_desc_df[meta_desc_df["Meta Description Quality"] == "too_long"])
        
        if urls_with_long_meta_desc > 0:
            doc.add_heading("URLs With Long Meta Descriptions", level=2)
            
            urls_with_long_meta_desc_df = meta_desc_df[meta_desc_df["Meta Description Quality"] == "too_long"]
            
            for _, row in urls_with_long_meta_desc_df.iterrows():
                doc.add_paragraph(f"{row['URL']} ({row['Meta Description Length']} characters)", style="List Bullet")
    
    def _add_image_analysis(self, doc, image_analyzer):
        """
        Add image analysis to the document.
        
        Args:
            doc (Document): The document
            image_analyzer (ImageAnalyzer): The image analyzer
        """
        doc.add_heading("Image Analysis", level=1)
        
        # Get the data
        image_df = image_analyzer.to_dataframe()
        
        # Add summary
        images_with_alt = len(image_df[image_df["Has Alt Text"]])
        images_without_alt = len(image_df) - images_with_alt
        
        doc.add_paragraph(f"Images with alt text: {images_with_alt}")
        doc.add_paragraph(f"Images without alt text: {images_without_alt}")
        
        # Add images without alt text
        if images_without_alt > 0:
            doc.add_heading("Images Without Alt Text", level=2)
            
            images_without_alt_df = image_df[~image_df["Has Alt Text"]]
            
            for _, row in images_without_alt_df.iterrows():
                doc.add_paragraph(f"{row['URL']}: {row['Image Source']}", style="List Bullet")
        
        # Add large images
        large_images = len(image_df[image_df["Image Size"] > 100000])  # > 100 KB
        
        if large_images > 0:
            doc.add_heading("Large Images", level=2)
            
            large_images_df = image_df[image_df["Image Size"] > 100000]
            
            for _, row in large_images_df.iterrows():
                doc.add_paragraph(f"{row['URL']}: {row['Image Source']} ({row['Image Size'] / 1024:.1f} KB)", style="List Bullet")
    
    def _add_links_analysis(self, doc, links_analyzer):
        """
        Add links analysis to the document.
        
        Args:
            doc (Document): The document
            links_analyzer (LinksAnalyzer): The links analyzer
        """
        doc.add_heading("Links Analysis", level=1)
        
        # Get the data
        links_df = links_analyzer.to_dataframe()
        
        # Add summary
        internal_links = len(links_df[links_df["Is Internal"]])
        external_links = len(links_df[links_df["Is External"]])
        broken_links = len(links_df[links_df["Is Broken"]])
        nofollow_links = len(links_df[links_df["Is Nofollow"]])
        
        doc.add_paragraph(f"Internal links: {internal_links}")
        doc.add_paragraph(f"External links: {external_links}")
        doc.add_paragraph(f"Broken links: {broken_links}")
        doc.add_paragraph(f"Nofollow links: {nofollow_links}")
        
        # Add broken links
        if broken_links > 0:
            doc.add_heading("Broken Links", level=2)
            
            broken_links_df = links_df[links_df["Is Broken"]]
            
            for _, row in broken_links_df.iterrows():
                doc.add_paragraph(f"{row['URL']}: {row['Link']}", style="List Bullet")
    
    def _add_reachability_analysis(self, doc, reachability_analyzer):
        """
        Add reachability analysis to the document.
        
        Args:
            doc (Document): The document
            reachability_analyzer (ReachabilityAnalyzer): The reachability analyzer
        """
        doc.add_heading("Reachability Analysis", level=1)
        
        # Get the data
        reachability_df = reachability_analyzer.to_dataframe()
        
        # Add summary
        reachable_urls = len(reachability_df[reachability_df["Is Reachable"]])
        orphan_pages = len(reachability_df[reachability_df["Is Orphan Page"]])
        
        doc.add_paragraph(f"Reachable URLs: {reachable_urls}")
        doc.add_paragraph(f"Orphan pages: {orphan_pages}")
        
        # Add orphan pages
        if orphan_pages > 0:
            doc.add_heading("Orphan Pages", level=2)
            
            orphan_pages_df = reachability_df[reachability_df["Is Orphan Page"]]
            
            for _, row in orphan_pages_df.iterrows():
                doc.add_paragraph(row["URL"], style="List Bullet")
        
        # Add clicks from home
        doc.add_heading("Clicks from Home", level=2)
        
        # Sort by clicks from home
        reachability_df = reachability_df.sort_values("Clicks from Home")
        
        # Add a table
        table = doc.add_table(rows=1, cols=2)
        table.style = "Table Grid"
        
        # Add header row
        header_cells = table.rows[0].cells
        header_cells[0].text = "URL"
        header_cells[1].text = "Clicks from Home"
        
        # Add data rows
        for _, row in reachability_df.iterrows():
            # Skip orphan pages
            if row["Is Orphan Page"]:
                continue
            
            # Add a row
            row_cells = table.add_row().cells
            row_cells[0].text = row["URL"]
            row_cells[1].text = str(row["Clicks from Home"])
    
    def _add_topic_analysis(self, doc, topic_analyzer):
        """
        Add topic analysis to the document.
        
        Args:
            doc (Document): The document
            topic_analyzer (MainTopicAnalyzer): The main topic analyzer
        """
        doc.add_heading("Topic Analysis", level=1)
        
        # Get the data
        topic_df = topic_analyzer.to_dataframe()
        
        # Add a word cloud of topics
        doc.add_heading("Topic Word Cloud", level=2)
        
        # Create a word cloud
        topics = " ".join(topic_df["Main Topics"].tolist())
        
        if topics:
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(topics)
            
            # Save the word cloud to a BytesIO object
            img_bytes = io.BytesIO()
            wordcloud.to_image().save(img_bytes, format="PNG")
            img_bytes.seek(0)
            
            # Add the word cloud to the document
            doc.add_picture(img_bytes, width=Inches(6))
        else:
            doc.add_paragraph("No topics found.")
        
        # Add a word cloud of keywords
        doc.add_heading("Keyword Word Cloud", level=2)
        
        # Create a word cloud
        keywords = " ".join(topic_df["Keywords"].tolist())
        
        if keywords:
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(keywords)
            
            # Save the word cloud to a BytesIO object
            img_bytes = io.BytesIO()
            wordcloud.to_image().save(img_bytes, format="PNG")
            img_bytes.seek(0)
            
            # Add the word cloud to the document
            doc.add_picture(img_bytes, width=Inches(6))
        else:
            doc.add_paragraph("No keywords found.")
        
        # Add topics per URL
        doc.add_heading("Topics per URL", level=2)
        
        # Add a table
        table = doc.add_table(rows=1, cols=2)
        table.style = "Table Grid"
        
        # Add header row
        header_cells = table.rows[0].cells
        header_cells[0].text = "URL"
        header_cells[1].text = "Main Topics"
        
        # Add data rows
        for _, row in topic_df.iterrows():
            # Add a row
            row_cells = table.add_row().cells
            row_cells[0].text = row["URL"]
            row_cells[1].text = row["Main Topics"]
    
    def _add_clusters_analysis(self, doc, clusters, item_type):
        """
        Add clusters analysis to the document.
        
        Args:
            doc (Document): The document
            clusters (list): The clusters
            item_type (str): The type of items in the clusters (Query or Keyword)
        """
        doc.add_heading(f"{item_type} Clusters", level=2)
        
        # Add a table
        table = doc.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        
        # Add header row
        header_cells = table.rows[0].cells
        header_cells[0].text = "Cluster"
        header_cells[1].text = f"Top {item_type}s"
        header_cells[2].text = "Metrics"
        
        # Add data rows
        for i, cluster in enumerate(clusters):
            # Add a row
            row_cells = table.add_row().cells
            row_cells[0].text = f"Cluster {i+1}"
            row_cells[1].text = ", ".join(cluster["top_queries" if item_type == "Query" else "top_keywords"])
            
            if item_type == "Query":
                row_cells[2].text = f"Queries: {cluster['queries']}\nImpressions: {cluster['impressions']:.0f}\nClicks: {cluster['clicks']:.0f}\nAvg Position: {cluster['avg_position']:.1f}"
            else:
                row_cells[2].text = f"Keywords: {cluster['keywords']}\nTraffic: {cluster['traffic']:.0f}\nAvg Position: {cluster['avg_position']:.1f}\nSearch Volume: {cluster['search_volume']:.0f}"
    
    def _add_topics_analysis(self, doc, topics):
        """
        Add topics analysis to the document.
        
        Args:
            doc (Document): The document
            topics (dict): The topics
        """
        doc.add_heading("Topics per URL", level=2)
        
        # Add a table
        table = doc.add_table(rows=1, cols=2)
        table.style = "Table Grid"
        
        # Add header row
        header_cells = table.rows[0].cells
        header_cells[0].text = "URL"
        header_cells[1].text = "Topics"
        
        # Add data rows
        for url, topic in topics.items():
            # Add a row
            row_cells = table.add_row().cells
            row_cells[0].text = url
            row_cells[1].text = ", ".join(topic)
    
    def _add_visibility_traffic_analysis(self, doc, visibility, traffic):
        """
        Add visibility and traffic analysis to the document.
        
        Args:
            doc (Document): The document
            visibility (dict): The visibility per topic
            traffic (dict): The traffic per topic
        """
        doc.add_heading("Visibility and Traffic per Topic", level=2)
        
        # Add a table
        table = doc.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        
        # Add header row
        header_cells = table.rows[0].cells
        header_cells[0].text
