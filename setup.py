"""
QCanvas Setup Configuration

This module provides the setup configuration for the QCanvas quantum computing
platform, including package metadata, dependencies, and installation options.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

from setuptools import setup, find_packages
import os
import re

# Read the README file
def read_readme():
    """Read the README file for long description."""
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = []
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
        return requirements

# Get version from __init__.py
def get_version():
    """Extract version from __init__.py file."""
    version_file = os.path.join("quantum_converters", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as fh:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", fh.read(), re.M)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Package configuration
setup(
    name="qcanvas",
    version=get_version(),
    author="QCanvas Team",
    author_email="team@qcanvas.dev",
    description="A comprehensive quantum computing platform for unified simulation and circuit conversion",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/qcanvas/qcanvas",
    project_urls={
        "Bug Reports": "https://github.com/qcanvas/qcanvas/issues",
        "Source": "https://github.com/qcanvas/qcanvas",
        "Documentation": "https://docs.qcanvas.dev",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
            "isort>=5.12.0",
            "pre-commit>=3.5.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "httpx>=0.25.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
        "monitoring": [
            "prometheus-client>=0.17.0",
            "structlog>=23.2.0",
        ],
        "production": [
            "gunicorn>=21.2.0",
            "uvicorn[standard]>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qcanvas=backend.app.main:main",
            "qcanvas-convert=quantum_converters.cli:main",
            "qcanvas-simulate=quantum_simulator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "quantum_converters": [
            "examples/*.py",
            "examples/*.qasm",
            "config/*.json",
            "config/*.yaml",
        ],
        "quantum_simulator": [
            "examples/*.py",
            "examples/*.qasm",
            "config/*.json",
            "config/*.yaml",
        ],
        "backend": [
            "static/*",
            "templates/*",
        ],
    },
    zip_safe=False,
    keywords=[
        "quantum computing",
        "quantum simulation",
        "circuit conversion",
        "cirq",
        "qiskit",
        "pennylane",
        "openqasm",
        "quantum algorithms",
        "quantum machine learning",
    ],
    platforms=["any"],
    license="MIT",
    maintainer="QCanvas Team",
    maintainer_email="team@qcanvas.dev",
    provides=["qcanvas"],
    requires_python=">=3.8",
    setup_requires=[
        "setuptools>=45.0.0",
        "wheel>=0.37.0",
    ],
    test_suite="tests",
    tests_require=[
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.11.0",
    ],
    # Additional metadata
    metadata_version="2.1",
    name="qcanvas",
    version=get_version(),
    summary="Quantum Unified Simulator Platform",
    description="A comprehensive quantum computing platform that provides unified simulation, circuit conversion, and visualization capabilities across multiple quantum frameworks.",
    keywords=[
        "quantum computing",
        "quantum simulation",
        "circuit conversion",
        "cirq",
        "qiskit",
        "pennylane",
        "openqasm",
        "quantum algorithms",
        "quantum machine learning",
    ],
    author="QCanvas Team",
    author_email="team@qcanvas.dev",
    maintainer="QCanvas Team",
    maintainer_email="team@qcanvas.dev",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    download_url="https://github.com/qcanvas/qcanvas/releases",
    project_urls={
        "Homepage": "https://qcanvas.dev",
        "Documentation": "https://docs.qcanvas.dev",
        "Repository": "https://github.com/qcanvas/qcanvas",
        "Bug Tracker": "https://github.com/qcanvas/qcanvas/issues",
        "Changelog": "https://github.com/qcanvas/qcanvas/blob/main/CHANGELOG.md",
        "Download": "https://github.com/qcanvas/qcanvas/releases",
    },
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
            "isort>=5.12.0",
            "pre-commit>=3.5.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "httpx>=0.25.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
        "monitoring": [
            "prometheus-client>=0.17.0",
            "structlog>=23.2.0",
        ],
        "production": [
            "gunicorn>=21.2.0",
            "uvicorn[standard]>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qcanvas=backend.app.main:main",
            "qcanvas-convert=quantum_converters.cli:main",
            "qcanvas-simulate=quantum_simulator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "quantum_converters": [
            "examples/*.py",
            "examples/*.qasm",
            "config/*.json",
            "config/*.yaml",
        ],
        "quantum_simulator": [
            "examples/*.py",
            "examples/*.qasm",
            "config/*.json",
            "config/*.yaml",
        ],
        "backend": [
            "static/*",
            "templates/*",
        ],
    },
    zip_safe=False,
    platforms=["any"],
    provides=["qcanvas"],
    requires_python=">=3.8",
    setup_requires=[
        "setuptools>=45.0.0",
        "wheel>=0.37.0",
    ],
    test_suite="tests",
    tests_require=[
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.11.0",
    ],
)