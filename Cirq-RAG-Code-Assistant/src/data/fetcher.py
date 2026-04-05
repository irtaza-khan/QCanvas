"""
Dataset Fetcher Module

This module handles fetching quantum computing code from GitHub repositories
and extracting relevant code samples for the knowledge base.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com

Purpose:
    - Clone GitHub repositories (Cirq-focused)
    - Extract relevant Cirq code samples
    - Filter code based on relevance heuristics
    - Save extracted code to JSONL format

Input:
    - Repository URLs and framework names
    - Filtering criteria (patterns, skip keywords)
    - Output directory path

Output:
    - JSONL file with extracted code samples
    - Metadata (framework, file path, code content)
    - Statistics about extraction process

Dependencies:
    - GitPython: For cloning repositories
    - os, json, re: For file operations and pattern matching
    - tqdm: For progress tracking
    - pathlib: For path handling

Links to other modules:
    - Used by: Data preprocessing pipeline
    - Uses: GitPython for repository access
    - Output feeds into: DataPreprocessor, DescriptionGenerator
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

try:
    from git import Repo
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("Warning: GitPython not available. Repository cloning will not work.")


class DatasetFetcher:
    """
    Fetches Cirq quantum computing code from GitHub repositories.
    
    This class handles cloning Cirq repositories, extracting relevant code samples,
    and saving them to JSONL format for further processing.
    """
    
    # Default repository configurations (Cirq-focused)
    DEFAULT_REPOS = {
        "Cirq": [
            "https://github.com/quantumlib/Cirq",
            "https://github.com/quantumlib/Quantum-Chess",
        ]
    }
    
    # Cirq-specific code patterns for relevance detection
    FRAMEWORK_PATTERNS = {
        "Cirq": [
            r"cirq\.Circuit",
            r"cirq\.LineQubit",
            r"cirq\.GridQubit",
            r"cirq\.measure",
            r"cirq\.Simulator",
            r"import\s+cirq",
            r"from\s+cirq",
        ]
    }
    
    # Keywords to skip in file paths
    SKIP_KEYWORDS = [
        "test",
        "setup",
        "conftest",
        "__init__",
        "dev_tools",
        "docs",
        ".github",
        "examples",  # Can be added if needed
    ]
    
    def __init__(
        self,
        repos: Optional[Dict[str, List[str]]] = None,
        repos_dir: str = "repos",
        output_dir: str = "data/datasets",
        skip_keywords: Optional[List[str]] = None,
    ):
        """
        Initialize the DatasetFetcher.
        
        Args:
            repos: Dictionary mapping framework names to repository URLs.
                   If None, uses DEFAULT_REPOS (Cirq-focused).
            repos_dir: Directory to clone repositories into.
            output_dir: Directory to save extracted datasets.
            skip_keywords: Additional keywords to skip in file paths.
        """
        self.repos = repos or self.DEFAULT_REPOS
        self.repos_dir = Path(repos_dir)
        self.output_dir = Path(output_dir)
        self._skip_keywords = (skip_keywords or []) + self.SKIP_KEYWORDS
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        
        if not GIT_AVAILABLE:
            raise ImportError(
                "GitPython is required for dataset fetching. "
                "Install it with: pip install GitPython"
            )
    
    def is_relevant_code(self, code: str, framework: str) -> bool:
        """
        Check if code is relevant based on framework-specific patterns.
        
        Args:
            code: Code content to check
            framework: Framework name (Cirq)
            
        Returns:
            True if code contains relevant patterns, False otherwise
        """
        patterns = self.FRAMEWORK_PATTERNS.get(framework, [])
        return any(re.search(p, code, re.IGNORECASE) for p in patterns)
    
    def should_skip_file(self, file_path: str) -> bool:
        """
        Check if file should be skipped based on path keywords.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file should be skipped, False otherwise
        """
        path_lower = file_path.lower()
        return any(keyword in path_lower for keyword in self._skip_keywords)
    
    def clone_repo(self, repo_url: str, force_clone: bool = False) -> Path:
        """
        Clone a repository if it doesn't exist.
        
        Args:
            repo_url: URL of the repository to clone
            force_clone: If True, re-clone even if directory exists
            
        Returns:
            Path to the cloned repository
        """
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = self.repos_dir / repo_name
        
        if repo_path.exists() and not force_clone:
            print(f"Repository {repo_name} already exists. Skipping clone.")
            return repo_path
        
        if force_clone and repo_path.exists():
            import shutil
            shutil.rmtree(repo_path)
        
        print(f"Cloning {repo_url} to {repo_path}...")
        try:
            Repo.clone_from(repo_url, repo_path, depth=1)  # Shallow clone for speed
            print(f"✅ Successfully cloned {repo_name}")
        except Exception as e:
            print(f"❌ Error cloning {repo_url}: {e}")
            raise
        
        return repo_path
    
    def normalize_code_formatting(self, code: str) -> str:
        """
        Normalize code formatting to ensure consistent, readable format.

        Args:
            code: Raw code content

        Returns:
            Normalized code with consistent formatting
        """
        if not code.strip():
            return code

        # Normalize line endings to \n
        code = code.replace('\r\n', '\n').replace('\r', '\n')

        # Remove trailing whitespace from each line
        lines = [line.rstrip() for line in code.split('\n')]

        # Remove empty lines at the beginning and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        # Join back with consistent newlines
        return '\n'.join(lines)

    def extract_framework_code(
        self,
        repo_path: Path,
        framework: str,
        min_code_length: int = 50,
        max_code_length: int = 50000,
    ) -> List[Dict]:
        """
        Extract relevant code samples from a repository.

        Args:
            repo_path: Path to the repository
            framework: Framework name
            min_code_length: Minimum code length to include
            max_code_length: Maximum code length to include

        Returns:
            List of dictionaries with framework, file, and code
        """
        results = []
        repo_path = Path(repo_path)

        if not repo_path.exists():
            print(f"Warning: Repository path {repo_path} does not exist.")
            return results

        # Find all Python files
        python_files = list(repo_path.rglob("*.py"))

        print(f"Scanning {len(python_files)} Python files in {repo_path.name}...")

        for file_path in tqdm(python_files, desc=f"Extracting {framework} code"):
            # Skip irrelevant files
            if self.should_skip_file(str(file_path)):
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
            except Exception:
                continue

            # Normalize code formatting
            code = self.normalize_code_formatting(code)

            # Filter by code length
            if len(code) < min_code_length or len(code) > max_code_length:
                continue

            # Check if code is relevant
            if self.is_relevant_code(code, framework):
                # Use relative path for cleaner output
                rel_path = file_path.relative_to(repo_path)
                results.append({
                    "framework": framework,
                    "file": str(rel_path),
                    "code": code,
                    "code_length": len(code),
                })

        return results
    
    def fetch_all(
        self,
        output_filename: str = "quantum_code_samples_filtered.jsonl",
        force_clone: bool = False,
        min_code_length: int = 50,
        max_code_length: int = 50000,
    ) -> Path:
        """
        Fetch code from all configured repositories.
        
        Args:
            output_filename: Name of the output JSONL file
            force_clone: If True, re-clone repositories even if they exist
            min_code_length: Minimum code length to include
            max_code_length: Maximum code length to include
            
        Returns:
            Path to the output file
        """
        all_data = []
        stats = {}
        
        for framework, repo_urls in self.repos.items():
            framework_samples = []
            for repo_url in repo_urls:
                try:
                    repo_path = self.clone_repo(repo_url, force_clone=force_clone)
                    samples = self.extract_framework_code(
                        repo_path,
                        framework,
                        min_code_length=min_code_length,
                        max_code_length=max_code_length,
                    )
                    framework_samples.extend(samples)
                    print(f"✅ Collected {len(samples)} samples from {repo_url}")
                except Exception as e:
                    print(f"❌ Error processing {repo_url}: {e}")
                    continue
            
            stats[framework] = len(framework_samples)
            all_data.extend(framework_samples)
        
        # Save to JSONL file
        output_path = self.output_dir / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            for item in all_data:
                # Ensure code is properly formatted before saving
                if 'code' in item:
                    item['code'] = self.normalize_code_formatting(item['code'])
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        # Print statistics
        print("\n" + "="*60)
        print("✅ Extraction complete!")
        print("="*60)
        print(f"Total samples extracted: {len(all_data)}")
        for framework, count in stats.items():
            print(f"  - {framework}: {count} samples")
        print(f"\n💾 Saved to: {output_path}")
        print(f"{'='*60}\n")
        
        return output_path


def main():
    """Main function for command-line usage."""
    fetcher = DatasetFetcher()
    fetcher.fetch_all()


if __name__ == "__main__":
    main()
