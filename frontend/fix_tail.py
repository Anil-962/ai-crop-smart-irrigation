import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We want to replace everything from the end of the settings block to the end of the file.
# Based on previous analysis, we know the problematic part is at the very end.
# Let's find the last ')' which likely belongs to the main return of App.

new_tail = [
    "              </div>\n",
    "            </div>\n",
    "          </main>\n",
    "        </div>\n",
    "\n",
    "        {showToast && (\n",
    "          <Toast\n",
    "            message={toastMessage}\n",
    "            onClose={() => setShowToast(false)}\n",
    "          />\n",
    "        )}\n",
    "      </div>\n",
    "    );\n",
    "  }\n",
    "\n",
    "export default App;\n"
]

# Locate the line "                  }" that ends the settings tab content if possible, or just truncate and replace.
# I'll look for the last "                  }" before line 2190.

target_line = -1
for i in range(len(lines) - 1, 0, -1):
    if "                  }" in lines[i] and i < 2190:
        target_line = i + 1
        break

if target_line != -1:
    new_content = lines[:target_line] + new_tail
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_content)
    print(f"Successfully replaced tail starting at line {target_line}")
else:
    print("Could not find target line to replace tail.")
