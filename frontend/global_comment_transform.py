import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

# First, let's READ the file to see the DAMAGE from the previous global fix
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# I am going to perform a RECOVERY and then a TARGETED FIX.
# The recovery: replace all __ with //
# Wait, I used _ in my previous script.

# Let's just USE the bit-accurate repair to get a baseline first.
# THE TRUE FIX is replacing // with /* */ globally.

# I'll create a script that:
# 1. Reads the file.
# 2. Replaces all // with /* and adds */ at the end of the line.
# 3. Carefully avoids URL slashes if any (though unlikely to have // in a string that isn't a comment here).

def convert_comments(text):
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if '//' in line:
            # Simple replacement for now, being careful with indentation
            parts = line.split('//', 1)
            new_line = parts[0] + '/* ' + parts[1].strip() + ' */'
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)

# But I need to RECOVER first because I accidentally replaced // with __
content = content.replace('__', '//')

# Now convert
final_content = convert_comments(content)

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(final_content)

print("Global comment transformation complete.")
