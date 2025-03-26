#!/usr/bin/env python3
"""
Setup script for the docusaurus_generator package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="docusaurus_generator",
    version="0.1.0",
    author="Kyongsik Yun",
    author_email="yunkss@gmail.com",
    description="Generate Docusaurus documentation from repository content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yunks128/docusaurus_generator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "gitpython>=3.1.0",
        "pyyaml>=5.1.0",
        "openai>=0.27.0",  # If using OpenAI for AI enhancement
    ],
    entry_points={
        "console_scripts": [
            "docusaurus-generator=docusaurus_generator.cli:main",
        ],
    },
)