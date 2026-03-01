import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'rb') as f:
    content = f.read()

slashes = []
for i in range(len(content)):
    if content[i] == ord('/'):
        # Context bytes
        prev2 = content[i-2] if i > 1 else 0
        prev1 = content[i-1] if i > 0 else 0
        next1 = content[i+1] if i < len(content)-1 else 0
        slashes.append((i, prev2, prev1, ord('/'), next1))

print(f"Total slashes (byte-level): {len(slashes)}")
for i, p2, p1, s, n1 in slashes:
    # Print only if it's NOT part of tag </ (60, 47) or /> (47, 62)
    # and NOT part of comment // (47, 47) or /* (47, 42) or */ (42, 47)
    
    is_tag = (p1 == 60) or (n1 == 62)
    is_comment = (p1 == 47) or (n1 == 47) or (n1 == 42) or (p1 == 42)
    
    if not is_tag and not is_comment:
        line_no = content.count(b'\n', 0, i) + 1
        # Get context string safely
        ctx = content[max(0, i-20):i+21].decode('ascii', errors='replace').replace('\n', ' ')
        print(f"L{line_no} [{i}]: {p2}, {p1}, {s}, {n1} | ctx: {repr(ctx)}")
