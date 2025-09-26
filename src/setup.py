#!/usr/bin/env python3
"""
Setup script for Adaptive Chatbot Professional Distribution
"""

from setuptools import setup, find_packages
import os

# Read requirements
def read_requirements():
    with open('requirements-fixed.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read long description
def read_description():
    with open('README_BUSINESS.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="adaptive-chatbot-pro",
    version="1.0.0",
    description="Professional AI Chatbot with Voice Teaching - Ready for Business",
    long_description=read_description(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/adaptive-chatbot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Business",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'adaptive-chatbot=adaptive_chatbot:main',
            'chatbot-setup=load_preloaded_knowledge:main',
        ],
    },
    include_package_data=True,
    package_data={
        'adaptive_chatbot': [
            '*.json',
            '*.md',
            'data/*',
            'logs/*',
        ],
    },
    keywords="chatbot ai voice hindi business automation customer-service",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/adaptive-chatbot/issues",
        "Funding": "https://github.com/sponsors/yourusername",
        "Source": "https://github.com/yourusername/adaptive-chatbot",
    },
)
