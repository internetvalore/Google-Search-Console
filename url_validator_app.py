#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
URL Validator Application GUI.
Contains the main application class for the URL validator.
"""

import tkinter as tk
from tkinter import messagebox
from url_validator import URLValidator
from config import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT,
    PADDING_X, PADDING_Y, TITLE_FONT, NORMAL_FONT,
    BUTTON_COLOR, BUTTON_TEXT_COLOR, ERROR_COLOR, SUCCESS_COLOR,
    WRAP_LENGTH, DEFAULT_URL_PREFIX, ERROR_TITLE, SUCCESS_TITLE
)


class URLValidatorApp:
    """Main application class for the URL validator."""
    
    def __init__(self, root):
        """
        Initialize the URL validator application.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(True, True)
    
    def create_widgets(self):
        """Create and configure the UI widgets."""
        self.create_main_frame()
        self.create_title_label()
        self.create_input_frame()
        self.create_submit_button()
        self.create_status_label()
    
    def create_main_frame(self):
        """Create the main frame."""
        self.main_frame = tk.Frame(self.root, padx=PADDING_X, pady=PADDING_Y)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def create_title_label(self):
        """Create the title label."""
        self.title_label = tk.Label(
            self.main_frame,
            text=WINDOW_TITLE,
            font=TITLE_FONT
        )
        self.title_label.pack(pady=(0, 20))
    
    def create_input_frame(self):
        """Create the input frame with URL label and entry."""
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=10)
        
        # URL label
        self.url_label = tk.Label(
            self.input_frame,
            text="Enter Root URL:",
            font=NORMAL_FONT
        )
        self.url_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # URL entry
        self.url_entry = tk.Entry(self.input_frame, font=NORMAL_FONT, width=30)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_entry.insert(0, DEFAULT_URL_PREFIX)
    
    def create_submit_button(self):
        """Create the submit button."""
        self.submit_button = tk.Button(
            self.main_frame,
            text="Validate URL",
            font=NORMAL_FONT,
            command=self.validate_url,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            padx=10,
            pady=5
        )
        self.submit_button.pack(pady=20)
    
    def create_status_label(self):
        """Create the status label."""
        self.status_label = tk.Label(
            self.main_frame,
            text="",
            font=NORMAL_FONT,
            wraplength=WRAP_LENGTH
        )
        self.status_label.pack(pady=10)
    
    def validate_url(self):
        """Validate the URL and show the result."""
        url = self.url_entry.get().strip()
        
        # Reset status
        self.status_label.config(text="")
        
        # Validate URL
        is_valid, message, _ = URLValidator.validate(url)
        
        # Show result
        if is_valid:
            self.show_success(message)
            messagebox.showinfo(SUCCESS_TITLE, message)
        else:
            self.show_error(message)
            messagebox.showerror(ERROR_TITLE, message)
    
    def show_error(self, message):
        """Display error message in the status label."""
        self.status_label.config(text=message, fg=ERROR_COLOR)
    
    def show_success(self, message):
        """Display success message in the status label."""
        self.status_label.config(text=message, fg=SUCCESS_COLOR)
