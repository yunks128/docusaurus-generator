"""
Main DocusaurusGenerator class for generating Docusaurus documentation from repository content.
"""
import os
import logging
import shutil
from typing import Dict, List, Optional

from .config_generator import DocusaurusConfigGenerator
from .content_generator import ContentGenerator
from .utils import setup_docusaurus, copy_static_assets, start_docusaurus_server


class DocusaurusGenerator:
    """
    Generates Docusaurus documentation from repository content.
    """
    
    def __new__(cls, *args, **kwargs):
        """
        Ensure the class can be instantiated with arguments.
        """
        return super(DocusaurusGenerator, cls).__new__(cls)
    
    def __init__(self, repo_path: str, output_dir: str, config: Optional[Dict] = None, use_ai: Optional[str] = None):
        """
        Initialize the documentation generator.
        
        Args:
            repo_path: Path to the repository
            output_dir: Directory where documentation should be generated
            config: Optional configuration dictionary
            use_ai: Optional AI model to use for enhanced documentation (e.g., "openai/gpt-4o")
        """
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.config = config or {}
        self.use_ai = use_ai
        
        # Initialize directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'static'), exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        if self.use_ai:
            self.logger.info(f"AI enhancement enabled using model: {self.use_ai}")
            
        # Initialize component generators
        self.config_generator = DocusaurusConfigGenerator(self.repo_path, self.output_dir, self.config, self.logger)
        self.content_generator = ContentGenerator(self.repo_path, self.output_dir, self.use_ai, self.logger)

    def generate(self) -> bool:
        """
        Generate the complete Docusaurus documentation site.
        
        Returns:
            bool: True if generation was successful, False otherwise
        """
        try:
            # Generate all content sections
            sections = self.content_generator.generate_all_sections()
            
            # Generate sidebar configuration
            self.content_generator.generate_sidebar(sections)
            
            # Generate Docusaurus configuration
            self.config_generator.generate_docusaurus_config()
            
            # Generate homepage
            self.content_generator.generate_homepage()
            
            # Copy static assets
            copy_static_assets(self.repo_path, self.output_dir, self.logger)
            
            return True

        except Exception as e:
            self.logger.error(f"Documentation generation failed: {str(e)}")
            return False
    
    def setup_and_start(self, install: bool = True, start: bool = True) -> bool:
        """
        Set up Docusaurus and optionally start the development server.
        
        Args:
            install: Whether to run npm install
            start: Whether to start the development server
            
        Returns:
            bool: True if setup and start were successful, False otherwise
        """
        try:
            # Generate documentation first
            success = self.generate()
            if not success:
                return False
                
            # Set up Docusaurus (npm install)
            if install:
                setup_docusaurus(self.output_dir, self.logger)
            
            # Start Docusaurus server
            if start:
                start_docusaurus_server(self.output_dir, self.logger)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Docusaurus setup and start failed: {str(e)}")
            return False