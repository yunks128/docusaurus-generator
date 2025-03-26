"""
Tests for the DocusaurusGenerator class.
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from docusaurus_generator import DocusaurusGenerator


class TestDocusaurusGenerator(unittest.TestCase):
    """Test cases for DocusaurusGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for output
        self.output_dir = tempfile.mkdtemp()
        
        # Use the current directory as a repo for testing
        self.repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Create a generator instance
        self.generator = DocusaurusGenerator(
            repo_path=self.repo_path,
            output_dir=self.output_dir
        )
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up the temporary directory
        if os.path.exists(self.output_dir):
            import shutil
            shutil.rmtree(self.output_dir)
    
    def test_initialization(self):
        """Test that the generator initializes correctly."""
        self.assertEqual(self.generator.repo_path, self.repo_path)
        self.assertEqual(self.generator.output_dir, self.output_dir)
        self.assertIsNotNone(self.generator.logger)
        self.assertIsNotNone(self.generator.config_generator)
        self.assertIsNotNone(self.generator.content_generator)
    
    @patch('docusaurus_generator.content_generator.ContentGenerator.generate_all_sections')
    @patch('docusaurus_generator.content_generator.ContentGenerator.generate_sidebar')
    @patch('docusaurus_generator.config_generator.DocusaurusConfigGenerator.generate_docusaurus_config')
    @patch('docusaurus_generator.content_generator.ContentGenerator.generate_homepage')
    @patch('docusaurus_generator.utils.copy_static_assets')
    def test_generate(self, mock_copy_assets, mock_gen_homepage, mock_gen_config, 
                     mock_gen_sidebar, mock_gen_sections):
        """Test the generate method calls all the necessary methods."""
        # Set up mocks
        mock_gen_sections.return_value = {'overview': 'content'}
        
        # Call generate
        result = self.generator.generate()
        
        # Assert all methods were called
        mock_gen_sections.assert_called_once()
        mock_gen_sidebar.assert_called_once_with({'overview': 'content'})
        mock_gen_config.assert_called_once()
        mock_gen_homepage.assert_called_once()
        mock_copy_assets.assert_called_once_with(self.repo_path, self.output_dir, self.generator.logger)
        
        # Assert result is True
        self.assertTrue(result)
    
    @patch('docusaurus_generator.generator.DocusaurusGenerator.generate')
    @patch('docusaurus_generator.utils.setup_docusaurus')
    @patch('docusaurus_generator.utils.start_docusaurus_server')
    def test_setup_and_start(self, mock_start, mock_setup, mock_generate):
        """Test the setup_and_start method calls all the necessary methods."""
        # Set up mocks
        mock_generate.return_value = True
        mock_setup.return_value = True
        mock_start.return_value = True
        
        # Call setup_and_start
        result = self.generator.setup_and_start(install=True, start=True)
        
        # Assert all methods were called
        mock_generate.assert_called_once()
        mock_setup.assert_called_once_with(self.output_dir, self.generator.logger)
        mock_start.assert_called_once_with(self.output_dir, self.generator.logger)
        
        # Assert result is True
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()