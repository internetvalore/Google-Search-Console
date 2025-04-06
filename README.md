# SEO Analysis Tool

A comprehensive tool for analyzing websites for SEO purposes, including crawling, content analysis, and integration with external data sources like Google Search Console and SEMrush.

## Features

- **Website Crawling:** Crawl websites and process sitemaps to discover all pages.
- **Content Analysis:** Analyze meta descriptions, images, links, and page reachability.
- **Topic Analysis:** Identify main topics and keywords for each page.
- **Search Console Integration:** Load and analyze Google Search Console data.
- **SEMrush Integration:** Load and analyze SEMrush data.
- **LM Studio Integration:** Generate meta descriptions and ADS questions using LM Studio.
- **Report Generation:** Generate comprehensive reports in Word format.

## Modules

- **seo_config_settings.py:** Configuration settings for the tool.
- **seo_url_validator.py:** URL validation and normalization.
- **seo_crawler.py:** Website crawling and sitemap processing.
- **seo_content_loader.py:** Content loading and processing.
- **seo_meta_description.py:** Meta description analysis.
- **seo_images.py:** Image analysis.
- **seo_links.py:** Link analysis.
- **seo_reachability.py:** Page reachability analysis.
- **seo_main_topic.py:** Topic and keyword analysis.
- **seo_search_console.py:** Search Console data loading and analysis.
- **seo_semrush.py:** SEMrush data loading and analysis.
- **seo_lmstudio.py:** LM Studio integration.
- **seo_report.py:** Report generation.
- **seo_main.py:** Main entry point and GUI.

## Requirements

- Python 3.8+
- Required Python packages:
  - requests
  - beautifulsoup4
  - pandas
  - numpy
  - networkx
  - scikit-learn
  - spacy
  - wordcloud
  - python-docx
  - matplotlib
  - aiohttp
  - nltk

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/seo-analysis-tool.git
   cd seo-analysis-tool
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download the required NLTK and spaCy data:
   ```
   python -m nltk.downloader punkt stopwords wordnet
   python -m spacy download en_core_web_sm
   ```

## Usage

1. Run the main script:
   ```
   python seo_main.py
   ```

2. Enter a URL and validate it.

3. Crawl the website or process the sitemap.

4. Load the content.

5. Perform various analyses.

6. Generate reports.

## Configuration

You can configure the tool by modifying the `seo_config_settings.py` file. The following settings are available:

- **Meta description settings:** Minimum and maximum length for a good meta description.
- **Image settings:** Maximum size for an image.
- **Link settings:** Timeout for checking if a link is broken.
- **Crawler settings:** Maximum number of pages to crawl, maximum depth, timeout, and user agent.
- **Content loader settings:** Maximum number of concurrent requests and timeout.
- **Topic analyzer settings:** Maximum number of keywords and topics to extract per page.
- **Search Console settings:** Number of clusters for Search Console data.
- **SEMrush settings:** Number of clusters for SEMrush data.
- **LM Studio settings:** API URL, maximum number of tokens, temperature, and top-p value.
- **Report settings:** Output directory for reports.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Requests](https://requests.readthedocs.io/en/master/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Pandas](https://pandas.pydata.org/)
- [NumPy](https://numpy.org/)
- [NetworkX](https://networkx.org/)
- [scikit-learn](https://scikit-learn.org/stable/)
- [spaCy](https://spacy.io/)
- [WordCloud](https://github.com/amueller/word_cloud)
- [python-docx](https://python-docx.readthedocs.io/en/latest/)
- [Matplotlib](https://matplotlib.org/)
- [aiohttp](https://docs.aiohttp.org/en/stable/)
- [NLTK](https://www.nltk.org/)
