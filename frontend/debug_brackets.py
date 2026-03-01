import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def track_brackets(text):
    stack = []
    in_string = False
    string_marker = None
    in_backtick = False
    in_comment_line = False
    in_comment_block = False
    
    i = 0
    while i < len(text):
        c = text[i]
        
        # Comments
        if not in_string and not in_backtick:
            if not in_comment_block:
                if not in_comment_line and text[i:i+2] == '//':
                    in_comment_line = True
                    i += 2; continue
                if in_comment_line and c == '\n':
                    in_comment_line = False
                    i += 1; continue
            if not in_comment_line:
                if not in_comment_block and text[i:i+2] == '/*':
                    in_comment_block = True
                    i += 2; continue
                if in_comment_block and text[i:i+2] == '*/':
                    in_comment_block = False
                    i += 2; continue
        
        if in_comment_line or in_comment_block:
            i += 1; continue
            
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
            i += 1; continue
            
        # Backticks
        if not in_string:
            if not in_backtick:
                if c == '`':
                    in_backtick = True
            else:
                if c == '`': # Simplistic, doesn't handle ${}
                    # But we'll handle ${} by NOT skipping backtick content
                    pass
        
        # BRACKETS
        if c in ['{', '[', '(']:
            line_no = text.count('\n', 0, i) + 1
            stack.append((c, line_no, i))
        elif c in ['}', ']', ')']:
            line_no = text.count('\n', 0, i) + 1
            if not stack:
                print(f"EXTRA CLOSING {c} at line {line_no}")
            else:
                top_c, top_line, top_idx = stack.pop()
                if (top_c == '{' and c != '}') or (top_c == '[' and c != ']') or (top_c == '(' and c != ')'):
                    print(f"MISMATCH: {top_c} from line {top_line} closed by {c} at line {line_no}")
        
        i += 1
        
    for c, line, idx in stack:
        print(f"UNCLOSED {c} from line {line}")

track_brackets(content)
