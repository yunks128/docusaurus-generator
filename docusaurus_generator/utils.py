"""
Utility functions for DocusaurusGenerator.
"""
import os
import sys
import shutil
import logging
import subprocess
from typing import Optional


def copy_static_assets(repo_path: str, output_dir: str, logger: logging.Logger) -> None:
    """
    Copy static assets from the repository to the output directory.
    
    Args:
        repo_path: Path to the repository
        output_dir: Directory where documentation should be generated
        logger: Logger instance
    """
    static_dir = os.path.join(output_dir, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                try:
                    source_path = os.path.join(root, file)
                    target_path = os.path.join(static_dir, file)
                    
                    # Only copy if source and target are different
                    if os.path.abspath(source_path) != os.path.abspath(target_path):
                        shutil.copy2(source_path, target_path)
                        
                except Exception as e:
                    logger.warning(f"Error copying asset {file}: {str(e)}")


def run_command(cmd: list, cwd: str, logger: logging.Logger) -> bool:
    """
    Run a command in a specific directory.
    
    Args:
        cmd: Command to run as a list of strings
        cwd: Directory to run the command in
        logger: Logger instance
        
    Returns:
        True if command succeeded, False otherwise
    """
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Stream output in real-time
        for line in process.stdout:
            logger.info(line.strip())
        
        # Wait for process to complete
        return_code = process.wait()
        
        # Log any errors
        if return_code != 0:
            for line in process.stderr:
                logger.error(line.strip())
            
            logger.error(f"Command failed with return code {return_code}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False


def setup_docusaurus(output_dir: str, logger: logging.Logger) -> bool:
    """
    Set up Docusaurus by installing dependencies.
    
    Args:
        output_dir: Directory where documentation should be generated
        logger: Logger instance
        
    Returns:
        True if setup succeeded, False otherwise
    """
    # Check if package.json exists, if not create it
    if not os.path.exists(os.path.join(output_dir, 'package.json')):
        logger.info("Initializing npm project...")
        if not run_command(['npm', 'init', '-y'], output_dir, logger):
            return False
    
    # Install Docusaurus dependencies
    logger.info("Installing Docusaurus dependencies...")
    dependencies = [
        '@docusaurus/core',
        '@docusaurus/preset-classic',
        'react',
        'react-dom'
    ]
    
    if not run_command(['npm', 'install', '--save'] + dependencies, output_dir, logger):
        return False
    
    # Update package.json with scripts
    update_package_json(output_dir, logger)
    
    return True


def update_package_json(output_dir: str, logger: logging.Logger) -> None:
    """
    Update package.json with Docusaurus scripts.
    
    Args:
        output_dir: Directory where documentation should be generated
        logger: Logger instance
    """
    import json
    
    package_json_path = os.path.join(output_dir, 'package.json')
    try:
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        # Add scripts
        package_data['scripts'] = {
            'start': 'docusaurus start',
            'build': 'docusaurus build',
            'swizzle': 'docusaurus swizzle',
            'deploy': 'docusaurus deploy',
            'clear': 'docusaurus clear',
            'serve': 'docusaurus serve',
            'write-translations': 'docusaurus write-translations',
            'write-heading-ids': 'docusaurus write-heading-ids'
        }
        
        # Write updated package.json
        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)
            
    except Exception as e:
        logger.warning(f"Error updating package.json: {str(e)}")


def start_docusaurus_server(output_dir: str, logger: logging.Logger) -> bool:
    """
    Start the Docusaurus development server.
    
    Args:
        output_dir: Directory where documentation should be generated
        logger: Logger instance
        
    Returns:
        True if server started successfully, False otherwise
    """
    logger.info("Starting Docusaurus development server...")
    return run_command(['npm', 'start'], output_dir, logger)