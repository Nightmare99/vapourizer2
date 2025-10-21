"""
Web crawler module for the Vapourizer project.

This module provides a WebCrawler class that encapsulates web crawling functionality
using the crawl4ai library with deep crawling capabilities.
"""

import asyncio
from typing import List, Optional, Dict, Any
from crawl4ai import AsyncWebCrawler, ContentTypeFilter, CrawlerRunConfig, DomainFilter, FilterChain, URLPatternFilter
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from util.constants import URL_PATTERNS, ALLOWED_DOMAINS, ALLOWED_CONTENT_TYPES


class WebCrawler:
    """
    A web crawler class that provides asynchronous web crawling capabilities.
    
    This class uses crawl4ai's AsyncWebCrawler with configurable deep crawling
    strategies to extract content from web pages.
    """
    
    def __init__(
        self,
        max_depth: int = 1,
        include_external: bool = True,
        verbose: bool = True
    ):
        """
        Initialize the WebCrawler with configuration parameters.
        
        Args:
            max_depth: Maximum depth for deep crawling (default: 1)
            include_external: Whether to include external links (default: False)
            verbose: Enable verbose logging (default: True)
        """
        self.max_depth = max_depth
        self.include_external = include_external
        self.verbose = verbose
        self._config = self._create_crawler_config()
    
    def _create_crawler_config(self) -> CrawlerRunConfig:
        """
        Create and return a CrawlerRunConfig with the specified parameters.
        
        Returns:
            CrawlerRunConfig: Configured crawler run configuration
        """
        filter_chain = FilterChain([
            # Only follow URLs with specific patterns
            URLPatternFilter(patterns=URL_PATTERNS),

            # Only crawl specific domains
            DomainFilter(allowed_domains=ALLOWED_DOMAINS),

            # Only include specific content types
            ContentTypeFilter(allowed_types=ALLOWED_CONTENT_TYPES)
        ])
        return CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=self.max_depth,
                include_external=self.include_external,
                filter_chain=filter_chain,
            ),
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=self.verbose,
        )
    
    async def crawl(self, url: str) -> List[Any]:
        """
        Crawl a given URL and return the results.
        
        Args:
            url: The URL to crawl
            
        Returns:
            List[Any]: List of crawl results
            
        Raises:
            Exception: If crawling fails
        """
        try:
            async with AsyncWebCrawler() as crawler:
                results = await crawler.arun(url, config=self._config)
                return results
        except Exception as e:
            raise Exception(f"Failed to crawl {url}: {str(e)}")
    
    async def crawl_and_display(self, url: str) -> None:
        """
        Crawl a URL and display the results in a formatted manner.
        
        Args:
            url: The URL to crawl
        """
        try:
            results = await self.crawl(url)
            
            print(f"Crawled {len(results)} pages in total")
            print("-" * 50)
            
            for result in results:
                print(f"URL: {result.url}")
                print(f"Depth: {result.metadata.get('depth', 0)}")
                print(f"Content Preview:\n{result.markdown[:200]}...")
                print("-" * 50)
                
        except Exception as e:
            print(f"Error during crawling: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current crawler configuration.
        
        Returns:
            Dict[str, Any]: Configuration summary
        """
        return {
            "max_depth": self.max_depth,
            "include_external": self.include_external,
            "verbose": self.verbose,
            "strategy": "BFSDeepCrawlStrategy",
            "scraping_strategy": "LXMLWebScrapingStrategy"
        }

