import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The culprits are // comments inside JSX blocks (e.g., inside a div).
# We search for // that are preceded by spaces and followed by word characters,
# and replace them with {/* ... */} IF they look like they are in a JSX context.

# Let's target the SPECIFIC lines identified by ESLint and my previous scans.
culprits = [
    '// Disease Scanner',
    '// Smart Irrigation',
    '// Field Reports',
    '// User Profile',
    '// Alerts Page',
    '// Settings Tab',
    '// 1. Theme Settings',
    '// 2. Language Settings',
    '// Tab Content',
    '// Dashboard',
    '// 1. Zone Overview Section',
    '// 2. KPI Grid Section',
    '// 3. Analytics Section',
    '// Section 2: Irrigation Control Panel',
    '// Section 3: Farm Zones Overview',
    '// Section 5: Recent Activity Log',
    '// Section 4: Weather Summary',
    '// Section 6: AI Intelligence (Bonus)'
]

for culprit in culprits:
    fixed = f'{{/* {culprit.replace("// ", "")} */}}'
    # We must be careful to match the exact spacing if possible, or use regex.
    pattern = re.escape(culprit)
    content = re.sub(pattern, fixed, content)

# Also fix the 'image//' just in case it's still there
content = content.replace('accept="image//"', 'accept="image/*"')

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("JSX comment transformation complete.")
