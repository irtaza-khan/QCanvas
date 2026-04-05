"""
Quick script to test if the notebook cell is checking the right field.
"""

# Simulate the result structure
result = {
    "success": True,  # Validator ran successfully
    "validation_passed": False,  # Code validation FAILED
    "stage": "simulation_failed",
    "error": "Circuit has no measurements to sample."
}

print("Current notebook logic:")
print(f"  result.get('success'): {result.get('success')}")
print(f"  Shows as: {'✅ PASSED' if result.get('success') else '❌ FAILED'}")
print()
print("Correct logic should be:")
print(f"  result.get('validation_passed'): {result.get('validation_passed')}")  
print(f"  Should show: {'✅ PASSED' if result.get('validation_passed') else '❌ FAILED'}")
print()
print("Fix: Change notebook cell from result.get('success') to result.get('validation_passed')")
