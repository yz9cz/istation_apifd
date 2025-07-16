#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iStation API Setup Script
سكريبت إعداد مشروع iStation API
"""

from setuptools import setup, find_packages
import os

# قراءة محتوى README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# قراءة متطلبات المشروع
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="istation-api",
    version="2.0.0",
    author="iStation Team",
    author_email="support@istation.com",
    description="API محلي عالي الأداء للبحث عن أسماء اللاعبين في الألعاب المختلفة",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/istation/istation-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "requests>=2.31.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "istation-api=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="api, gaming, pubg, freefire, jawaker, bigolive, poppolive, player, lookup",
    project_urls={
        "Bug Reports": "https://github.com/istation/istation-api/issues",
        "Source": "https://github.com/istation/istation-api",
        "Documentation": "http://localhost:8001/docs",
    },
)
