#!/usr/bin/env python3
"""
Vapourizer - Web Crawler Application

Entry point for the Vapourizer web crawler application.
This application uses the crawlers package to perform deep web crawling.
"""

import asyncio
from urllib.parse import urlparse
from crawlers import WebCrawler
from util import FileWriter
from llm.agent import agent

async def main():
    """
    Main application entry point.
    
    Demonstrates the usage of the WebCrawler class to crawl
    the Walmart Digital Toolkit documentation.
    """
    # Initialize the web crawler with configuration
    crawler = WebCrawler(
        max_depth=2,
        include_external=True,
        verbose=True
    )
    
    # Display crawler configuration
    print("Web Crawler Configuration:")
    config_summary = crawler.get_config_summary()
    for key, value in config_summary.items():
        print(f"  {key}: {value}")
    print()
    
    # Target URL to crawl
    target_url = "https://digitaltoolkit.livingdesign.walmart.com/develop/react/"
    # target_url = "https://ai.pydantic.dev/"
    # target_url = "https://langchain-ai.github.io/langgraph/concepts/why-langgraph/"
    # target_url = "https://gofastmcp.com/getting-started/welcome"
    print(f"Target URL: {target_url}")
    print("=" * 60)
    
    # Perform the crawl
    try:
        print(f"Starting crawl of: {target_url}")
        crawl_results = await crawler.crawl(target_url)
        
        print(f"Successfully crawled {len(crawl_results)} pages")
        
        # Initialize file writer and streaming markdown file
        file_writer = FileWriter(output_dir="out")
        output_path = file_writer.initialize_streaming_markdown(
            base_filename="walmart_design_toolkit",
            # base_filename="pydantic_ai",
            # base_filename="langgraph",
            # base_filename="fastmcp",
            title=f"Web Crawl Results - {len(crawl_results)} pages"
        )
        
        print(f"📄 Streaming results to: {output_path}")
        
        # Process each crawl result and immediately append to markdown
        for i, result in enumerate(crawl_results, 1):
            print(f"\n🤖 >> Extracting information from {result.url}")
            try:
                output = await agent.run(f"""
                    Consider the markdown attached. You must extract
                    useful information from it and return as formatted
                    markdown.

                    {result.markdown}
                """)
                print(f"\n🤖 >> Extracted information from {result.url}")
            except Exception as e:
                # Exception may occur if crawled data is HUGE
                print(f"❌ Error extracting information from {result.url}: {e}")
                continue
            
            # Immediately append the agent output to the markdown file
            section_title = f"Page {i}: {result.url}"
            file_writer.append_to_markdown(
                file_path=output_path,
                content=output.output,
                section_title=section_title
            )
            print(f"✅ >> Appended results for {result.url} to markdown file")
        
        print(f"\n✅ Crawl completed successfully!")
        print(f"📄 All results saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error during crawl: {e}")


if __name__ == "__main__":
    asyncio.run(main())