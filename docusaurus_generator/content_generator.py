"""
Content generation functionality for Docusaurus documentation.
"""
import os
import re
import git
import yaml
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import shutil

from .ai_enhancer import enhance_with_ai


class ContentGenerator:
    """
    Generator for Docusaurus content files.
    """
    
    def __init__(self, repo_path: str, output_dir: str, use_ai: Optional[str], logger: logging.Logger):
        """
        Initialize the content generator.
        
        Args:
            repo_path: Path to the repository
            output_dir: Directory where documentation should be generated
            use_ai: Optional AI model to use for enhanced documentation
            logger: Logger instance
        """
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.use_ai = use_ai
        self.logger = logger


    def generate_all_sections(self) -> Dict[str, Optional[str]]:
        """
        Generate all documentation sections.
        
        Returns:
            A dictionary of section names mapped to their content.
        """
        # Create the docs directory
        docs_dir = os.path.join(self.output_dir, 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        sections = {
            'overview': self._generate_overview(),
            'installation': self._generate_installation(),
            'api': self._generate_api(),
            'guides': self._generate_guides(),
            'contributing': self._generate_contributing(),
            'changelog': self._generate_changelog(),
            'deployment': self._generate_deployment(),
            'architecture': self._generate_architecture(),
            'testing': self._generate_testing(),
            'security': self._generate_security()
        }

        for section_name, content in sections.items():
            if content:
                if self.use_ai:
                    content = enhance_with_ai(content, section_name, self.use_ai, self.logger)

                # Updated path to include docs directory
                file_path = os.path.join(docs_dir, f"{section_name}.md")
                with open(file_path, 'w') as f:
                    f.write(content)

                self.logger.info(f"Generated {section_name} documentation")
        
        # Create an index.md file to serve as the main entry point
        project_name = os.path.basename(self.repo_path)
        
        # Try to get a better description from README or package.json
        description = f"{project_name} documentation"
        readme_path = self._find_file("README.md")
        if readme_path:
            with open(readme_path, 'r') as f:
                readme_content = f.read()
                # Extract the first paragraph as a description
                match = re.search(r'#.*?\n\n(.*?)\n\n', readme_content, re.DOTALL)
                if match:
                    description = match.group(1).strip()
        
        index_content = self._format_page(
            title="Home",
            content=f"""# {project_name.title()} Documentation

    {description}

    ## Getting Started

    - [Overview](overview.md)
    {'- [Installation](installation.md)' if sections.get('installation') else ''}
    {'- [API Documentation](api.md)' if sections.get('api') else ''}

    ## Additional Resources

    {'- [Architecture](architecture.md)' if sections.get('architecture') else ''}
    {'- [Guides & Tutorials](guides.md)' if sections.get('guides') else ''}
    {'- [Contributing](contributing.md)' if sections.get('contributing') else ''}
    """,
            frontmatter={
                'id': 'index',
                'slug': '/',
            }
        )
        with open(os.path.join(docs_dir, 'index.md'), 'w') as f:
            f.write(index_content)
        
        self.logger.info("Generated index.md as main entry point")
                
        return sections


    def generate_homepage(self):
        """
        Generate enhanced src/pages/index.js and src/components/HomepageFeatures/index.js
        Creates a comprehensive homepage with hero banner, features section, and calls to action
        based on the template provided.
        """
        # Create necessary directories
        pages_dir = os.path.join(self.output_dir, 'src', 'pages')
        components_dir = os.path.join(self.output_dir, 'src', 'components')
        features_dir = os.path.join(components_dir, 'HomepageFeatures')
        css_dir = os.path.join(self.output_dir, 'src', 'css')
        
        os.makedirs(pages_dir, exist_ok=True)
        os.makedirs(features_dir, exist_ok=True)
        os.makedirs(css_dir, exist_ok=True)
        
        # Extract project information
        project_name = os.path.basename(self.repo_path)
        repo_url = f"https://github.com/{project_name}"
        description = f"{project_name} documentation and resources."
        
        # Create index.js for homepage with hero banner and sections
        index_js_content = f'''import clsx from 'clsx';
    import Link from '@docusaurus/Link';
    import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
    import Layout from '@theme/Layout';
    import HomepageFeatures from '@site/src/components/HomepageFeatures';
    import Heading from '@theme/Heading';
    import styles from './index.module.css';

    function HomepageHeader() {{
    const {{siteConfig}} = useDocusaurusContext();
    return (
        <header className={{clsx('hero', styles.heroBanner)}}>
        <div className="container">
            <Heading as="h1" className={{styles.heroTitle}}>
            {project_name}
            </Heading>
            <p className={{styles.heroSubtitle}}>{description}</p>
            <div className={{styles.buttons}}>
            <Link className="button button--primary button--lg" to="/docs">
                ✅ Get Started
            </Link>
            <Link className="button button--primary button--lg" to="/docs/download">
                ⬇️ Download Now
            </Link>
            <Link className="button button--primary button--lg" to="/about">
                📪 Contact
            </Link>
            </div>
            <div className={{styles.screenshotContainer}}>
            <img
                src="/img/800x400.png"
                alt="Product Screenshot"
                className={{styles.screenshot}}
            />
            </div>
        </div>
        </header>
    );
    }}

    function CustomerLogos() {{
    return (
        <section className={{styles.customerLogos}}>
        <div className="container">
            <h2 className="sectionTitle">(Optional) Used By</h2>
            <div className={{styles.logos}}>
            <img src="/img/200x200.png" alt="Customer 1" />
            <img src="/img/200x200.png" alt="Customer 2" />
            <img src="/img/200x200.png" alt="Customer 3" />
            </div>
        </div>
        </section>
    );
    }}

    function Testimonials() {{
    return (
        <section className={{styles.testimonials}}>
        <div className="container">
            <h2 className="sectionTitle">(Optional) What People Say</h2>
            <div className={{styles.quotes}}>
            <blockquote>
                <p>"This product is amazing!"</p>
                <cite>- Happy Customer</cite>
            </blockquote>
            <blockquote>
                <p>"It has transformed the way we work."</p>
                <cite>- Satisfied Client</cite>
            </blockquote>
            <blockquote>
                <p>"Incredible support and features."</p>
                <cite>- Loyal User</cite>
            </blockquote>
            </div>
        </div>
        </section>
    );
    }}

    function GetStarted() {{
    return (
        <section className={{styles.getStarted}}>
        <div className="container">
            <h2 className="sectionTitle">Get Started</h2>
            <div className={{styles.getStartedContent}}>
            <div>
                <h3>For Users</h3>
                <Link to="/docs/user" className={{styles.link}}>
                Read the Users Guide
                </Link>
            </div>
            <div>
                <h3>For Developers</h3>
                <Link to="/docs/developer" className={{styles.link}}>
                Read the Developers Guide
                </Link>
            </div>
            </div>
        </div>
        </section>
    );
    }}

    function LearnMore() {{
    return (
        <section className={{styles.learnMore}}>
        <div className="container">
            <h2 className="sectionTitle">Learn More</h2>
            <ul className={{styles.learnMoreList}}>
            <li>
                <Link to="{repo_url}" className={{styles.link}}>
                GitHub Repository
                </Link>
            </li>
            <li>
                <Link to="/docs/faqs" className={{styles.link}}>
                Frequently Asked Questions
                </Link>
            </li>
            <li>
                <Link to="/blog" className={{styles.link}}>
                News and Updates
                </Link>
            </li>
            </ul>
        </div>
        </section>
    );
    }}

    export default function Home() {{
    const {{siteConfig}} = useDocusaurusContext();
    return (
        <Layout title={{`Welcome to ${{siteConfig.title}}`}} description="{description}">
        <HomepageHeader />
        <main>
            <HomepageFeatures />
            <GetStarted />
            <LearnMore />
            <CustomerLogos />
            <Testimonials />
        </main>
        </Layout>
    );
    }}
    '''

        # Create index.module.css for styling the homepage
        index_module_css = '''.heroBanner {
    background-color: #00467a;
    color: #ffffff;
    padding: 6rem 0;
    text-align: left;
    position: relative;
    overflow: hidden;
    }

    .heroBanner h1 {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #ffffff;
    }

    .heroBanner p {
    font-size: 1.5rem;
    margin-bottom: 2rem;
    color: #ffffff;
    }

    [data-theme='dark'] .heroBanner {
    background-color: #0d3856;
    color: #e0e0e0;
    }

    [data-theme='dark'] .heroBanner h1,
    [data-theme='dark'] .heroBanner p {
    color: #e0e0e0;
    }

    .buttons {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 1rem;
    flex-wrap: wrap;
    }

    .screenshotContainer {
    margin-top: 2rem;
    text-align: left;
    }

    .screenshot {
    max-width: 100%;
    height: auto;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    }

    .customerLogos, .testimonials, .getStarted, .learnMore {
    padding: 4rem 0;
    }

    .logos {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 2rem;
    flex-wrap: wrap;
    }

    .quotes {
    display: flex;
    justify-content: flex-start;
    gap: 20px;
    flex-wrap: wrap;
    }

    .quotes blockquote {
    font-size: 1.25rem;
    font-style: italic;
    max-width: 800px;
    margin: 0;
    }

    .quotes cite {
    display: block;
    margin-top: 1rem;
    font-size: 1rem;
    }

    .getStartedContent {
    display: flex;
    justify-content: flex-start;
    flex-wrap: wrap;
    }

    .getStartedContent div {
    flex: 1;
    margin: 0px 0px;
    min-width: 200px;
    }

    .learnMoreList {
    list-style: none;
    padding: 0;
    text-align: left;
    }

    .learnMoreList li {
    margin: 10px 0;
    }

    .link {
    text-decoration: none;
    font-weight: 600;
    }

    .link:hover {
    text-decoration: underline;
    }
    '''

        # Create enhanced HomepageFeatures component
        homepage_features_content = f'''import React from 'react';
    import Heading from '@theme/Heading';
    import styles from './styles.module.css';

    const FeatureList = [
    {{
        title: 'Easy to Use',
        Svg: () => <img src="/img/200x200.png" alt="Easy to Use" />,
        description: (
        <>
            {project_name} was designed from the ground up to be easily installed and
            used to get your project up and running quickly.
        </>
        ),
    }},
    {{
        title: 'Focus on What Matters',
        Svg: () => <img src="/img/200x200.png" alt="Focus on What Matters" />,
        description: (
        <>
            {project_name} lets you focus on your content and documentation,
            while we handle all the technical details behind the scenes.
        </>
        ),
    }},
    {{
        title: 'Extensible',
        Svg: () => <img src="/img/200x200.png" alt="Extensible" />,
        description: (
        <>
            Extend or customize your project's documentation by adding and 
            configuring various plugins and components.
        </>
        ),
    }},
    ];

    function Feature({{Svg, title, description}}) {{
    return (
        <div className="col col--4">
        <div className={{styles.featureItem}}>
            <div className={{styles.featureImage}}>
            <Svg className={{styles.featureSvg}} role="img" />
            </div>
            <div className={{styles.featureContent}}>
            <Heading as="h3">{{title}}</Heading>
            <p>{{description}}</p>
            </div>
        </div>
        </div>
    );
    }}

    export default function HomepageFeatures() {{
    return (
        <section className={{styles.features}}>
        <div className="container">
            <h2 className="sectionTitle">Key Features</h2>
            <div className="row">
            {{FeatureList.map((props, idx) => (
                <Feature key={{idx}} {{...props}} />
            ))}}
            </div>
        </div>
        </section>
    );
    }}
    '''

        # Create styles for HomepageFeatures
        homepage_features_styles = '''.features {
    padding: 4rem 0;
    width: 100%;
    }

    .featureItem {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    height: 100%;
    }

    .featureImage {
    margin-bottom: 1rem;
    }

    .featureSvg {
    height: 200px;
    width: 200px;
    }

    .featureContent {
    text-align: center;
    }

    .featureContent h3 {
    margin-bottom: 0.5rem;
    font-size: 1.5rem;
    }

    @media screen and (max-width: 966px) {
    .featureItem {
        padding: 1rem;
    }
    }
    '''

        # Create custom.css with enhanced styles
        custom_css = '''/**
    * Any CSS included here will be global. The classic template
    * bundles Infima by default. Infima is a CSS framework designed to
    * work well for content-centric websites.
    */

    /* Override the default Infima variables */
    :root {
    --ifm-color-primary: #005b96;
    --ifm-color-primary-dark: #00467a;
    --ifm-color-primary-darker: #003865;
    --ifm-color-primary-darkest: #00294f;
    --ifm-color-primary-light: #0073b1;
    --ifm-color-primary-lighter: #0086cc;
    --ifm-color-primary-lightest: #0099e6;
    --ifm-code-font-size: 95%;
    --docusaurus-highlighted-code-line-bg: rgba(0, 0, 0, 0.05);
    --ifm-font-family-base: 'Open Sans', sans-serif;
    --ifm-heading-font-weight: 600;
    }

    /* Adjustments for dark mode */
    [data-theme='dark'] {
    --ifm-color-primary: #66b2ff;
    --ifm-color-primary-dark: #4d9de0;
    --ifm-color-primary-darker: #3388cc;
    --ifm-color-primary-darkest: #1a73b2;
    --ifm-color-primary-light: #80c6ff;
    --ifm-color-primary-lighter: #99d4ff;
    --ifm-color-primary-lightest: #b3e2ff;
    --docusaurus-highlighted-code-line-bg: rgba(0, 0, 0, 0.3);
    }

    /* Add styles for the navbar links */
    .navbar__link {
    text-decoration: none;
    color: inherit;
    font-weight: 600;
    }

    .navbar__link:hover {
    text-decoration: underline;
    color: inherit;
    }

    /* Ensure the sidebar links follow the same pattern */
    .menu__link {
    text-decoration: none;
    color: inherit;
    font-weight: 600;
    }

    .menu__link:hover {
    text-decoration: underline;
    color: inherit;
    }

    /* Title styles */
    .navbar__title, .navbar__brand {
    text-decoration: none;
    color: inherit;
    font-weight: 600;
    }

    .navbar__title:hover, .navbar__brand:hover {
    text-decoration: none;
    color: inherit;
    }

    /* Section styles */
    .section {
    padding: 60px 0;
    }

    .sectionTitle {
    font-size: 2rem;
    color: var(--ifm-color-primary-dark);
    text-align: left;
    margin-bottom: 2rem;
    font-weight: 600;
    }

    [data-theme='dark'] .sectionTitle {
    color: #ffffff;
    }

    /* Button styles */
    .button--primary {
    background-color: var(--ifm-color-primary);
    color: #ffffff;
    border: none;
    padding: 12px 24px;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 4px;
    transition: background-color 0.3s ease;
    }

    .button--primary:hover {
    background-color: var(--ifm-color-primary-dark);
    color: #ffffff;
    }

    .button--secondary {
    background-color: #025c8d;
    color: #ffffff !important;
    border: none;
    padding: 12px 24px;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 4px;
    transition: background-color 0.3s ease;
    }

    .button--secondary:hover {
    background-color: #003865;
    color: #ffffff;
    }

    /* Ensure proper contrast in dark mode */
    [data-theme='dark'] .button--primary, 
    [data-theme='dark'] .button--secondary,
    [data-theme='dark'] .button--primary:hover, 
    [data-theme='dark'] .button--secondary:hover {
    color: #ffffff;
    }

    /* Container styles */
    .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    }
    '''

        # Write files
        with open(os.path.join(pages_dir, 'index.js'), 'w') as f:
            f.write(index_js_content)
        
        with open(os.path.join(pages_dir, 'index.module.css'), 'w') as f:
            f.write(index_module_css)
        
        with open(os.path.join(features_dir, 'index.js'), 'w') as f:
            f.write(homepage_features_content)
        
        with open(os.path.join(features_dir, 'styles.module.css'), 'w') as f:
            f.write(homepage_features_styles)
        
        with open(os.path.join(css_dir, 'custom.css'), 'w') as f:
            f.write(custom_css)
        
        # Create static image placeholder directory
        img_dir = os.path.join(self.output_dir, 'static', 'img')
        os.makedirs(img_dir, exist_ok=True)
        
        # Create a placeholder logo file if it doesn't exist
        if not os.path.exists(os.path.join(img_dir, 'logo.svg')):
            with open(os.path.join(img_dir, 'logo.svg'), 'w') as f:
                f.write(f'''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="200" fill="#005b96"/>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="white" font-family="Arial" font-size="40">
            {project_name[0:1].upper()}
        </text>
    </svg>''')
        
        # Create placeholder image files if they don't exist
        for size in ['200x200', '800x400']:
            width, height = map(int, size.split('x'))
            if not os.path.exists(os.path.join(img_dir, f'{size}.png')):
                self._create_placeholder_image(os.path.join(img_dir, f'{size}.png'), width, height)
        
        # Create favicon if it doesn't exist
        if not os.path.exists(os.path.join(img_dir, 'favicon.ico')):
            shutil.copy(
                os.path.join(img_dir, 'logo.svg'),
                os.path.join(img_dir, 'favicon.ico')
            )
        
        if self.use_ai:
            # Enhance files with AI if enabled
            with open(os.path.join(pages_dir, 'index.js'), 'r') as f:
                enhanced_index = enhance_with_ai(f.read(), 'index.js', self.use_ai, self.logger)
                with open(os.path.join(pages_dir, 'index.js'), 'w') as f_out:
                    f_out.write(enhanced_index)
            
            with open(os.path.join(features_dir, 'index.js'), 'r') as f:
                enhanced_features = enhance_with_ai(f.read(), 'HomepageFeatures', self.use_ai, self.logger)
                with open(os.path.join(features_dir, 'index.js'), 'w') as f_out:
                    f_out.write(enhanced_features)
        
        self.logger.info(f"Generated enhanced homepage with title, subtitle, and documentation links")

    def _create_placeholder_image(self, filepath, width, height):
        """Create a simple placeholder image."""
        try:
            # Try to use PIL if available
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (width, height), color=(240, 240, 240))
            draw = ImageDraw.Draw(img)
            
            # Add text with dimensions
            text = f"{width}×{height}"
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            
            text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
            text_position = ((width - text_width) // 2, (height - text_height) // 2)
            draw.text(text_position, text, fill=(100, 100, 100), font=font)
            
            # Draw a border
            draw.rectangle([(0, 0), (width-1, height-1)], outline=(200, 200, 200))
            
            img.save(filepath)
        except ImportError:
            # If PIL is not available, create an empty file
            with open(filepath, 'wb') as f:
                f.write(b'')
            self.logger.warning(f"PIL not available, created empty placeholder at {filepath}")

    def generate_sidebar(self, sections: Dict[str, Optional[str]]) -> None:
        """Generate sidebar configuration."""
        sidebar_items = []
        
        # Add main index as the first entry
        sidebar_items.append({
            'type': 'doc',
            'id': 'index',
            'label': 'Home'
        })
        
        # First add overview if it exists
        if sections.get('overview') is not None:
            sidebar_items.append({
                'type': 'doc',
                'id': 'overview',
                'label': 'Overview'
            })
        
        # Then add other sections in a specific order
        important_sections = ['installation', 'architecture', 'api']
        for section in important_sections:
            if sections.get(section) is not None:
                sidebar_items.append({
                    'type': 'doc',
                    'id': section,
                    'label': section.title()
                })
        
        # Add remaining sections
        additional_sections = [s for s in sections.keys() if s not in ['overview'] + important_sections]
        for section in sorted(additional_sections):
            if sections.get(section) is not None:
                sidebar_items.append({
                    'type': 'doc',
                    'id': section,
                    'label': section.title()
                })
        
                
        # Write sidebar configuration as JavaScript
        with open(os.path.join(self.output_dir, 'sidebars.js'), 'w') as f:
            f.write("/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */\n")
            f.write("module.exports = {\n")
            f.write("  docs: [\n")
            
            for i, item in enumerate(sidebar_items):
                if item['type'] == 'doc':
                    f.write(f"    {{\n")
                    f.write(f"      type: 'doc',\n")
                    f.write(f"      id: '{item['id']}',\n")
                    f.write(f"      label: '{item['label']}',\n")
                    f.write(f"    }}")
                elif item['type'] == 'category':
                    f.write(f"    {{\n")
                    f.write(f"      type: 'category',\n")
                    f.write(f"      label: '{item['label']}',\n")
                    f.write(f"      collapsed: {str(item['collapsed']).lower()},\n")
                    f.write(f"      items: [{', '.join(repr(x) for x in item['items'])}],\n")
                    f.write(f"    }}")
                
                if i < len(sidebar_items) - 1:
                    f.write(",\n")
                else:
                    f.write("\n")
            
            f.write("  ],\n")
            f.write("};\n")


    def _generate_overview(self) -> Optional[str]:
        """Generate overview page from README."""
        readme_path = self._find_file("README.md")
        if not readme_path:
            return None
            
        with open(readme_path, 'r') as f:
            content = f.read()
            
        return self._format_page(
            title="Overview",
            content=content,
            frontmatter={
                'id': 'overview',
            }
        )

    def _generate_installation(self) -> Optional[str]:
        """Generate installation guide."""
        install_content = []
        
        # Check README installation section
        readme = self._find_file("README.md")
        if readme:
            with open(readme, 'r') as f:
                content = f.read()
                install_section = self._extract_section(content, "Installation", "Usage")
                if install_section:
                    install_content.append(install_section)

                
        # Check for package files
        package_files = {
            'Python': ['requirements.txt', 'setup.py'],
            'Node.js': ['package.json'],
            'Java': ['pom.xml'],
            'Ruby': ['Gemfile']
        }
        
        for lang, files in package_files.items():
            for file in files:
                if os.path.exists(os.path.join(self.repo_path, file)):
                    install_content.append(f"\n## {lang} Installation\n")
                    with open(os.path.join(self.repo_path, file), 'r') as f:
                        install_content.append(f"```\n{f.read()}\n```")
        
        if not install_content:
            return None
            
        return self._format_page(
            title="Installation",
            content="\n\n".join(install_content)
        )

    def _generate_api(self) -> Optional[str]:
        """Generate API documentation from source files."""
        api_content = []
        source_extensions = {'.py', '.js', '.java', '.cpp', '.h'}
        
        # Skip certain directories that shouldn't be documented
        skip_dirs = {'node_modules', '.git', '__pycache__', 'build', 'dist', 'venv', 'env'}
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip directories that shouldn't be documented
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in source_extensions):
                    relative_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                    api_content.append(f"\n## {relative_path}\n")
                    
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extract classes and functions
                        classes = re.findall(r'class\s+(\w+)', content)
                        functions = re.findall(r'def\s+(\w+)\s*\(', content)
                        
                        if classes:
                            api_content.append("\n### Classes\n")
                            api_content.extend(f"- `{cls}`" for cls in classes)
                        
                        if functions:
                            api_content.append("\n### Functions\n")
                            api_content.extend(f"- `{func}()`" for func in functions)
                    except UnicodeDecodeError:
                        self.logger.warning(f"Could not read file {relative_path} due to encoding issues")
        
        if not api_content:
            return None
            
        return self._format_page(
            title="API",
            content="\n".join(api_content)
        )


    def _generate_guides(self) -> Optional[str]:
        """Generate user guides from docs directory."""
        guides_content = []
        docs_dirs = ['docs', 'doc', 'guides', 'tutorials']
        
        # Process each directory
        for docs_dir in docs_dirs:
            dir_path = os.path.join(self.repo_path, docs_dir)
            if not os.path.exists(dir_path):
                continue
                
            # Process each markdown file in the directory
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if not file.endswith(('.md', '.rst')):
                        continue
                        
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    
                    try:
                        # Read the file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Process the content through our MDX sanitizer
                        content = self._sanitize_for_mdx(content)
                        
                        # Add file info header
                        file_header = f"## {rel_path}\n\n"
                        guides_content.append(file_header + content)
                    except Exception as e:
                        print(f"Error processing file {file_path}: {str(e)}")
                        guides_content.append(f"## {rel_path}\n\n*File could not be processed due to an error.*")
        
        if not guides_content:
            return None
            
        return self._format_page(
            title="Guides",
            content="\n\n---\n\n".join(guides_content)
        )

    def _sanitize_for_mdx(self, content: str) -> str:
        """
        Sanitize content to be MDX-compatible.
        This handles common issues that cause MDX compilation errors.
        """
        import re
        
        # Step 1: Save code blocks to protect them from modifications
        code_blocks = []
        
        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f"CODE_BLOCK_{len(code_blocks)-1}"
        
        # Save fenced code blocks
        content = re.sub(r'```[\s\S]*?```', save_code_block, content)
        
        # Save inline code blocks
        content = re.sub(r'`[^`]*`', save_code_block, content)
        
        # Step 2: Fix common MDX issues
        
        # Fix 1: Replace < followed by numbers (like <3) with &lt;
        content = re.sub(r'<(\d)', r'&lt;\1', content)
        
        # Fix 2: Replace unclosed HTML/JSX tags
        # This regex looks for opening tags that aren't properly closed
        content = re.sub(r'<([a-zA-Z][a-zA-Z0-9_:-]*)(?![^<>]*>)', r'&lt;\1', content)
        
        # Fix 3: Replace HTML comments with MDX-safe comments
        content = re.sub(r'<!--([\s\S]*?)-->', r'{/* \1 */}', content)
        
        # Fix 4: Ensure proper spacing in self-closing tags
        content = re.sub(r'<([a-zA-Z][a-zA-Z0-9_:-]*[^>]*?)\/>', r'<\1 />', content)
        
        # Fix 5: Escape curly braces that might be interpreted as JSX expressions
        content = re.sub(r'(?<![`\\{]){(?!\s*[/#])', r'&#123;', content)
        content = re.sub(r'(?<![`\\}])}', r'&#125;', content)
        
        # Step 3: Restore code blocks
        for i, block in enumerate(code_blocks):
            content = content.replace(f"CODE_BLOCK_{i}", block)
        
        return content


    def _generate_contributing(self) -> Optional[str]:
        """Generate contributing guidelines."""
        contributing_file = self._find_file("CONTRIBUTING.md")
        if not contributing_file:
            return None
            
        with open(contributing_file, 'r') as f:
            content = f.read()
            
        return self._format_page(
            title="Contributing",
            content=content
        )

    def _generate_changelog(self) -> Optional[str]:
        """Generate changelog from CHANGELOG.md and git history."""
        changelog_content = []
        
        # Check for CHANGELOG file
        changelog_file = self._find_file("CHANGELOG.md")
        if changelog_file:
            with open(changelog_file, 'r') as f:
                changelog_content.append(f.read())
        
        # Add recent git history
        try:
            repo = git.Repo(self.repo_path)
            # Try to get the default branch name instead of assuming 'main'
            default_branch = None
            try:
                # Try getting the HEAD branch first
                default_branch = repo.active_branch.name
            except TypeError:
                # If HEAD is detached, try getting the default branch from remote
                try:
                    default_branch = repo.git.symbolic_ref('refs/remotes/origin/HEAD').replace('refs/remotes/origin/', '')
                except git.GitCommandError:
                    # If that fails too, try common branch names
                    for branch in ['main', 'master']:
                        try:
                            repo.git.rev_parse('--verify', branch)
                            default_branch = branch
                            break
                        except git.GitCommandError:
                            continue
            
            if default_branch:
                commits = list(repo.iter_commits(default_branch))[:20]
                if commits:
                    changelog_content.append("\n## Recent Changes\n")
                    for commit in commits:
                        date = datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d')
                        changelog_content.append(f"- {date}: {commit.summary}")
            else:
                self.logger.warning("Could not determine default branch. Skipping git history.")
                
        except Exception as e:
            self.logger.warning(f"Error getting git history: {str(e)}")
        
        if not changelog_content:
            return None
            
        return self._format_page(
            title="Changelog",
            content="\n\n".join(changelog_content)
        )
        
    def _generate_deployment(self) -> Optional[str]:
        """Generate deployment documentation."""
        deployment_content = []
        
        # Check for deployment-related files
        deployment_files = {
            'Docker': ['Dockerfile', 'docker-compose.yml'],
            'Kubernetes': ['.kubernetes/', 'k8s/'],
            'CI/CD': ['.github/workflows/', '.gitlab-ci.yml', 'Jenkinsfile'],
            'Scripts': ['deploy.sh', 'deploy.py']
        }
        
        for category, files in deployment_files.items():
            found_files = []
            for file in files:
                file_path = os.path.join(self.repo_path, file)
                if os.path.exists(file_path):
                    found_files.append(file)
                    if os.path.isfile(file_path):
                        with open(file_path, 'r') as f:
                            deployment_content.append(f"\n### {file}\n```\n{f.read()}\n```")
            
            if found_files:
                deployment_content.insert(0, f"\n## {category}\n")
                deployment_content.insert(1, f"Found configuration in: {', '.join(found_files)}")
        
        if not deployment_content:
            return None
            
        return self._format_page(
            title="Deployment",
            content="\n".join(deployment_content)
        )

    def _generate_architecture(self) -> Optional[str]:
        """Generate architecture documentation."""
        architecture_content = []
        
        # Check for architecture documentation files
        arch_files = ['ARCHITECTURE.md', 'docs/architecture.md', 'docs/design.md']
        
        for file in arch_files:
            file_path = os.path.join(self.repo_path, file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    architecture_content.append(f.read())
                break
        
        # Add project structure
        architecture_content.append("\n## Project Structure\n")
        architecture_content.append("```")
        
        exclude_dirs = {'.git', '__pycache__', 'node_modules', 'build', 'dist'}
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            level = root.replace(self.repo_path, '').count(os.sep)
            indent = ' ' * 4 * level
            architecture_content.append(f"{indent}{os.path.basename(root)}/")
            
            subindent = ' ' * 4 * (level + 1)
            for f in sorted(files):
                architecture_content.append(f"{subindent}{f}")
        
        architecture_content.append("```")
        
        return self._format_page(
            title="Architecture",
            content="\n".join(architecture_content)
        )

    def _generate_testing(self) -> Optional[str]:
        """Generate testing documentation."""
        testing_content = []
        
        # Check for testing documentation
        test_docs = ['TESTING.md', 'docs/testing.md']
        for doc in test_docs:
            doc_path = os.path.join(self.repo_path, doc)
            if os.path.exists(doc_path):
                with open(doc_path, 'r') as f:
                    testing_content.append(f.read())
                break
        
        # Find test directories and files
        test_markers = ['test', 'tests', 'spec', 'specs']
        test_files = []
        
        for root, _, files in os.walk(self.repo_path):
            if any(marker in root.lower() for marker in test_markers):
                rel_path = os.path.relpath(root, self.repo_path)
                test_files.extend([
                    (rel_path, f) for f in files 
                    if f.endswith(('.py', '.js', '.ts', '.java', '.cpp'))
                ])
        
        if test_files:
            testing_content.append("\n## Test Structure\n")
            current_dir = None
            
            for dir_path, file in sorted(test_files):
                if dir_path != current_dir:
                    current_dir = dir_path
                    testing_content.append(f"\n### {dir_path}/\n")
                testing_content.append(f"- {file}")
        
        if not testing_content:
            return None
            
        return self._format_page(
            title="Testing",
            content="\n".join(testing_content)
        )
        
    def _generate_security(self) -> Optional[str]:
        """Generate security documentation."""
        security_content = []
        
        # Check for security documentation
        security_files = ['SECURITY.md', '.github/SECURITY.md', 'docs/security.md']
        for file in security_files:
            file_path = os.path.join(self.repo_path, file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    security_content.append(f.read())
                break
        
        # Check for security-related configurations
        security_configs = {
            'Authentication': ['.env.example', 'config/auth.*'],
            'Dependencies': ['package-lock.json', 'requirements.txt', 'Gemfile.lock'],
            'CI Security': [
                '.github/workflows/codeql-analysis.yml',
                '.github/workflows/security.yml',
                '.snyk'
            ]
        }
        
        for category, patterns in security_configs.items():
            found_files = []
            for pattern in patterns:
                for file in Path(self.repo_path).glob(pattern):
                    found_files.append(file.name)
            
            if found_files:
                security_content.append(f"\n## {category}\n")
                security_content.append(f"Security configurations found in: {', '.join(found_files)}")
        
        if not security_content:
            return None
            
        return self._format_page(
            title="Security",
            content="\n".join(security_content)
        )
        
    def _find_file(self, filename: str) -> Optional[str]:
        """Find a file in the repository."""
        for root, _, files in os.walk(self.repo_path):
            if filename in files:
                return os.path.join(root, filename)
        return None

    def _extract_section(self, content: str, start: str, end: str) -> Optional[str]:
        """Extract content between two headers."""
        pattern = f"#+ *{start}.*?(?=#+ *{end}|$)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(0).strip() if match else None

    def _format_page(self, title: str, content: str, frontmatter: Dict = None) -> str:
        """Format a documentation page with frontmatter."""
        # Normalize the ID to match Docusaurus conventions (lowercase with spaces converted to hyphens)
        normalized_id = title.lower().replace(' ', '-')
        
        fm = {
            'id': normalized_id,
            'title': title,
            'sidebar_label': title,
            **(frontmatter or {})
        }
        
        frontmatter_yaml = yaml.dump(fm, default_flow_style=False)
        return f"---\n{frontmatter_yaml}---\n\n{content}"