import sys

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# find the last "                  }" which usually ends the tab content block
target_line = -1
for i in range(len(lines) - 1, 0, -1):
    if "                  }" in lines[i] and i < 2075:
        target_line = i + 1
        break

if target_line == -1:
    target_line = 2050 

new_tail = [
    "                </div>\n",
    "              </div>\n",
    "            </main>\n",
    "          </div>\n",
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

new_content = lines[:target_line] + new_tail
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(new_content)

print(f"Replaced tail at line {target_line}")
