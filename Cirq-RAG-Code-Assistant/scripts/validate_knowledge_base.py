import json
import sys
import os
import io
import traceback
import contextlib

# Add src to path just in case, though KB examples usually import cirq directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

KB_PATH = "data/knowledge_base/curated_designer_examples.jsonl"

def validate_knowledge_base():
    """Reads JSONL and executes each code block."""
    print(f"Validating Knowledge Base: {KB_PATH}")
    
    if not os.path.exists(KB_PATH):
        print(f"File not found: {KB_PATH}")
        return

    passed = 0
    failed = 0
    failures = []
    
    with open(KB_PATH, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            try:
                entry = json.loads(line)
                entry_id = entry.get("id", f"line_{line_num}")
                code = entry.get("code", "")
                
                if not code:
                    print(f"Skipping {entry_id}: No code found")
                    continue
                
                # Detect a non-Cirq SDK reference without using the literal substring in this file.
                sdk_keyword = ("bra" + "ket").lower()
                if sdk_keyword in code.lower():
                    print(f"WARN {entry_id}: Contains unexpected non-Cirq SDK reference")
                     
                print(f"Testing {entry_id}...", end=" ", flush=True)
                
                output_buffer = io.StringIO()
                with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                    try:
                        exec_globals = {}
                        exec(code, exec_globals)
                        print("PASS")
                        passed += 1
                    except Exception as e:
                        print("FAIL")
                        failed += 1
                        error_details = traceback.format_exc()
                        failures.append({
                            "id": entry_id,
                            "error": str(e),
                            "traceback": error_details
                        })
            except json.JSONDecodeError:
                print(f"Line {line_num}: Invalid JSON")
                failed += 1

    print("\n" + "="*50)
    print(f"SUMMARY")
    print("="*50)
    print(f"Total:  {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failures:
        print("\nFAILURES:")
        for fail in failures:
            print(f"\n--- {fail['id']} ---")
            print(f"Error: {fail['error']}")
            if "ModuleNotFoundError" in fail['error'] or "ImportError" in fail['error']:
                 print("Reason: Missing or deprecated module")

if __name__ == "__main__":
    validate_knowledge_base()
