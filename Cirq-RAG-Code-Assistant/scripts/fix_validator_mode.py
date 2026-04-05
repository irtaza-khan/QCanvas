"""
Script to update validator notebooks to use config mode instead of hardcoded mode.

This fixes the issue where notebooks hardcode mode="remote" instead of reading from config.
"""

import json
import sys
from pathlib import Path

def fix_notebook(notebook_path: Path) -> bool:
    """
    Replace hardcoded mode="remote" with mode from config.
    """
    print(f"📄 Processing: {notebook_path.name}")
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        modified = False
        for cell in notebook.get('cells', []):
            if cell['cell_type'] == 'code':
                source = cell.get('source', [])
                
                # Convert to string for easier processing
                if isinstance(source, list):
                    source_str = ''.join(source)
                else:
                    source_str = source
                
                # Check if this cell initializes ValidatorAgent with hardcoded mode
                if 'ValidatorAgent(mode=' in source_str:
                    print(f"  🔧 Found ValidatorAgent initialization")
                    
                    # Replace hardcoded mode with config-based initialization
                    new_source_str = source_str.replace(
                        'ValidatorAgent(mode="remote", retriever=retriever)',
                        'ValidatorAgent(retriever=retriever)  # Mode is read from config.json'
                    ).replace(
                        'ValidatorAgent(mode="local", retriever=retriever)',
                        'ValidatorAgent(retriever=retriever)  # Mode is read from config.json'
                    )
                    
                    if new_source_str != source_str:
                        # Convert back to list format (preserving notebook format)
                        new_source = [line + '\n' if not line.endswith('\n') else line 
                                     for line in new_source_str.split('\n')]
                        # Remove trailing newline from last line
                        if new_source and new_source[-1] == '\n':
                            new_source = new_source[:-1]
                        
                        cell['source'] = new_source
                        modified = True
                        print(f"  ✅ Updated to use config mode")
        
        if modified:
            # Write back
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=4, ensure_ascii=False)
            print(f"  💾 Saved changes to {notebook_path.name}")
            return True
        else:
            print(f"  ℹ️  No changes needed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    project_root = Path(__file__).parent.parent
    notebooks_dir = project_root / "notebooks"
    
    print("🔄 Fixing Validator Mode in Notebooks")
    print("=" * 60)
    print()
    
    # Fix notebooks
    notebooks_to_fix = [
        notebooks_dir / "07_validator_agent.ipynb",
        notebooks_dir / "09_orchestration.ipynb"
    ]
    
    total_modified = 0
    for nb in notebooks_to_fix:
        if nb.exists():
            if fix_notebook(nb):
                total_modified += 1
            print()
        else:
            print(f"⚠️  Not found: {nb}")
            print()
    
    print("=" * 60)
    print(f"✅ Complete! Modified {total_modified} notebook(s)")
    print()
    print("📝 Next steps:")
    print("   1. Restart Jupyter notebook kernel")
    print("   2. Re-run the initialization cells")
    print("   3. Verify logs show 'ValidatorAgent initialized in 'local' mode'")

if __name__ == "__main__":
    main()
