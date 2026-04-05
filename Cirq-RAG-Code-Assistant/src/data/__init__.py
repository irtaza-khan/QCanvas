"""
Data Processing Module

This module handles data fetching, preprocessing, and loading for the
Cirq-RAG-Code-Assistant knowledge base.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com
"""

# Export data processing components
from .fetcher import DatasetFetcher
from .preprocessor import DataPreprocessor
from .description_generator import DescriptionGenerator
from .dataset_loader import DatasetLoader

__all__ = [
    "DatasetFetcher",
    "DataPreprocessor",
    "DescriptionGenerator",
    "DatasetLoader",
]

