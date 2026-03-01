import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace patterns like /5 /10 /20 /40 with _5 _10 _20 _40
# These are the tailwind opacity values that use slashes.
# esbuild might be misparsing them as regex starts if they are inside template literals or certain JSX contexts.
new_content = re.sub(r'/([0-9]+)', r'_\1', content)

# Also check for any other literal / that might be a problem
# But we must be careful not to break closing tags like </div>
# Closing tags are </
# Self closing are />
# We will ONLY replace / when it's NOT part of a tag.

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_content)

print("Global slash-opacity replacement complete.")
