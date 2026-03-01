import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def find_all_slashes(text):
    in_string = False
    string_char = None
    in_comment = False
    comment_type = None # 'block' or 'line'
    in_backtick = False
    
    slashes = []
    
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
        
        # Handle backticks
        if not in_comment and not in_string:
            if not in_backtick:
                if char == '`':
                    in_backtick = True
            else:
                if char == '`' and text[i-1] != '\\':
                    in_backtick = False
                    
        # Find slash
        if char == '/':
            state = "CODE"
            if in_string: state = f"STRING({string_char})"
            if in_backtick: state = "BACKTICK"
            if in_comment: state = f"COMMENT({comment_type})"
            
            # Context
            context = text[max(0, i-20):i+21].replace('\n', '\\n')
            slashes.append((i, state, context))
        
        i += 1
        
    return slashes

slashes = find_all_slashes(content)
print(f"Total slashes: {len(slashes)}")

# We are looking for slashes in "CODE" state that aren't parts of tags </ or />
naked = []
for i, state, context in slashes:
    if state == "CODE":
        # Check if part of tag
        idx_in_context = 20
        if context[idx_in_context-1] == '<':
            pass
        elif context[idx_in_context+1] == '>':
            pass
        else:
            naked.append((i, context))

print(f"Naked slashes: {len(naked)}")
for i, context in naked:
    line_no = content.count('\n', 0, i) + 1
    print(f"Index {i} (Line {line_no}): {repr(context)}")
