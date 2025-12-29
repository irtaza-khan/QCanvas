
try:
    with open('logs/backend.err.log', 'r', errors='ignore') as f:
        content = f.read()
    with open('debug_output.txt', 'w', encoding='utf-8') as f:
        f.write("=== backend.err.log ===\n")
        f.write(content)
        f.write("\n\n")
except Exception as e:
    with open('debug_output.txt', 'w') as f:
        f.write(f"Error reading err log: {e}\n")

try:
    with open('logs/backend.log', 'r', errors='ignore') as f:
        content = f.read()
    with open('debug_output.txt', 'a', encoding='utf-8') as f:
        f.write("=== backend.log ===\n")
        f.write(content)
except Exception as e:
    with open('debug_output.txt', 'a') as f:
        f.write(f"Error reading out log: {e}\n")
