import subprocess
import os
import sys
import time

frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
print(f"Installing in: {frontend_dir}")
result = subprocess.run(['bun', 'install'], cwd=frontend_dir, capture_output=True, text=True, timeout=300)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print(f"Exit code: {result.returncode}")
