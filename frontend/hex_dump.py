import sys
import os

def analyze_file(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    with open(path, 'rb') as f:
        content = f.read()
    
    # Check for non-ASCII
    for i, byte in enumerate(content):
        if byte > 127:
            print(f"Non-ASCII at byte {i}: {hex(byte)}")
    
    # Show last 500 bytes as hex and chars
    last_part = content[-500:]
    print("\n--- Tail Hex Dump ---")
    for i in range(0, len(last_part), 16):
        chunk = last_part[i:i+16]
        hex_vals = ' '.join(f'{b:02x}' for b in chunk)
        chars = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        print(f"{i:04x}: {hex_vals:<48} | {chars}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_file(sys.argv[1])
    else:
        print("Usage: python hex_dump.py <file_path>")
