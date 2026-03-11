#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retry NSE analysis after 5 minutes with sound alert
"""
import time
import subprocess
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Waiting 5 minutes before retrying NSE analysis...")
print("   Start time:", time.strftime("%H:%M:%S"))

# Wait 5 minutes (300 seconds)
for remaining in range(300, 0, -30):
    mins, secs = divmod(remaining, 60)
    print(f"   ⏳ {mins:02d}:{secs:02d} remaining...", end='\r')
    time.sleep(30)

print("\n\n5 minutes elapsed! Running analysis now...")

# Play system beep (Windows)
try:
    import winsound
    # Play 3 beeps
    for _ in range(3):
        winsound.Beep(1000, 500)  # 1000 Hz for 500ms
        time.sleep(0.2)
except ImportError:
    print("\a\a\a")  # Fallback: terminal bell

# Run the analysis
print("\n" + "="*80)
subprocess.run([sys.executable, "nse_analysis_modular.py"])

# Final alert
try:
    import winsound
    winsound.Beep(1500, 1000)  # Higher pitch, longer beep when done
except ImportError:
    print("\a")

print("\nAnalysis complete!")

# Made with Bob
