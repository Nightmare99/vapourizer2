"""
Configuration constants for the Vapourizer web crawler.

This module contains all the configuration constants used by the web crawler,
including URL patterns, allowed domains, and content types for filtering.
"""

# URL patterns to match when crawling
URL_PATTERNS = [
    "*react*",
    "*langgraph*", 
    "*pydantic*",
    "*fastmcp*",
]

# Allowed domains for crawling
ALLOWED_DOMAINS = [
    "ai.pydantic.dev",
    "langchain-ai.github.io", 
    "digitaltoolkit.livingdesign.walmart.com",
    "gofastmcp.com",
]

# Allowed content types for crawling
ALLOWED_CONTENT_TYPES = [
    "text/html"
]
