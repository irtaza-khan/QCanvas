"""
Description Generator Module

This module generates natural language descriptions for quantum code samples
using rule-based and ML-assisted approaches.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com

Purpose:
    - Generate descriptions for code samples
    - Extract key information (functions, classes, algorithms)
    - Use rule-based heuristics for description generation
    - Optionally use ML models for enhanced descriptions
    - Create educational explanations

Input:
    - Code samples (with or without existing descriptions)
    - Framework type
    - Generation parameters (use_ml, description_style)

Output:
    - Code samples with descriptions
    - Description quality metrics
    - Generation statistics

Dependencies:
    - transformers: For ML-based summarization (optional)
    - re: For pattern matching and extraction
    - json: For data handling
    - torch: For PyTorch backend (if using ML)

Links to other modules:
    - Used by: Data preprocessing pipeline
    - Uses: Transformers (optional) for ML summarization
    - Output feeds into: KnowledgeBase
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class DescriptionGenerator:
    """
    Generates natural language descriptions for quantum code samples.
    
    Supports both rule-based and ML-assisted description generation.
    """
    
    # Cirq-specific keyword mappings
    FRAMEWORK_KEYWORDS = {
        "Cirq": {
            "circuit": "quantum circuit construction",
            "measure": "measurement operations",
            "gate": "quantum gate operations",
            "decomposition": "matrix or operator decomposition",
            "benchmark": "benchmark performance tests",
            "simulator": "quantum circuit simulation",
            "optimize": "circuit optimization",
            "transform": "circuit transformation",
            "qubit": "qubit operations",
            "moment": "circuit moments",
        }
    }
    
    # Algorithm detection patterns
    ALGORITHM_PATTERNS = {
        "vqe": [r"vqe", r"variational", r"eigensolver", r"ground.?state"],
        "qaoa": [r"qaoa", r"max.?cut", r"optimization"],
        "grover": [r"grover", r"amplitude.?amplification", r"oracle"],
        "qft": [r"qft", r"quantum.?fourier.?transform", r"fourier"],
        "teleportation": [r"teleport", r"bell.?state"],
        "shor": [r"shor", r"period.?finding", r"factorization"],
    }
    
    def __init__(
        self,
        use_ml: bool = False,
        ml_model: str = "facebook/bart-large-cnn",
        device: str = "auto",
    ):
        """
        Initialize the DescriptionGenerator.
        
        Args:
            use_ml: Whether to use ML-based summarization
            ml_model: Hugging Face model for summarization
            device: Device to run ML model on ("auto", "cpu", "cuda")
        """
        self.use_ml = use_ml and TRANSFORMERS_AVAILABLE
        self.ml_model = ml_model
        self.device = device
        self.summarizer = None
        
        if self.use_ml:
            try:
                print(f"Loading ML summarizer: {ml_model}...")
                self.summarizer = pipeline(
                    "summarization",
                    model=ml_model,
                    device_map=device if device != "auto" else None,
                )
                print("✅ ML summarizer loaded successfully")
            except Exception as e:
                print(f"⚠️  Failed to load ML summarizer: {e}")
                print("Falling back to rule-based generation")
                self.use_ml = False
    
    def extract_code_structure(self, code: str) -> Dict[str, List[str]]:
        """
        Extract structural information from code.
        
        Args:
            code: Code content
            
        Returns:
            Dictionary with functions, classes, and imports
        """
        func_matches = re.findall(r'def\s+([a-zA-Z_]\w*)', code)
        class_matches = re.findall(r'class\s+([a-zA-Z_]\w*)', code)
        import_matches = re.findall(r'import\s+([a-zA-Z_][\w.]*)', code)
        from_matches = re.findall(r'from\s+([a-zA-Z_][\w.]*)\s+import', code)
        
        return {
            "functions": func_matches,
            "classes": class_matches,
            "imports": import_matches + from_matches,
        }
    
    def detect_algorithm(self, code: str) -> Optional[str]:
        """
        Detect quantum algorithm from code patterns.
        
        Args:
            code: Code content
            
        Returns:
            Algorithm name if detected, None otherwise
        """
        code_lower = code.lower()
        for algorithm, patterns in self.ALGORITHM_PATTERNS.items():
            if any(re.search(p, code_lower) for p in patterns):
                return algorithm.upper()
        return None
    
    def generate_rule_based_description(
        self,
        code: str,
        framework: str,
    ) -> str:
        """
        Generate description using rule-based heuristics.
        
        Args:
            code: Code content
            framework: Framework name
            
        Returns:
            Generated description
        """
        code_lower = code.lower()
        structure = self.extract_code_structure(code)
        algorithm = self.detect_algorithm(code)
        
        # Get framework-specific keywords
        keywords_map = self.FRAMEWORK_KEYWORDS.get(framework, {})
        detected_keywords = []
        
        for keyword, description in keywords_map.items():
            if keyword in code_lower:
                detected_keywords.append(description)
        
        # Build description components
        parts = []
        
        # Algorithm detection
        if algorithm:
            parts.append(f"Implements {algorithm} algorithm")
        
        # Function/class information
        if structure["functions"]:
            main_funcs = structure["functions"][:3]  # Top 3 functions
            if len(main_funcs) == 1:
                parts.append(f"defines function {main_funcs[0]}")
            elif len(main_funcs) > 1:
                parts.append(f"defines functions: {', '.join(main_funcs)}")
        
        if structure["classes"]:
            main_classes = structure["classes"][:2]  # Top 2 classes
            if len(main_classes) == 1:
                parts.append(f"defines class {main_classes[0]}")
            elif len(main_classes) > 1:
                parts.append(f"defines classes: {', '.join(main_classes)}")
        
        # Keyword-based description
        if detected_keywords:
            if len(detected_keywords) == 1:
                parts.append(f"demonstrates {detected_keywords[0]}")
            else:
                parts.append(f"demonstrates {', '.join(detected_keywords[:-1])} and {detected_keywords[-1]}")
        
        # Framework mention
        framework_part = f"using {framework}"
        
        # Combine parts
        if parts:
            description = f"This code {', '.join(parts)} {framework_part}."
        else:
            description = f"A {framework} code example demonstrating quantum computing functionality."
        
        return description
    
    def generate_ml_description(self, code: str, max_input_length: int = 2000) -> Optional[str]:
        """
        Generate description using ML summarization.
        
        Args:
            code: Code content
            max_input_length: Maximum code length for ML input
            
        Returns:
            ML-generated summary or None if generation fails
        """
        if not self.summarizer:
            return None
        
        try:
            # Truncate code if too long
            code_snippet = code[:max_input_length]
            
            # Generate summary
            result = self.summarizer(
                code_snippet,
                max_length=50,
                min_length=10,
                do_sample=False,
            )
            
            return result[0]['summary_text']
        except Exception as e:
            return None
    
    def generate_description(
        self,
        code: str,
        framework: str,
        use_ml: Optional[bool] = None,
    ) -> str:
        """
        Generate description for code sample.
        
        Args:
            code: Code content
            framework: Framework name
            use_ml: Override instance use_ml setting
            
        Returns:
            Generated description
        """
        use_ml = use_ml if use_ml is not None else self.use_ml
        
        # Start with rule-based description
        description = self.generate_rule_based_description(code, framework)
        
        # Optionally enhance with ML
        if use_ml:
            ml_summary = self.generate_ml_description(code)
            if ml_summary:
                description = f"{description} ML Summary: {ml_summary}"
        
        return description
    
    def add_descriptions_to_dataset(
        self,
        input_path: Path,
        output_path: Path,
        use_ml: Optional[bool] = None,
        batch_size: int = 100,
    ) -> Dict:
        """
        Add descriptions to all entries in a JSONL dataset.
        
        Args:
            input_path: Path to input JSONL file
            output_path: Path to output JSONL file
            use_ml: Whether to use ML summarization
            batch_size: Batch size for processing
            
        Returns:
            Statistics dictionary
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        stats = {
            "total": 0,
            "processed": 0,
            "skipped": 0,
            "errors": 0,
        }
        
        output_entries = []
        
        # Read input file
        print(f"Reading dataset from {input_path}...")
        with open(input_path, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
        
        stats["total"] = len(lines)
        
        # Process entries
        print(f"Generating descriptions for {stats['total']} entries...")
        for line_no, line in enumerate(tqdm(lines, desc="Generating descriptions"), 1):
            try:
                entry = json.loads(line.strip())
                code = entry.get("code", "")
                framework = entry.get("framework", "Unknown")
                
                if not code.strip():
                    stats["skipped"] += 1
                    continue
                
                # Generate description
                description = self.generate_description(code, framework, use_ml=use_ml)
                entry["description"] = description
                
                output_entries.append(entry)
                stats["processed"] += 1
                
            except json.JSONDecodeError:
                print(f"⚠️  Skipping invalid JSON on line {line_no}")
                stats["errors"] += 1
            except Exception as e:
                print(f"⚠️  Error processing line {line_no}: {e}")
                stats["errors"] += 1
        
        # Write output file
        print(f"Writing output to {output_path}...")
        with open(output_path, "w", encoding="utf-8") as outfile:
            for entry in output_entries:
                # Ensure code formatting is preserved
                if 'code' in entry and isinstance(entry['code'], str):
                    # Normalize line endings and trailing whitespace
                    code_lines = [line.rstrip() for line in entry['code'].split('\n')]
                    # Remove empty lines at start/end but preserve internal structure
                    while code_lines and not code_lines[0].strip():
                        code_lines.pop(0)
                    while code_lines and not code_lines[-1].strip():
                        code_lines.pop()
                    entry['code'] = '\n'.join(code_lines)
                outfile.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        # Print statistics
        print(f"\n{'='*60}")
        print(f"✅ Description generation complete!")
        print(f"{'='*60}")
        print(f"Total entries: {stats['total']}")
        print(f"Processed: {stats['processed']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print(f"\n💾 Saved to: {output_path}")
        print(f"{'='*60}\n")
        
        return stats


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate descriptions for quantum code dataset")
    parser.add_argument("input", type=str, help="Input JSONL file path")
    parser.add_argument("output", type=str, help="Output JSONL file path")
    parser.add_argument("--use-ml", action="store_true", help="Use ML-based summarization")
    parser.add_argument("--ml-model", type=str, default="facebook/bart-large-cnn",
                       help="ML model for summarization")
    
    args = parser.parse_args()
    
    generator = DescriptionGenerator(use_ml=args.use_ml, ml_model=args.ml_model)
    generator.add_descriptions_to_dataset(
        Path(args.input),
        Path(args.output),
        use_ml=args.use_ml,
    )


if __name__ == "__main__":
    main()
