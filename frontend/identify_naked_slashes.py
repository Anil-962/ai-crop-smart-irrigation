import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def find_naked_slashes(text):
    in_string = False
    string_char = None
    in_comment = False
    comment_type = None # 'block' or 'line'
    in_backtick = False
    
    results = []
    
    i = 0
    while i < len(text):
        char = text[i]
        
        # Handle comments
        if not in_string and not in_backtick:
            if not in_comment:
                if text[i:i+2] == '//':
                    in_comment = True
                    comment_type = 'line'
                    i += 2
                    continue
                elif text[i:i+2] == '/*':
                    in_comment = True
                    comment_type = 'block'
                    i += 2
                    continue
            else:
                if comment_type == 'line' and char == '\n':
                    in_comment = False
                    i += 1
                    continue
                elif comment_type == 'block' and text[i:i+2] == '*/':
                    in_comment = False
                    i += 2
                    continue
                i += 1
                continue
        
        # Handle strings
        if not in_comment and not in_backtick:
            if not in_string:
                if char in ["'", '"']:
                    in_string = True
                    string_char = char
            else:
                if char == string_char and text[i-1] != '\\':
                    in_string = False
        
        if not in_comment and not in_string:
            if not in_backtick:
                if char == '`':
                    in_backtick = True
            else:
                if char == '`' and text[i-1] != '\\':
                    in_backtick = False
                    
        # Check for naked slash
        if not in_string and not in_comment and not in_backtick:
            if char == '/':
                # Exclude closing tags </ and />
                if text[i-1] == '<':
                    pass # Closing tag part
                elif i+1 < len(text) and text[i+1] == '>':
                    pass # Self closing part
                else:
                    # Potential regex or arithmetic
                    line_start = text.rfind('\n', 0, i) + 1
                    line_no = text.count('\n', 0, i) + 1
                    results.append((line_no, i, text[max(0, i-20):i+20]))
        
        i += 1
        
    return results

slashes = find_naked_slashes(content)
print(f"Total naked slashes found: {len(slashes)}")
for s in slashes:
    print(f"Line {s[0]}: {repr(s[2])}")
