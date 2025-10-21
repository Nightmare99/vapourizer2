"""
File writing utilities for the Vapourizer project.

This module provides file writing capabilities, specifically for markdown files
in the output directory structure.
"""

import os
from pathlib import Path
from typing import Union, Optional
from datetime import datetime


class FileWriter:
    """
    A utility class for writing files, specifically markdown files to an output directory.
    
    This class handles creating output directories, generating filenames, and writing
    content to markdown files with proper error handling.
    """
    
    def __init__(self, output_dir: str = "out"):
        """
        Initialize the FileWriter with an output directory.
        
        Args:
            output_dir: Directory where files will be written (default: "out")
        """
        self.output_dir = Path(output_dir)
        self._ensure_output_directory()
    
    def _ensure_output_directory(self) -> None:
        """
        Ensure the output directory exists, creating it if necessary.
        """
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise Exception(f"Failed to create output directory {self.output_dir}: {str(e)}")
    
    def _generate_filename(self, base_name: str, extension: str = ".md", timestamp: bool = True) -> str:
        """
        Generate a filename based on the base name and optional timestamp.
        
        Args:
            base_name: Base name for the file
            extension: File extension (default: ".md")
            timestamp: Whether to include timestamp in filename (default: True)
            
        Returns:
            str: Generated filename
        """
        # Sanitize base name for filesystem
        sanitized_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        sanitized_name = sanitized_name.replace(' ', '_').lower()
        
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{sanitized_name}_{timestamp_str}{extension}"
        else:
            return f"{sanitized_name}{extension}"
    
    def write_markdown(
        self, 
        content: str, 
        filename: Optional[str] = None, 
        title: Optional[str] = None,
        timestamp: bool = True
    ) -> Path:
        """
        Write markdown content to a file in the output directory.
        
        Args:
            content: Markdown content to write
            filename: Optional custom filename (without extension)
            title: Optional title for the markdown file
            timestamp: Whether to include timestamp in filename (default: True)
            
        Returns:
            Path: Path to the written file
            
        Raises:
            Exception: If writing fails
        """
        try:
            # Generate filename if not provided
            if filename is None:
                base_name = title if title else "crawl_output"
            else:
                base_name = filename
            
            file_name = self._generate_filename(base_name, timestamp=timestamp)
            file_path = self.output_dir / file_name
            
            # Prepare markdown content with header if title provided
            markdown_content = ""
            if title:
                markdown_content += f"# {title}\n\n"
                markdown_content += f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                markdown_content += "---\n\n"
            
            markdown_content += content
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Failed to write markdown file: {str(e)}")
    
    def write_crawl_results(
        self, 
        results: list, 
        base_filename: str = "crawl_results",
        timestamp: bool = True
    ) -> Path:
        """
        Write crawl results to a markdown file with structured formatting.
        
        Args:
            results: List of crawl results from the web crawler
            base_filename: Base name for the output file
            timestamp: Whether to include timestamp in filename
            
        Returns:
            Path: Path to the written file
        """
        try:
            # Prepare markdown content
            title = f"Web Crawl Results - {len(results)} pages"
            content_parts = []
            
            content_parts.append(f"**Total Pages Crawled:** {len(results)}\n")
            content_parts.append("## Crawl Results\n")
            
            for i, result in enumerate(results, 1):
                content_parts.append(f"### Page {i}: {result.url}")
                content_parts.append(f"**Depth:** {result.metadata.get('depth', 0)}")
                content_parts.append(f"**Status:** {getattr(result, 'status_code', 'N/A')}")
                content_parts.append("**Content:**")
                content_parts.append("```markdown")
                content_parts.append(result.markdown if hasattr(result, 'markdown') else str(result))
                content_parts.append("```")
                content_parts.append("---\n")
            
            markdown_content = "\n".join(content_parts)
            
            return self.write_markdown(
                content=markdown_content,
                filename=base_filename,
                title=title,
                timestamp=timestamp
            )
            
        except Exception as e:
            raise Exception(f"Failed to write crawl results: {str(e)}")
    
    def initialize_streaming_markdown(
        self,
        base_filename: str = "streaming_results",
        title: Optional[str] = None,
        timestamp: bool = True
    ) -> Path:
        """
        Initialize a markdown file for streaming content.
        
        Args:
            base_filename: Base name for the output file
            title: Optional title for the markdown file
            timestamp: Whether to include timestamp in filename
            
        Returns:
            Path: Path to the initialized file
        """
        try:
            file_name = self._generate_filename(base_filename, timestamp=timestamp)
            file_path = self.output_dir / file_name
            
            # Initialize with header
            header_content = ""
            if title:
                header_content += f"# {title}\n\n"
                header_content += f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                header_content += "---\n\n"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(header_content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Failed to initialize streaming markdown file: {str(e)}")
    
    def append_to_markdown(self, file_path: Path, content: str, section_title: Optional[str] = None) -> None:
        """
        Append content to an existing markdown file.
        
        Args:
            file_path: Path to the markdown file to append to
            content: Content to append
            section_title: Optional section title to add before content
            
        Raises:
            Exception: If appending fails
        """
        try:
            append_content = ""
            if section_title:
                append_content += f"## {section_title}\n\n"
            
            append_content += content + "\n\n"
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(append_content)
                f.flush()  # Ensure content is written immediately
                
        except Exception as e:
            raise Exception(f"Failed to append to markdown file: {str(e)}")
    
    def get_output_directory(self) -> Path:
        """
        Get the current output directory path.
        
        Returns:
            Path: Output directory path
        """
        return self.output_dir
