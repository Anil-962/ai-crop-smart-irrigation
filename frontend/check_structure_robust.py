import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def check_structure(text):
    stack = []
    in_string = False
    string_char = None
    in_backtick = False
    in_comment = False
    comment_type = None
    
    for i, char in enumerate(text):
        if not in_string and not in_backtick:
            if not in_comment:
                if text[i:i+2] == '//':
                    in_comment = True
                    comment_type = 'line'
                    continue
                elif text[i:i+2] == '/*':
                    in_comment = True
                    comment_type = 'block'
                    continue
            else:
                if comment_type == 'line' and char == '\n':
                    in_comment = False
                elif comment_type == 'block' and text[i:i+2] == '*/':
                    in_comment = False
                continue
        
        if not in_comment:
            if not in_string and not in_backtick:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                elif char == '`':
                    in_backtick = True
                elif char in ['{', '[', '(']:
                    stack.append((char, i))
                elif char in ['}', ']', ')']:
                    if not stack:
                        print(f"Extra closing {char} at {i}")
                    else:
                        top, pos = stack.pop()
                        if (top == '{' and char != '}') or (top == '[' and char != ']') or (top == '(' and char != ')'):
                            print(f"Mismatched {top} at {pos} with {char} at {i}")
            elif in_string:
                if char == string_char and text[i-1] != '\\':
                    in_string = False
            elif in_backtick:
                if char == '`' and text[i-1] != '\\':
                    in_backtick = False
                    
    print(f"Stack size at end: {len(stack)}")
    for char, pos in stack:
        line_no = text.count('\n', 0, pos) + 1
        print(f"Unclosed {char} at index {pos} (Line {line_no})")
    
    if in_string: print(f"Unclosed string {string_char}")
    if in_backtick: print("Unclosed backtick")
    if in_comment: print("Unclosed comment")

check_structure(content)
