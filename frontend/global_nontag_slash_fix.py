import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace all '/' that are NOT part of a tag (</ or />)
# A simple way is to replace all / with _ and then fix the tags.

# 1. Replace all / with a unique marker
temp = content.replace('/', 'SLASH_MARKER')

# 2. Fix the tags: </ becomes </ and /> becomes />
# Wait, if I replace / with SLASH_MARKER, </ becomes <SLASH_MARKER and /> becomes SLASH_MARKER>
temp = temp.replace('<SLASH_MARKER', '</')
temp = temp.replace('SLASH_MARKER>', '/>')

# Now temp has SLASH_MARKER for all non-tag slashes (like in comments or bg-primary/5)
# Let's replace SLASH_MARKER with _
final = temp.replace('SLASH_MARKER', '_')

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(final)

print("Global non-tag slash replacement complete.")
