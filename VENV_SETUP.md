# Virtual Environment Setup for SEO Analysis Tool

This document explains how the virtual environment was set up for this project.

## Setup Steps

1. Created a virtual environment:
   ```
   python -m venv venv
   ```

2. Activated the virtual environment:
   ```
   venv\Scripts\activate
   ```

3. Installed dependencies from a modified requirements file:
   ```
   pip install -r requirements_modified.txt
   ```

4. Downloaded required NLTK data:
   ```
   python -m nltk.downloader punkt stopwords wordnet
   ```

5. Downloaded required spaCy language model:
   ```
   python -m spacy download en_core_web_sm
   ```

## Running the Application

You can run the application using the provided batch file:
```
run_seo_tool.bat
```

Or manually:
1. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```

2. Run the main script:
   ```
   python main.py
   ```

## Notes

- The `requirements_modified.txt` file was created based on the original `requirements.txt` file, with the following changes:
  - Commented out `tk>=8.6.0` as Tkinter is included with Python installations
  - Commented out `gzip>=0.1.0` as it's part of the Python standard library

- The virtual environment isolates the project dependencies from the system Python installation, ensuring compatibility and preventing conflicts with other projects.
