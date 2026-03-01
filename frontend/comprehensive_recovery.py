import sys
import re

path = "d:/Ani/Hackathons/AMD/ai-crop-smart-irrigation/frontend/src/App.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Restore the corrupted comments from previous global fixes
# Corrupted patterns might be:
# {_* ... *_}
# __ ...
# _* ... *_

# Let's use regex to find and restore
# Replace {_* ... *_} with /* ... */
content = re.sub(r'\{_\* (.*?) \*_\}', r'/* \1 */', content)

# Replace __ with //
content = content.replace('__', '//')

# Replace _* with /*
content = content.replace('_*', '/*')
# Replace *_ with */
content = content.replace('*_', '*/')

# 2. Re-apply the minimalist bit-accurate tail to ensure the end is clean
marker = 'localStorage.setItem'
idx = content.rfind(marker)
if idx != -1:
    head = content[:idx]
    tail = """localStorage.setItem('agroguard_lang', lang);
                                  }}
                                >
                                  {lang === 'en' ? 'English' : lang === 'hi' ? 'Hindi' : 'Kannada'}
                                </button>
                              ))}
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
    final_content = head + tail
else:
    final_content = content

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(final_content)

print("Comprehensive recovery and tail repair complete.")
