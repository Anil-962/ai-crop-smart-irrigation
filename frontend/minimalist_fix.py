import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Look for patterns that might be misinterpreted as a regex:
# e.g., / something / or comments that look like regexes.
# We also want to check for any unclosed strings or template literals near the end.

# Let's perform a very aggressive cleanup of the end of the file.
# We'll find the last stable '}' and rebuild the tail from scratch, 
# ensuring NO slashes or weird characters exist.

idx = content.rfind('localStorage.setItem')
if idx == -1:
    print("Marker not found")
    sys.exit(1)

head = content[:idx]

# This time, I'll use a very minimal, super-clean tail.
tail = """localStorage.setItem('agroguard_lang', lang);
                                  }
                                }
                              )
                            }
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                }
              </div>
            </div>
          </main>
        </div>
      </div>
{showToast && (
  <Toast
    message={toastMessage}
    onClose={() => setShowToast(false)}
  />
)}
    </div>
  );
}

export default App;
"""

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(head + tail)

print("Minimalist ASCII-only tail replacement complete.")
