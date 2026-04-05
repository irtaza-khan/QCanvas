"""
Dataset Loader Module

This module handles loading and managing quantum code datasets in JSONL format.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com

Purpose:
    - Load JSONL dataset files
    - Parse and validate dataset entries
    - Filter and query datasets
    - Provide dataset statistics
    - Support batch loading and iteration

Input:
    - JSONL file paths
    - Filter criteria (framework, quality, etc.)
    - Batch size for processing

Output:
    - Dataset entries (dictionaries)
    - Dataset statistics
    - Filtered subsets
    - Iterator for batch processing

Dependencies:
    - json: For JSONL parsing
    - pathlib: For file path handling
    - typing: For type hints

Links to other modules:
    - Used by: DataPreprocessor, KnowledgeBase
    - Uses: File system for dataset access
    - Part of: Data processing pipeline
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Iterator, Callable, Any
from collections import Counter


class DatasetLoader:
    """
    Loads and manages quantum code datasets in JSONL format.
    
    Provides functionality for loading, filtering, and iterating over
    dataset entries with support for batch processing.
    """
    
    def __init__(self, dataset_path: Path):
        """
        Initialize the DatasetLoader.
        
        Args:
            dataset_path: Path to the JSONL dataset file
        """
        self.dataset_path = Path(dataset_path)
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {self.dataset_path}")
        
        self._entries: Optional[List[Dict]] = None
        self._stats: Optional[Dict] = None
    
    def load(self, lazy: bool = False) -> List[Dict]:
        """
        Load all entries from the dataset.
        
        Args:
            lazy: If True, don't cache entries in memory
            
        Returns:
            List of dataset entries
        """
        if not lazy and self._entries is not None:
            return self._entries
        
        entries = []
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Skipping invalid JSON on line {line_no}: {e}")
                    continue
        
        if not lazy:
            self._entries = entries
        
        return entries
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Calculate and return dataset statistics.
        
        Returns:
            Dictionary with statistics
        """
        if self._stats is not None:
            return self._stats
        
        entries = self.load()
        
        # Initialize stats with default values
        stats = {
            "total": 0,
            "frameworks": {},
            "avg_code_length": 0,
            "min_code_length": 0,
            "max_code_length": 0,
            "with_descriptions": 0,
            "description_coverage": 0.0,
        }
        
        if not entries:
            self._stats = stats
            return stats
        
        frameworks = Counter(entry.get("framework", "Unknown") for entry in entries)
        code_lengths = [
            len(entry.get("code", "")) for entry in entries if entry.get("code")
        ]
        with_descriptions = sum(
            1 for entry in entries if entry.get("description")
        )
        
        # Update stats with calculated values
        stats.update({
            "total": len(entries),
            "frameworks": dict(frameworks),
            "avg_code_length": sum(code_lengths) / len(code_lengths) if code_lengths else 0,
            "min_code_length": min(code_lengths) if code_lengths else 0,
            "max_code_length": max(code_lengths) if code_lengths else 0,
            "with_descriptions": with_descriptions,
            "description_coverage": with_descriptions / len(entries) if entries else 0.0,
        })
        
        self._stats = stats
        return stats
    
    def filter(
        self,
        framework: Optional[str] = None,
        min_code_length: Optional[int] = None,
        max_code_length: Optional[int] = None,
        has_description: Optional[bool] = None,
        custom_filter: Optional[Callable[[Dict], bool]] = None,
    ) -> List[Dict]:
        """
        Filter dataset entries based on criteria.
        
        Args:
            framework: Filter by framework name
            min_code_length: Minimum code length
            max_code_length: Maximum code length
            has_description: Filter by presence of description
            custom_filter: Custom filter function
            
        Returns:
            Filtered list of entries
        """
        entries = self.load()
        filtered = []
        
        for entry in entries:
            # Framework filter
            if framework and entry.get("framework") != framework:
                continue
            
            # Code length filters
            code_length = len(entry.get("code", ""))
            if min_code_length and code_length < min_code_length:
                continue
            if max_code_length and code_length > max_code_length:
                continue
            
            # Description filter
            if has_description is not None:
                has_desc = bool(entry.get("description"))
                if has_description != has_desc:
                    continue
            
            # Custom filter
            if custom_filter and not custom_filter(entry):
                continue
            
            filtered.append(entry)
        
        return filtered
    
    def get_by_framework(self, framework: str) -> List[Dict]:
        """
        Get all entries for a specific framework.
        
        Args:
            framework: Framework name
            
        Returns:
            List of entries for the framework
        """
        return self.filter(framework=framework)
    
    def iter_batches(self, batch_size: int = 100) -> Iterator[List[Dict]]:
        """
        Iterate over dataset in batches.
        
        Args:
            batch_size: Number of entries per batch
            
        Yields:
            Batches of entries
        """
        entries = self.load()
        
        for i in range(0, len(entries), batch_size):
            yield entries[i:i + batch_size]
    
    def sample(self, n: int, seed: Optional[int] = None) -> List[Dict]:
        """
        Sample n random entries from the dataset.
        
        Args:
            n: Number of samples to return
            seed: Random seed for reproducibility
            
        Returns:
            List of sampled entries
        """
        import random
        
        entries = self.load()
        
        if seed is not None:
            random.seed(seed)
        
        if n >= len(entries):
            return entries
        
        return random.sample(entries, n)
    
    def save_filtered(
        self,
        filtered_entries: List[Dict],
        output_path: Path,
    ) -> Path:
        """
        Save filtered entries to a new JSONL file.
        
        Args:
            filtered_entries: List of entries to save
            output_path: Path to output file
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in filtered_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        return output_path
    
    def print_stats(self) -> None:
        """Print dataset statistics to console."""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print(f"Dataset Statistics: {self.dataset_path.name}")
        print("="*60)
        print(f"Total entries: {stats['total']}")
        print("\nFrameworks:")
        for framework, count in stats['frameworks'].items():
            print(f"  - {framework}: {count}")
        print("\nCode length:")
        print(f"  - Average: {stats['avg_code_length']:.0f} characters")
        print(f"  - Min: {stats['min_code_length']} characters")
        print(f"  - Max: {stats['max_code_length']} characters")
        print("\nDescriptions:")
        print(f"  - With descriptions: {stats['with_descriptions']}")
        print(f"  - Coverage: {stats['description_coverage']:.1%}")
        print("="*60 + "\n")


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load and analyze quantum code dataset")
    parser.add_argument("dataset", type=str, help="Path to JSONL dataset file")
    parser.add_argument("--stats", action="store_true", help="Print dataset statistics")
    parser.add_argument("--framework", type=str, help="Filter by framework")
    parser.add_argument("--sample", type=int, help="Sample n random entries")
    parser.add_argument("--output", type=str, help="Save filtered/sampled data to file")
    
    args = parser.parse_args()
    
    loader = DatasetLoader(Path(args.dataset))
    
    if args.stats:
        loader.print_stats()
    
    if args.framework:
        filtered = loader.get_by_framework(args.framework)
        print(f"Found {len(filtered)} entries for {args.framework}")
        if args.output:
            loader.save_filtered(filtered, Path(args.output))
    
    if args.sample:
        sampled = loader.sample(args.sample)
        print(f"Sampled {len(sampled)} entries")
        if args.output:
            loader.save_filtered(sampled, Path(args.output))


if __name__ == "__main__":
    main()
