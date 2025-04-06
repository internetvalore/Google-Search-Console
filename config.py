#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration settings for the URL Validator application.
"""

# Window settings
WINDOW_TITLE = "URL Validator"
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 200

# UI settings
PADDING_X = 20
PADDING_Y = 20
TITLE_FONT = ("Arial", 16, "bold")
NORMAL_FONT = ("Arial", 12)
BUTTON_COLOR = "#4CAF50"
BUTTON_TEXT_COLOR = "white"
ERROR_COLOR = "red"
SUCCESS_COLOR = "green"
WRAP_LENGTH = 450

# URL validation settings
DEFAULT_URL_PREFIX = "https://"
REQUEST_TIMEOUT = 5
VALID_SCHEMES = ['http', 'https']

# Message box titles
ERROR_TITLE = "Validation Error"
SUCCESS_TITLE = "Validation Successful"
