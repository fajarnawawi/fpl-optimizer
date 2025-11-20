"""
Setup script for FPL Optimizer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fpl-optimizer",
    version="1.0.0",
    author="Based on research by Danial Ramezani",
    description="Data-driven Fantasy Premier League team optimization using integer programming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fpl-optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fpl-optimize=src.main:main",
        ],
    },
    keywords="fantasy premier league fpl optimization integer programming machine learning",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/fpl-optimizer/issues",
        "Source": "https://github.com/yourusername/fpl-optimizer",
        "Paper": "https://arxiv.org/abs/2505.02170",
    },
)
