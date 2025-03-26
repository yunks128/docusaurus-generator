"""
Docusaurus configuration generation functionality.
"""
import os
import re
import git
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import shutil

class DocusaurusConfigGenerator:
    """
    Generator for Docusaurus configuration files.
    """
    
    def __init__(self, repo_path: str, output_dir: str, config: Dict, logger: logging.Logger):
        """
        Initialize the configuration generator.
        
        Args:
            repo_path: Path to the repository
            output_dir: Directory where documentation should be generated
            config: Configuration dictionary
            logger: Logger instance
        """
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.config = config
        self.logger = logger


    def _extract_project_info(self) -> dict:
        """Extract project information from repository and package files."""
        # Extract project name from repository
        project_name = os.path.basename(self.repo_path)
        repo_name = project_name
        description = f"{project_name} Documentation"
        repo_url = ""
        org_name = ""
        
        # Try to find more details in package.json if it exists
        project_info = self._extract_package_json_info(project_name, description, repo_url)
        project_name = project_info["project_name"]
        description = project_info["description"]
        repo_url = project_info["repo_url"]
        
        # Extract organization and repo name from git if available
        git_info = self._extract_git_info(org_name, repo_name, repo_url)
        org_name = git_info["org_name"]
        repo_name = git_info["repo_name"]
        repo_url = git_info["repo_url"]
        
        return {
            "project_name": project_name,
            "repo_name": repo_name,
            "description": description,
            "repo_url": repo_url,
            "org_name": org_name
        }

    def _extract_package_json_info(self, project_name, description, repo_url):
        """Extract information from package.json if it exists."""
        package_json = os.path.join(self.repo_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                    if 'name' in package_data:
                        project_name = package_data['name']
                    if 'description' in package_data:
                        description = package_data['description']
                    if 'repository' in package_data:
                        repo_url = self._extract_repo_url_from_package(package_data)
            except Exception as e:
                self.logger.warning(f"Error reading package.json: {str(e)}")
        
        return {
            "project_name": project_name,
            "description": description,
            "repo_url": repo_url
        }

    def _extract_repo_url_from_package(self, package_data):
        """Extract repository URL from package data."""
        if isinstance(package_data['repository'], str):
            return package_data['repository']
        elif isinstance(package_data['repository'], dict) and 'url' in package_data['repository']:
            return package_data['repository']['url']
        return ""

    def _extract_git_info(self, org_name, repo_name, repo_url):
        """Extract organization and repo information from git."""
        try:
            repo = git.Repo(self.repo_path)
            for remote in repo.remotes:
                for url in remote.urls:
                    # Extract org and repo from common git URL formats
                    match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', url)
                    if match:
                        org_name = match.group(1)
                        repo_name = match.group(2)
                        repo_url = f"https://github.com/{org_name}/{repo_name}"
                        break
        except Exception as e:
            self.logger.warning(f"Error extracting git information: {str(e)}")
        
        return {
            "org_name": org_name,
            "repo_name": repo_name,
            "repo_url": repo_url
        }

    def _create_supporting_files(self, project_info):
        """Create supporting files for the Docusaurus site."""
        self._create_custom_css_file()
        self._create_logo_files()

    def _create_logo_files(self):
        """Create logo and favicon files."""
        img_dir = os.path.join(self.output_dir, 'static', 'img')
        os.makedirs(img_dir, exist_ok=True)
        
        # Create a placeholder logo file
        with open(os.path.join(img_dir, 'logo.svg'), 'w') as f:
            f.write("""<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" fill="#4183c4"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="white" font-family="Arial" font-size="40">
        DOCS
    </text>
    </svg>""")
        
        # Create a placeholder favicon
        shutil.copy(
            os.path.join(img_dir, 'logo.svg'),
            os.path.join(img_dir, 'favicon.svg')
        )

    def _create_custom_css_file(self):
        """Create the custom CSS file."""
        os.makedirs(os.path.join(self.output_dir, 'src', 'css'), exist_ok=True)
        with open(os.path.join(self.output_dir, 'src', 'css', 'custom.css'), 'w') as f:
            f.write("""
    /* Your custom styles */
    :root {
    --ifm-color-primary: #4183c4;
    --ifm-color-primary-dark: #3a75b0;
    --ifm-color-primary-darker: #336699;
    --ifm-color-primary-darkest: #2d5986;
    --ifm-color-primary-light: #5191d3;
    --ifm-color-primary-lighter: #639fdb;
    --ifm-color-primary-lightest: #75ade2;
    --ifm-code-font-size: 95%;
    }
    """)
            

    def generate_docusaurus_config(self) -> None:
        """
        Generate the docusaurus.config.js file for the documentation site.
        """
        self.logger.debug("Starting docusaurus config generation")
        
        # Extract project information
        project_info = self._extract_project_info()
        
        # Generate the complete config file
        config_path = os.path.join(self.output_dir, 'docusaurus.config.js')
        
        repo_name = project_info["repo_name"]
        description = project_info["description"]
        org_name = project_info["org_name"]
        repo_url = project_info["repo_url"]
        
        # Create community section for footer if repo_url exists
        community_section = ""
        if repo_url:
            community_section = f"""
                {{
                title: 'Community',
                items: [
                    {{
                    label: 'GitHub',
                    href: '{repo_url}',
                    }},
                ],
                }},"""
        
        # Create the complete config file
        config_content = f"""/** @type {{import('@docusaurus/types').DocusaurusConfig}} */
    module.exports = {{
    title: "{repo_name}",
    tagline: "{description}",
    url: "{self.config.get('url', 'https://your-docusaurus-site.example.com')}",
    baseUrl: "{self.config.get('baseUrl', '/')}",
    onBrokenLinks: "warn",
    onBrokenMarkdownLinks: "warn",
    favicon: "img/favicon.svg",
    organizationName: "{org_name or self.config.get('organizationName', 'your-org')}",
    projectName: "{repo_name}",
    presets: [
        [
        "@docusaurus/preset-classic",
        {{
            docs: {{
            sidebarPath: require.resolve('./sidebars.js'),
            routeBasePath: "/",
            }},
            theme: {{
            customCss: require.resolve('./src/css/custom.css'),
            }},
        }},
        ],
    ],
    themeConfig: {{
        navbar: {{
        title: "{repo_name}",
        logo: {{
            alt: "{repo_name} Logo",
            src: "img/logo.svg",
        }},
        items: [
            {{
            to: "/",
            label: "Documentation",
            position: "left",
            activeBaseRegex: "^/$|^/(?!.+)",
            }},
            {{
            to: "/overview",
            label: "Overview",
            position: "left",
            }},
            {{
            to: "/api",
            label: "API",
            position: "left",
            }},
            {f'''{{
            href: "{repo_url}",
            label: "GitHub",
            position: "right",
            }},''' if repo_url else ''}
        ],
        }},
        footer: {{
        style: "dark",
        links: [
            {{
            title: "Docs",
            items: [
                {{
                label: "Overview",
                to: "/overview",
                }},
                {{
                label: "API",
                to: "/api",
                }},
            ],
            }},{community_section}
        ],
        copyright: "Copyright © {datetime.now().year} {org_name or 'Project Contributors'}. Built with Docusaurus.",
        }},
    }},
    }};
    """
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Create supporting files
        self._create_supporting_files(project_info)
        
        self.logger.info("Generated Docusaurus configuration")