# Docusaurus Generator

<div align="center">
<h1 align="center">Docusaurus Generator</h1>
</div>

<pre align="center">Automated documentation generator that converts repository content into a complete Docusaurus site</pre>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![npm](https://img.shields.io/badge/npm-required-red)](https://www.npmjs.com/)

![Docusaurus Generator Screenshot](https://via.placeholder.com/800x400?text=Docusaurus+Generator+Screenshot)

Docusaurus Generator is a powerful tool that analyzes your code repository, automatically extracts documentation, and generates a complete Docusaurus documentation site. It's designed for developers who want to maintain quality documentation with minimal effort. The tool intelligently parses READMEs, source code, and other repository files to create a comprehensive and well-structured documentation site.

[Documentation](https://github.com/yourusername/docusaurus_generator#readme) | [Issue Tracker](https://github.com/yourusername/docusaurus_generator/issues)

## Features

* Automatically generates documentation from repository content
* Creates a complete Docusaurus site structure with proper configuration
* Extracts API documentation from source code
* Generates homepage, sidebar, and navigation components
* Supports optional AI enhancement for better documentation quality
* One-command setup and launch of Docusaurus server
* Works with multiple programming languages (Python, JavaScript, Java, etc.)
* Customizable output via configuration files

## Contents

* [Quick Start](#quick-start)
* [Changelog](#changelog)
* [FAQ](#frequently-asked-questions-faq)
* [Contributing Guide](#contributing)
* [License](#license)
* [Support](#support)

## Quick Start

This guide provides a quick way to get started with Docusaurus Generator. For more comprehensive documentation, see the full documentation in this README.

### Requirements

* Python 3.6 or higher
* pip (Python package manager)
* npm (Node.js package manager)
* Git (for repository analysis)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yunks128/docusaurus-generator.git
   cd docusaurus-generator
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. Verify installation:
   ```bash
   docusaurus-generator --help
   ```

### Run Instructions

1. Generate documentation for a repository:
   ```bash
   docusaurus-generator /path/to/your/repo --output-dir ./docs-site
   ```

2. Generate, install dependencies, and start the server in one command:
   ```bash
   docusaurus-generator /path/to/your/repo --install --start
   ```

3. Open your browser to view the generated documentation site:
   ```
   http://localhost:3000
   ```

### Usage Examples

* **Basic documentation generation**:
  ```bash
  docusaurus-generator /path/to/your/repo
  ```

* **Generate documentation with custom configuration**:
  ```bash
  docusaurus-generator /path/to/your/repo --config ./my-config.yaml
  ```

* **Generate documentation with AI enhancement**:
  ```bash
  docusaurus-generator /path/to/your/repo --use-ai "openai/gpt-4o"
  docusaurus-generator /path/to/your/repo --use-ai "ollama/llama3.3"

  ```

* **Using from Python**:
  ```python
  from docusaurus_generator import DocusaurusGenerator
  
  generator = DocusaurusGenerator(
      repo_path="/path/to/your/repo",
      output_dir="./docs-site",
      config={"url": "https://example.com", "baseUrl": "/docs/"}
  )
  
  generator.setup_and_start(install=True, start=True)
  ```

### Available Command-line Options

- `repo_path`: Path to the repository (required)
- `--output-dir`, `-o`: Directory where documentation should be generated (default: `./docusaurus`)
- `--config`, `-c`: Path to configuration file
- `--use-ai`: Enable AI enhancement with specified model (e.g., "openai/gpt-4o")
- `--verbose`, `-v`: Enable verbose logging
- `--install`: Install Docusaurus dependencies
- `--start`: Start Docusaurus development server after generation

## Changelog

See our [CHANGELOG.md](CHANGELOG.md) for a history of our changes.

See our [releases page](https://github.com/yourusername/docusaurus_generator/releases) for our key versioned releases.

## Frequently Asked Questions (FAQ)

1. **How does Docusaurus Generator decide what to include in the documentation?**
   - It analyzes repository files including READMEs, source code, and configuration files to generate appropriate sections based on repository content.

2. **Does it work with any programming language?**
   - Yes, it works with multiple languages including Python, JavaScript, Java, C++, and others. The API documentation extraction features are language-specific.

3. **How can I customize the generated documentation?**
   - You can use a configuration file (YAML format) to specify various options. See the `config.yaml` sample for details.

4. **What is the AI enhancement feature?**
   - This optional feature uses AI to improve documentation quality by enhancing descriptions, adding examples, and improving readability.

5. **Do I need to have Docusaurus installed beforehand?**
   - No, the tool handles the Docusaurus installation process with the `--install` flag.

## Contributing

Interested in contributing to our project? Please follow these steps:

1. Create a GitHub issue describing what changes you need
2. [Fork](https://github.com/yourusername/docusaurus_generator/fork) this repo
3. Make your modifications in your own fork
4. Make a pull-request in this repo with the code in your fork and tag the repo owner as a reviewer

**Working on your first pull request?** See guide: [How to Contribute to an Open Source Project on GitHub](https://kcd.im/pull-request)

We welcome contributions of all types including:
- Bug fixes
- Feature additions
- Documentation improvements
- Test case additions
- Examples and usage samples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, bug reports, or feature requests, please [open an issue](https://github.com/yourusername/docusaurus_generator/issues).

Key maintainers:
- [@yunks128](https://github.com/yunks128)
