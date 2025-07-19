# -*- coding: utf-8 -*-
"""
Report Helper 安装配置文件

用于安装和分发 Report Helper 应用程序。
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
with open("docs/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取依赖文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="report-helper",
    version="1.0.0",
    author="Report Helper Team",
    author_email="support@reporthelper.com",
    description="工作日志助手 - 管理工作日志和生成报告的桌面应用程序",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reporthelper/report-helper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "report-helper=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["../resources/*", "../config.json"],
    },
    zip_safe=False,
)