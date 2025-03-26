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
        """Generate src/pages/index.js and src/components/HomepageFeatures/index.js"""
        # Define constants to avoid duplication
        INDEX_JS = 'index.js'
        PACKAGE_JSON = 'package.json'
        
        project_name = os.path.basename(self.repo_path)
        repo_url = ""
        description = f"{project_name} documentation and resources."

        # Extract from package.json if available
        package_json_path = os.path.join(self.repo_path, PACKAGE_JSON)
        if os.path.exists(package_json_path):
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                project_name = package_data.get('name', project_name)
                description = package_data.get('description', description)
                
                if 'repository' in package_data:
                    repo_data = package_data['repository']
                    repo_url = repo_data if isinstance(repo_data, str) else repo_data.get('url', '')

        # Create content for index.js
        index_js_content = f"""import React from 'react';
    import Layout from '@theme/Layout';
    import HomepageFeatures from '../components/HomepageFeatures';

    export default function Home() {{
    return (
        <Layout
        title="{project_name}"
        description="{description}">
        <main>
            <HomepageFeatures />
        </main>
        </Layout>
    );
    }}
    """

        # Create content for HomepageFeatures/index.js
        homepage_features_content = f"""import React from 'react';
    import styles from './styles.module.css';

    export default function HomepageFeatures() {{
    return (
        <section className={{styles.features}}>
        <div className="container">
            <div className="row">
            <div className="col col--4">
                <h3>Quick Start</h3>
                <p>Get started with {project_name} quickly by following the documentation and guides.</p>
            </div>
            <div className="col col--4">
                <h3>Features</h3>
                <p>{description}</p>
            </div>
            <div className="col col--4">
                <h3>Repository</h3>
                <p><a href=\"{repo_url}\" target=\"_blank\" rel=\"noopener noreferrer\">GitHub Repository</a></p>
            </div>
            </div>
        </div>
        </section>
    );
    }}
    """

        # Apply AI enhancement if enabled
        if self.use_ai:
            index_js_content = enhance_with_ai(index_js_content, INDEX_JS, self.use_ai, self.logger)
            homepage_features_content = enhance_with_ai(homepage_features_content, 'HomepageFeatures', self.use_ai, self.logger)

        # Create directories and write files
        index_js_dir = os.path.join(self.output_dir, 'src', 'pages')
        features_js_dir = os.path.join(self.output_dir, 'src', 'components', 'HomepageFeatures')
        
        os.makedirs(index_js_dir, exist_ok=True)
        os.makedirs(features_js_dir, exist_ok=True)

        # Create styles.module.css for HomepageFeatures
        with open(os.path.join(features_js_dir, 'styles.module.css'), 'w') as f:
            f.write("""
.features {
  display: flex;
  align-items: center;
  padding: 2rem 0;
  width: 100%;
}
""")

        with open(os.path.join(index_js_dir, INDEX_JS), 'w') as f:
            f.write(index_js_content)

        with open(os.path.join(features_js_dir, INDEX_JS), 'w') as f:
            f.write(homepage_features_content)

        self.logger.info(f"Generated homepage {INDEX_JS} and HomepageFeatures/{INDEX_JS}")

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
        
        for docs_dir in docs_dirs:
            dir_path = os.path.join(self.repo_path, docs_dir)
            if os.path.exists(dir_path):
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        if file.endswith(('.md', '.rst')):
                            with open(os.path.join(root, file), 'r') as f:
                                guides_content.append(f.read())
        
        if not guides_content:
            return None
            
        return self._format_page(
            title="Guides & Tutorials",
            content="\n\n---\n\n".join(guides_content)
        )

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