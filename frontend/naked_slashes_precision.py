import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def find_unbalanced_slash(text):
    in_string = False
    string_marker = None
    in_backtick = False
    in_comment_line = False
    in_comment_block = False
    in_jsx_attr = False # Simplified
    
    # We will track if we are in a regex
    # But detecting regex start in JS is notoriously hard.
    # However, for this task, we can look for any / that looks like a start
    
    slashes = []
    
    i = 0
    while i < len(text):
        c = text[i]
        
        # Line comment
        if not in_string and not in_backtick and not in_comment_block:
            if not in_comment_line and text[i:i+2] == '//':
                in_comment_line = True
                i += 2
                continue
            if in_comment_line and c == '\n':
                in_comment_line = False
                i += 1
                continue
        
        # Block comment
        if not in_string and not in_backtick and not in_comment_line:
            if not in_comment_block and text[i:i+2] == '/*':
                in_comment_block = True
                i += 2
                continue
            if in_comment_block and text[i:i+2] == '*/':
                in_comment_block = False
                i += 2
                continue
        
        if in_comment_line or in_comment_block:
            i += 1
            continue
            
        # Strings
        if not in_backtick:
            if not in_string:
                if c in ["'", '"']:
                    in_string = True
                    string_marker = c
            else:
                if c == string_marker and text[i-1] != '\\':
                    in_string = False
        
        if in_string:
            i += 1
            continue
            
        # Backticks
        if not in_backtick:
            if c == '`':
                in_backtick = True
        else:
            if c == '`' and text[i-1] != '\\':
                in_backtick = False
        
        if in_backtick:
            i += 1
            continue
            
        # If we are here, we are in "CODE" (including JSX text)
        if c == '/':
            # Check for </ or />
            is_tag = False
            if i > 0 and text[i-1] == '<': is_tag = True
            if i < len(text)-1 and text[i+1] == '>': is_tag = True
            
            if not is_tag:
                line_no = text.count('\n', 0, i) + 1
                slashes.append((line_no, i, text[max(0, i-40):i+41].replace('\n', ' ')))
        
        i += 1
        
    return slashes

print("Naked slashes report:")
all_naked = find_unbalanced_slash(content)
for line, idx, ctx in all_naked:
    print(f"L{line} [{idx}]: {repr(ctx)}")
